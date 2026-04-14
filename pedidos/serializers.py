from rest_framework import serializers
from .models import Pedido, PedidoProducto, Producto, EstadoPedido
from django.db import transaction

class PedidoProductoInputSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField()
    cantidad    = serializers.IntegerField(min_value=1)

    def validate_producto_id(self, value):
        try:
            producto = Producto.objects.get(id=value, activo=True)
        except Producto.DoesNotExist:
            raise serializers.ValidationError(f'El producto con id {value} no existe o no está activo.')
        return value


class RegistrarPedidoSerializer(serializers.Serializer):
    cliente_id = serializers.IntegerField()
    productos  = PedidoProductoInputSerializer(many=True)

    def validate_cliente_id(self, value):
        from usuarios.models import Usuario
        try:
            cliente = Usuario.objects.get(id=value, activo=True)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError('El cliente no existe o no está activo.')
        if not cliente.rol or cliente.rol.nombre != 'cliente':
            raise serializers.ValidationError('El usuario indicado no tiene rol de cliente.')
        return value

    def validate_productos(self, value):
        if len(value) == 0:
            raise serializers.ValidationError('El pedido debe tener al menos un producto.')
        # verificar ids duplicados
        ids = [p['producto_id'] for p in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError('No puede repetir el mismo producto en el pedido.')
        return value

    def validate(self, data):
        # validar stock de cada producto
        for item in data['productos']:
            producto = Producto.objects.get(id=item['producto_id'], activo=True)
            if producto.stock_disponible < item['cantidad']:
                raise serializers.ValidationError(
                    f'Stock insuficiente para "{producto.nombre}". '
                    f'Disponible: {producto.stock_disponible}, solicitado: {item["cantidad"]}.'
                )
        return data

    @transaction.atomic #para evitar errores de concurrencia y asegurar que el pedido se registre correctamente o no se registre nada en caso de error
    def create(self, validated_data):
        from usuarios.models import Usuario
        request      = self.context['request']
        cliente      = Usuario.objects.get(id=validated_data['cliente_id'])
        estado       = EstadoPedido.objects.get(nombre='Registrado')
        registrado_por = request.user

        pedido = Pedido.objects.create(
            cliente=cliente,
            registrado_por=registrado_por,
            estado=estado,
            total=0,
        )

        total = 0
        for item in validated_data['productos']:
            producto = Producto.objects.select_for_update().get(id=item['producto_id'])
            cantidad = item['cantidad']

            #evitar que se cree un pedido di no hay stock suficiente, aunque esto ya se valido antes
            #sirve para evitar problemas de concurrencia, por ejemplo si dos pedidos intentan comprar el mismo producto al mismo tiempo y solo hay stock para uno de ellos
            if producto.stock_disponible < cantidad:
                raise serializers.ValidationError(
                    f'Stock insuficiente para "{producto.nombre}". '
                    f'Disponible: {producto.stock_disponible}, solicitado: {cantidad}.'
                )

            PedidoProducto.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio_unitario_snapshot=producto.precio_unitario,
            )

            # descontar stock disponible y aumentar reservado
            producto.stock_disponible -= cantidad
            producto.stock_reservado  += cantidad
            producto.save()

            total += producto.precio_unitario * cantidad

        pedido.total = total
        pedido.save()

        return pedido


class PedidoProductoOutputSerializer(serializers.ModelSerializer):
    producto_nombre  = serializers.CharField(source='producto.nombre')
    producto_id      = serializers.IntegerField(source='producto.id')

    class Meta:
        model  = PedidoProducto
        fields = ['producto_id', 'producto_nombre', 'cantidad', 'precio_unitario_snapshot']


class PedidoOutputSerializer(serializers.ModelSerializer):
    cliente        = serializers.CharField(source='cliente.nombre')
    registrado_por = serializers.CharField(source='registrado_por.nombre')
    estado         = serializers.CharField(source='estado.nombre')
    productos      = PedidoProductoOutputSerializer(source='pedidoproducto_set', many=True)

    class Meta:
        model  = Pedido
        fields = ['id', 'cliente', 'registrado_por', 'estado', 'total', 'creado_en', 'productos']