from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# -------------------------------------------
# MODELO DE USUARIO PERSONALIZADO
# -------------------------------------------
class User(AbstractUser):
    ROLE_CHOICES = (
        ('cliente', 'Cliente'),
        ('empresa', 'Empresa'),
        ('admin', 'Administrador'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='cliente')

    def __str__(self):
        return f"{self.username} ({self.role})"


# -------------------------------------------
# 1. Catálogo de Servicios
# -------------------------------------------
class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    tarifa_base = models.DecimalField(max_digits=10, decimal_places=2)
    SEGMENTOS = (
        ('cartech', 'Cartech'),
        ('foodtech', 'Foodtech'),
        ('agetech', 'Agetech'),
    )
    segmento = models.CharField(max_length=20, choices=SEGMENTOS, default='cartech')
    form_schema = models.JSONField(default=list, blank=True, help_text="Esquema del formulario dinámico (lista de campos)")

    def __str__(self):
        return self.nombre


# -------------------------------------------
# 2. Solicitudes realizadas por usuarios
# -------------------------------------------
class Solicitud(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En proceso'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="solicitudes"
    )

    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    descripcion = models.TextField()
    ubicacion = models.TextField(default="Sin especificar", help_text="Dirección o ubicación donde se necesita el servicio")
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    datos_formulario = models.JSONField(default=dict, blank=True, help_text="Datos dinámicos del formulario según el servicio")

    def __str__(self):
        return f"Solicitud #{self.id} de {self.usuario.username}"


class SolicitudHistorial(models.Model):
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='historial')
    estado_anterior = models.CharField(max_length=20, choices=Solicitud.ESTADOS, null=True, blank=True)
    estado_nuevo = models.CharField(max_length=20, choices=Solicitud.ESTADOS)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    usuario_responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    comentario = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Cambio {self.estado_anterior} -> {self.estado_nuevo} ({self.solicitud.id})"


# -------------------------------------------
# 3. Cotización automática
# -------------------------------------------
class Cotizacion(models.Model):
    solicitud = models.OneToOneField(Solicitud, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_generada = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cotización {self.id} - Solicitud {self.solicitud.id}"
