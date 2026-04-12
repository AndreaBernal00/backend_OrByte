from django.contrib import admin
from .models import Marca, Categoria, Producto, EstadoPedido, Pedido, PedidoProducto

admin.site.register(Marca)
admin.site.register(Categoria)
admin.site.register(Producto)
admin.site.register(EstadoPedido)
admin.site.register(Pedido)
admin.site.register(PedidoProducto)