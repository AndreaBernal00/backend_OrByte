from django.urls import path
from .views import RegistrarPedidoView, InformePedidosView, EditarPedidoView

urlpatterns = [
    path('pedidos/registrar/',        RegistrarPedidoView.as_view(), name='registrar-pedido'),
    path('pedidos/informe/',          InformePedidosView.as_view(),  name='informe-pedidos'),
    path('pedidos/<int:pedido_id>/editar/', EditarPedidoView.as_view(),  name='editar-pedido'),
]