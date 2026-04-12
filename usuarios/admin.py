from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Rol, Usuario

admin.site.register(Rol)

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display   = ('email', 'nombre', 'rol', 'activo', 'is_staff')
    search_fields  = ('email', 'nombre')
    ordering       = ('email',)
    # sobreescribir estos para eliminar referencias a campos que no existen
    list_filter       = ('is_staff', 'activo', 'rol')
    filter_horizontal = ()
    fieldsets = (
        (None,          {'fields': ('email', 'password')}),
        ('Información', {'fields': ('nombre', 'telefono', 'rol', 'activo')}),
        ('Permisos',    {'fields': ('is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'password1', 'password2', 'rol', 'is_staff'),
        }),
    )