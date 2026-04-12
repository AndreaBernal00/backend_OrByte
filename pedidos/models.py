from django.db import models
from django.conf import settings


class Marca(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'marcas'

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'categorias'
        verbose_name_plural = 'categorías'

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre           = models.CharField(max_length=100)
    descripcion      = models.TextField(null=True, blank=True)
    precio_unitario  = models.DecimalField(max_digits=10, decimal_places=2)
    stock_disponible = models.PositiveIntegerField(default=0)
    stock_reservado  = models.PositiveIntegerField(default=0)
    categoria        = models.ForeignKey(Categoria, on_delete=models.PROTECT, db_column='categoria_id')
    marca            = models.ForeignKey(Marca, on_delete=models.PROTECT, db_column='marca_id')
    activo           = models.BooleanField(default=True)
    creado_en        = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'productos'

    def __str__(self):
        return self.nombre


class EstadoPedido(models.Model):
    nombre = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = 'estados_pedido'
        verbose_name_plural = 'estados de pedido'

    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    cliente        = models.ForeignKey(
                         settings.AUTH_USER_MODEL,
                         on_delete=models.PROTECT,
                         related_name='pedidos_como_cliente',
                         db_column='cliente_id'
                     )
    registrado_por = models.ForeignKey(
                         settings.AUTH_USER_MODEL,
                         on_delete=models.PROTECT,
                         related_name='pedidos_registrados',
                         db_column='registrado_por_id'
                     )
    estado         = models.ForeignKey(EstadoPedido, on_delete=models.PROTECT, db_column='estado_id')
    total          = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    creado_en      = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pedidos'
        indexes = [
            models.Index(fields=['cliente', 'creado_en'],        name='idx_ped_cliente_fecha'),
            models.Index(fields=['estado', 'creado_en'],         name='idx_ped_estado_fecha'),
            models.Index(fields=['registrado_por', 'creado_en'], name='idx_ped_registrado_por_fecha'),
        ]

    def __str__(self):
        return f'Pedido #{self.id} — {self.cliente.nombre}'


class PedidoProducto(models.Model):
    pedido                   = models.ForeignKey(Pedido, on_delete=models.CASCADE, db_column='pedido_id')
    producto                 = models.ForeignKey(Producto, on_delete=models.PROTECT, db_column='producto_id')
    cantidad                 = models.PositiveIntegerField()
    precio_unitario_snapshot = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'pedido_productos'
        constraints = [
            models.UniqueConstraint(fields=['pedido', 'producto'], name='unique_pedido_producto')
        ]

    def __str__(self):
        return f'{self.cantidad}x {self.producto.nombre} en Pedido #{self.pedido.id}'