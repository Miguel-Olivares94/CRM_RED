def user_roles(request):
    """Agrega flags de rol al contexto de todos los templates."""
    if not request.user.is_authenticated:
        return {}
    u = request.user
    grupos = set(u.groups.values_list('name', flat=True))
    return {
        'puede_asignar_equipo': u.is_superuser or bool(grupos & {'Admin', 'Manager'}),
    }
