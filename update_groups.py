#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User, Group
from core.models import UserProfile

# Crear grupos si no existen
print("=== CREAR GRUPOS ===")
grupos_necesarios = ['Admin', 'Manager', 'Ejecutivo', 'Vendedor']
for nombre in grupos_necesarios:
    group, created = Group.objects.get_or_create(name=nombre)
    if created:
        print(f"Creado: {nombre}")
    else:
        print(f"Ya existe: {nombre}")

# Obtener Rogers
roy = User.objects.get(username='Roy')
print(f"\n=== ACTUALIZANDO ROGERS ===")
print(f"Usuario: {roy.username}")

# Remover del grupo Ejecutivo
if roy.groups.filter(name='Ejecutivo').exists():
    roy.groups.remove(Group.objects.get(name='Ejecutivo'))
    print("Removido de: Ejecutivo")

# Agregar al grupo Manager
manager_group = Group.objects.get(name='Manager')
roy.groups.add(manager_group)
print("Agregado a: Manager")

# Actualizar subordinados
print(f"\n=== ACTUALIZANDO SUBORDINADOS ===")
subordinados = roy.subordinados.all()
print(f"Total subordinados: {subordinados.count()}")

for sub_profile in subordinados:
    user = sub_profile.user
    # Remover de Ejecutivo
    if user.groups.filter(name='Ejecutivo').exists():
        user.groups.remove(Group.objects.get(name='Ejecutivo'))
    # Agregar a Vendedor
    vendedor_group = Group.objects.get(name='Vendedor')
    user.groups.add(vendedor_group)
    grupos = list(user.groups.values_list('name', flat=True))
    print(f"{user.username}: {grupos}")

print("\n=== VERIFICACION FINAL ===")
print("Admin group:", list(Group.objects.get(name='Admin').user_set.values_list('username', flat=True)))
print("Manager group:", list(Group.objects.get(name='Manager').user_set.values_list('username', flat=True)))
print("Vendedor group:", list(Group.objects.get(name='Vendedor').user_set.values_list('username', flat=True)))
print("\nDone!")
