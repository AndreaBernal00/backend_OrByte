from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import RegistrarPedidoSerializer, PedidoOutputSerializer
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