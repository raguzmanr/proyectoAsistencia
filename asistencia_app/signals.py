from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Solicitud, Cotizacion

@receiver(post_save, sender=Solicitud)
def crear_cotizacion_automatica(sender, instance, created, **kwargs):
    """
    Crea automáticamente una cotización cuando se crea una nueva solicitud.
    Usa la tarifa base del servicio como monto inicial.
    """
    if created:
        # Verificar si ya existe cotización (por seguridad)
        if not hasattr(instance, 'cotizacion'):
            Cotizacion.objects.create(
                solicitud=instance,
                monto=instance.servicio.tarifa_base
            )
            print(f"Cotización automática creada para Solicitud #{instance.id}")
