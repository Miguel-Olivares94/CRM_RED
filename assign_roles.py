#!/usr/bin/env python
"""
Script para asignar roles a usuarios
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User, Group

# Obtener o crear grupos
admin_group, _ = Group.objects.get_or_create(name='Admin')
ejecutivo_group, _ = Group.objects.get_or_create(name='Ejecutivo')

print('=== ASIGNANDO ROLES ===')

# Usuario 1: admin@admin.cl → Admin
try:
    user1 = User.objects.get(id=1)
    user1.groups.add(admin_group)
    print(f'✓ {user1.email} → Admin')
except User.DoesNotExist:
    print('✗ Usuario 1 no existe')

# Usuario 2: admin@claro.cl → Admin
try:
    user2 = User.objects.get(id=2)
    user2.groups.add(admin_group)
    print(f'✓ {user2.email} → Admin')
except User.DoesNotExist:
    print('✗ Usuario 2 no existe')

# Usuario 4: vendedor2@claro.cl → Ejecutivo
try:
    user4 = User.objects.get(id=4)
    user4.groups.add(ejecutivo_group)
    print(f'✓ {user4.email} → Ejecutivo')
except User.DoesNotExist:
    print('✗ Usuario 4 no existe')

print('\n=== USUARIOS CON ROLES ASIGNADOS ===')
usuarios = User.objects.all()
for u in usuarios:
    grupos = list(u.groups.values_list('name', flat=True))
    rol_display = ', '.join(grupos) if grupos else 'Sin rol'
    print(f'{u.email}: {rol_display}')
