from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta


@receiver(post_save, sender='core.Oportunidad')
def crear_seguimiento_inicial(sender, instance, created, **kwargs):
    """
    Al crear una Oportunidad, genera automáticamente un Seguimiento
    de tipo RECORDATORIO para el ejecutivo asignado, con vencimiento
    en 3 días (plazo razonable para el primer contacto).
    """
    if not created:
        return

    from core.models import Seguimiento

    fecha_vencimiento = (timezone.now() + timedelta(days=3)).date()

    Seguimiento.objects.create(
        oportunidad=instance,
        tipo='RECORDATORIO',
        prioridad='ALTA',
        estado='PENDIENTE',
        descripcion=(
            f"Primer contacto con {instance.cliente.nombre_empresa}. "
            f"Oportunidad levantada el {instance.fecha_creacion.strftime('%d/%m/%Y')}. "
            f"Etapa inicial: {instance.get_etapa_display()}."
        ),
        asignado_a=instance.usuario,
        fecha_vencimiento=fecha_vencimiento,
        creado_por=instance.creado_por or instance.usuario,
    )
