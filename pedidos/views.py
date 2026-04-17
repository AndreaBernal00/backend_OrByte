from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum

from django.db import transaction

from .models import Pedido, PedidoProducto, Producto, EstadoPedido
from .serializers import RegistrarPedidoSerializer, PedidoOutputSerializer, InformePedidoSerializer, EditarPedidoSerializer
from .permissions import EsAdminOTrabajador


class RegistrarPedidoView(APIView):
    permission_classes = [EsAdminOTrabajador]

    def post(self, request):
        serializer = RegistrarPedidoSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            pedido = serializer.save()
            output = PedidoOutputSerializer(pedido)
            return Response(output.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InformePedidosView(APIView):
    permission_classes = [EsAdminOTrabajador]

    def get(self, request):
        qs = Pedido.objects.select_related(
            'cliente', 'registrado_por', 'estado'
        ).prefetch_related(
            'pedidoproducto_set__producto'
        ).order_by('-creado_en')

        # --- filtros opcionales ---
        fecha_ini = request.query_params.get('fecha_ini')
        fecha_fin = request.query_params.get('fecha_fin')
        estado_id = request.query_params.get('estado_id')
        cliente_id = request.query_params.get('cliente_id')

        errores = {}

        if fecha_ini:
            try:
                fecha_ini_dt = datetime.strptime(fecha_ini, '%Y-%m-%d').date()
                qs = qs.filter(creado_en__date__gte=fecha_ini_dt)
            except ValueError:
                errores['fecha_ini'] = 'Formato inválido. Use YYYY-MM-DD.'

        if fecha_fin:
            try:
                fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                qs = qs.filter(creado_en__date__lte=fecha_fin_dt)
            except ValueError:
                errores['fecha_fin'] = 'Formato inválido. Use YYYY-MM-DD.'

        if errores:
            return Response(errores, status=status.HTTP_400_BAD_REQUEST)

        if estado_id:
            qs = qs.filter(estado_id=estado_id)

        if cliente_id:
            qs = qs.filter(cliente_id=cliente_id)

        # --- resumen agregado ---
        total_pedidos = qs.count()
        monto_total   = qs.aggregate(total=Sum('total'))['total'] or 0

        serializer = InformePedidoSerializer(qs, many=True)

        return Response({
            'resumen': {
                'total_pedidos': total_pedidos,
                'monto_total':   monto_total,
            },
            'pedidos': serializer.data,
        })


class EditarPedidoView(APIView):
    permission_classes = [EsAdminOTrabajador]

    def patch(self, request, pedido_id):
        try:
            pedido = Pedido.objects.select_related('estado').get(id=pedido_id)
        except Pedido.DoesNotExist:
            return Response({'error': 'Pedido no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = EditarPedidoSerializer(data=request.data, context={'pedido': pedido})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        nuevo_estado = EstadoPedido.objects.get(id=serializer.validated_data['estado_id'])

        with transaction.atomic():
            if nuevo_estado.nombre == 'Cancelado':
                for item in PedidoProducto.objects.filter(pedido=pedido):
                    producto = Producto.objects.select_for_update().get(id=item.producto_id)
                    producto.stock_disponible += item.cantidad
                    producto.stock_reservado  -= item.cantidad
                    producto.save()

            elif nuevo_estado.nombre == 'Completado':
                for item in PedidoProducto.objects.filter(pedido=pedido):
                    producto = Producto.objects.select_for_update().get(id=item.producto_id)
                    producto.stock_reservado -= item.cantidad
                    producto.save()

            pedido.estado = nuevo_estado
            pedido.save()

        output = PedidoOutputSerializer(pedido)
        return Response(output.data, status=status.HTTP_200_OK)