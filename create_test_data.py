#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Cliente, Contacto, Oportunidad, Comision

Usuario = get_user_model()

# Crear usuarios  
try:
    user1 = Usuario.objects.get(email='vendedor1@claro.cl')
except Usuario.DoesNotExist:
    user1 = Usuario.objects.create_user(
        email='vendedor1@claro.cl',
        username='vendedor1@claro.cl',
        first_name='Juan',
        last_name='Vendedor'
    )

try:
    user2 = Usuario.objects.get(email='vendedor2@claro.cl')
except Usuario.DoesNotExist:
    user2 = Usuario.objects.create_user(
        email='vendedor2@claro.cl',
        username='vendedor2@claro.cl',
        first_name='María',
        last_name='Vendedor'
    )

# Crear clientes
for i in range(1, 6):
    cliente, creado = Cliente.objects.get_or_create(
        rut=f'12345{i}',
        defaults={
            'nombre_empresa': f'Empresa {i}',
            'sector': 'Telecomunicaciones',
            'estado': 'ACTIVO',
            'usuario_asignado': user1 if i % 2 == 0 else user2,
        }
    )
    status = 'Creado' if creado else 'Existía'
    print(f"[{status}] Cliente: {cliente.nombre_empresa}")

# Crear oportunidades
for cliente in Cliente.objects.all()[:3]:
    for j in range(1, 3):
        Oportunidad.objects.get_or_create(
            cliente=cliente,
            nombre=f'{cliente.nombre_empresa} - Oportunidad {j}',
            defaults={
                'monto': 10000 * j,
                'etapa': ['LEAD', 'CONTACTO', 'PROPUESTA'][j % 3],
                'usuario': cliente.usuario_asignado,
            }
        )

# Crear comisiones
Comision.objects.get_or_create(
    usuario=user1,
    periodo='2024-01',
    defaults={
        'lineas_vendidas_portabilidad': 10,
        'lineas_vendidas_nueva': 5,
        'comision_calculada': 50000,
        'estado': 'CALCULADA',
    }
)

print(f"\n✅ Datos de prueba creados:")
print(f"   Clientes: {Cliente.objects.count()}")
print(f"   Oportunidades: {Oportunidad.objects.count()}")
print(f"   Comisiones: {Comision.objects.count()}")
