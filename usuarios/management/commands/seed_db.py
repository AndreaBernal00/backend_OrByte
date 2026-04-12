from django.core.management.base import BaseCommand
from usuarios.models import Rol, Usuario
from pedidos.models import (
    Marca, Categoria, Producto,
    EstadoPedido, Pedido, PedidoProducto
)


class Command(BaseCommand):
    help = 'Carga datos de prueba en la base de datos'

    def handle(self, *args, **kwargs):

        # Roles
        roles = {}
        for nombre in ['admin', 'trabajador', 'cliente']:
            obj, _ = Rol.objects.get_or_create(nombre=nombre)
            roles[nombre] = obj
        self.stdout.write('✅ Roles')

        # Estados
        estados = {}
        for nombre in ['Registrado', 'En preparación', 'Enviado', 'Completado', 'Cancelado']:
            obj, _ = EstadoPedido.objects.get_or_create(nombre=nombre)
            estados[nombre] = obj
        self.stdout.write('✅ Estados')

        # Marcas
        marcas = {}
        for nombre in ['Logitech', 'Razer', 'HyperX']:
            obj, _ = Marca.objects.get_or_create(nombre=nombre)
            marcas[nombre] = obj
        self.stdout.write('✅ Marcas')

        # Categorías
        cats = {}
        for nombre in ['Teclados', 'Mouses', 'Diademas']:
            obj, _ = Categoria.objects.get_or_create(nombre=nombre)
            cats[nombre] = obj
        self.stdout.write('✅ Categorías')

        # Usuarios
        usuarios_data = [
            ('Santiago Admin',    'admin@orbyte.com',  'admin1234',   'admin',      True),
            ('Carlos Trabajador', 'carlos@orbyte.com', 'trab1234',    'trabajador', False),
            ('Ana Trabajadora',   'ana@orbyte.com',    'trab1234',    'trabajador', False),
            ('Luis Cliente',      'luis@gmail.com',    'cliente1234', 'cliente',    False),
            ('María Cliente',     'maria@gmail.com',   'cliente1234', 'cliente',    False),
            ('Pedro Cliente',     'pedro@gmail.com',   'cliente1234', 'cliente',    False),
            ('Sofía Cliente',     'sofia@gmail.com',   'cliente1234', 'cliente',    False),
            ('Andrés Cliente',    'andres@gmail.com',  'cliente1234', 'cliente',    False),
        ]
        usuarios = {}
        for nombre, email, password, rol_nombre, is_staff in usuarios_data:
            if not Usuario.objects.filter(email=email).exists():
                user = Usuario.objects.create_user(
                    email=email,
                    nombre=nombre,
                    password=password,
                    rol=roles[rol_nombre],
                    is_staff=is_staff,
                    is_superuser=is_staff,
                )
            else:
                user = Usuario.objects.get(email=email)
            usuarios[email] = user
        self.stdout.write('✅ Usuarios')

        # Productos
        productos_data = [
            ('Logitech MX Keys',       'Teclado inalámbrico premium',          320000, 15, 'Teclados', 'Logitech'),
            ('Logitech MX Master 3',   'Mouse ergonómico inalámbrico',         280000, 20, 'Mouses',   'Logitech'),
            ('Razer BlackWidow V4',    'Teclado mecánico con switches Razer',  450000, 10, 'Teclados', 'Razer'),
            ('Razer DeathAdder V3',    'Mouse gaming con sensor Focus Pro',    230000, 18, 'Mouses',   'Razer'),
            ('Razer Kraken V3',        'Diadema gaming con THX Spatial',       350000, 12, 'Diademas', 'Razer'),
            ('HyperX Alloy Origins',   'Teclado mecánico compacto TKL',        380000,  8, 'Teclados', 'HyperX'),
            ('HyperX Pulsefire Haste', 'Mouse ultraligero para gaming',        180000, 25, 'Mouses',   'HyperX'),
            ('HyperX Cloud Alpha',     'Diadema con drivers duales de cámara', 310000, 14, 'Diademas', 'HyperX'),
        ]
        productos = {}
        for nombre, desc, precio, stock, cat, marca in productos_data:
            obj, _ = Producto.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'descripcion': desc,
                    'precio_unitario': precio,
                    'stock_disponible': stock,
                    'categoria': cats[cat],
                    'marca': marcas[marca],
                }
            )
            productos[nombre] = obj
        self.stdout.write('✅ Productos')

        # Pedidos
        pedidos_data = [
            (
                'luis@gmail.com', 'carlos@orbyte.com', 'Completado',
                [('Logitech MX Keys', 1), ('Logitech MX Master 3', 1)]
            ),
            (
                'maria@gmail.com', 'ana@orbyte.com', 'Enviado',
                [('Razer BlackWidow V4', 1)]
            ),
            (
                'pedro@gmail.com', 'carlos@orbyte.com', 'En preparación',
                [('Razer DeathAdder V3', 1), ('HyperX Pulsefire Haste', 1)]
            ),
            (
                'sofia@gmail.com', 'ana@orbyte.com', 'Registrado',
                [('Razer Kraken V3', 1)]
            ),
            (
                'andres@gmail.com', 'carlos@orbyte.com', 'Cancelado',
                [('Logitech MX Keys', 1)]
            ),
        ]

        for cliente_email, vendedor_email, estado_nombre, items in pedidos_data:
            pedido, created = Pedido.objects.get_or_create(
                cliente=usuarios[cliente_email],
                estado=estados[estado_nombre],
                defaults={'registrado_por': usuarios[vendedor_email]}
            )
            if created:
                total = 0
                for nombre_producto, cantidad in items:
                    producto = productos[nombre_producto]
                    PedidoProducto.objects.create(
                        pedido=pedido,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario_snapshot=producto.precio_unitario,
                    )
                    total += producto.precio_unitario * cantidad
                pedido.total = total
                pedido.save()

        self.stdout.write('✅ Pedidos')
        self.stdout.write(self.style.SUCCESS('\n🎉 Base de datos cargada correctamente'))