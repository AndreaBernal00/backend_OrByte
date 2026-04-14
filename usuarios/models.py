from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class Rol(models.Model):
    nombre = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = 'roles'
        verbose_name_plural = 'roles'

    def __str__(self):
        return self.nombre


class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombre, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, nombre=nombre, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nombre, password=None, **extra_fields):
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True')
        return self.create_user(email, nombre, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    nombre    = models.CharField(max_length=100)
    email     = models.EmailField(max_length=150, unique=True)
    telefono  = models.CharField(max_length=20, null=True, blank=True)
    rol       = models.ForeignKey(
                    Rol,
                    on_delete=models.PROTECT,
                    #null=True, blank=True,
                    db_column='rol_id'
                )
    activo    = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    is_staff     = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['nombre']

    objects = UsuarioManager()

    class Meta:
        db_table = 'usuarios'

    def __str__(self):
        return f'{self.nombre} ({self.email})'

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser