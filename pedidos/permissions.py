from rest_framework.permissions import BasePermission


class EsAdminOTrabajador(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if not request.user.rol:
            return False

        return request.user.rol.nombre in ['admin', 'trabajador']