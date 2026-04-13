from django.urls import path
from .views import RegistrarPedidoView

urlpatterns = [
    path('pedidos/registrar/', RegistrarPedidoView.as_view(), name='registrar-pedido'),
]