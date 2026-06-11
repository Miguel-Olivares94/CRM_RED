from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta


# ─── Capa 2: señal de seguridad anti-fuga de datos ───────────────────────────
# Si Cliente, MetaVentas o Comision llegan a guardarse con empresa=NULL
# y tienen un creado_por/usuario con empresa asignada, la señal la recupera.

def _empresa_desde_usuario(user):
    """Retorna la empresa del perfil del usuario o None."""
    if user is None:
        return None
    try:
        return user.profile.empresa
    except Exception:
        return None


@receiver(pre_save, sender='core.Cliente')
def asegurar_empresa_cliente(sender, instance, **kwargs):
    """Red de seguridad: asigna empresa desde creado_por si aún es NULL."""
    if instance.empresa_id is None:
        empresa = _empresa_desde_usuario(instance.creado_por) or \
                  _empresa_desde_usuario(instance.usuario_asignado)
        if empresa:
            instance.empresa = empresa


@receiver(pre_save, sender='core.MetaVentas')
def asegurar_empresa_meta(sender, instance, **kwargs):
    """Red de seguridad: asigna empresa desde el usuario si aún es NULL."""
    if instance.empresa_id is None:
        empresa = _empresa_desde_usuario(instance.usuario)
        if empresa:
            instance.empresa = empresa


@receiver(pre_save, sender='core.Comision')
def asegurar_empresa_comision(sender, instance, **kwargs):
    """Red de seguridad: asigna empresa desde el usuario si aún es NULL."""
    if instance.empresa_id is None:
        empresa = _empresa_desde_usuario(instance.usuario)
        if empresa:
            instance.empresa = empresa


# ─── Señal de negocio: seguimiento al crear Oportunidad ──────────────────────

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
