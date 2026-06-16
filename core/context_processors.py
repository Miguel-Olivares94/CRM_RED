from django.conf import settings


def user_roles(request):
    """Agrega flags de rol al contexto de todos los templates."""
    ctx = {
        'SINDIAPP_DOCUMENTOS_HABILITADO': getattr(settings, 'SINDIAPP_DOCUMENTOS_HABILITADO', True),
    }
    if not request.user.is_authenticated:
        return ctx
    u = request.user
    grupos = set(u.groups.values_list('name', flat=True))
    ctx['puede_asignar_equipo'] = u.is_superuser or bool(grupos & {'Admin', 'Manager'})
    return ctx
