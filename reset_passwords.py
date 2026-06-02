#!/usr/bin/env python
"""
Script para resetear contraseñas de usuarios
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

# Definir contraseñas por usuario
users_passwords = {
    'admin@admin.cl': 'Admin123!',
    'admin@claro.cl': 'Admin123!',
    'vendedor1@claro.cl': 'Vendedor123!',
    'vendedor2@claro.cl': 'Vendedor123!',
}

print('=== RESETEANDO CONTRASEÑAS ===\n')

for email, password in users_passwords.items():
    try:
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        print(f'✓ {email}')
        print(f'  Contraseña: {password}\n')
    except User.DoesNotExist:
        print(f'✗ {email} no existe\n')

print('=== CREDENCIALES PARA LOGIN ===\n')
print('Admin:')
print('  Email: admin@admin.cl')
print('  Contraseña: Admin123!\n')
print('Ejecutivo/Vendedor:')
print('  Email: vendedor1@claro.cl')
print('  Contraseña: Vendedor123!')
