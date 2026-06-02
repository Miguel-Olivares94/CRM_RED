#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Cliente, Oportunidad, Seguimiento
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from decimal import Decimal

User = get_user_model()

# Obtener usuarios
admin_user = User.objects.filter(username='admin').first()
if not admin_user:
    print("No se encontró usuario admin")
    exit()

# Obtener clientes
clientes = Cliente.objects.all()[:3]

if not clientes:
    print("No hay clientes en la BD")
    exit()

# Crear oportunidades
oportunidades_data = [
    {
        'cliente': clientes[0] if len(clientes) > 0 else None,
        'usuario': admin_user,
        'monto': Decimal('150000.00'),
        'moneda': 'CLP',
        'etapa': 'CALIFICADO',
        'probabilidad': 60,
        'productos': 'Portabilidad + M2M',
        'lineas': 5,
        'fecha_cierre_estimada': datetime.now().date() + timedelta(days=30),
        'proximo_contacto': datetime.now().date() + timedelta(days=7),
        'observaciones': 'Cliente interesado en portabilidad de líneas corporativas',
    },
    {
        'cliente': clientes[1] if len(clientes) > 1 else None,
        'usuario': admin_user,
        'monto': Decimal('300000.00'),
        'moneda': 'CLP',
        'etapa': 'PROPUESTA',
        'probabilidad': 75,
        'productos': 'Nuevo cliente M2M',
        'lineas': 10,
        'fecha_cierre_estimada': datetime.now().date() + timedelta(days=15),
        'proximo_contacto': datetime.now().date() + timedelta(days=3),
        'observaciones': 'Propuesta enviada esperando respuesta',
    },
    {
        'cliente': clientes[2] if len(clientes) > 2 else None,
        'usuario': admin_user,
        'monto': Decimal('75000.00'),
        'moneda': 'CLP',
        'etapa': 'CONTACTO',
        'probabilidad': 30,
        'productos': 'Consultoría',
        'lineas': 2,
        'fecha_cierre_estimada': datetime.now().date() + timedelta(days=60),
        'proximo_contacto': datetime.now().date() + timedelta(days=14),
        'observaciones': 'Contacto inicial, requiere mayor análisis',
    },
    {
        'cliente': clientes[0] if len(clientes) > 0 else None,
        'usuario': admin_user,
        'monto': Decimal('500000.00'),
        'moneda': 'CLP',
        'etapa': 'NEGOCIACION',
        'probabilidad': 85,
        'productos': 'Paquete corporativo completo',
        'lineas': 20,
        'fecha_cierre_estimada': datetime.now().date() + timedelta(days=10),
        'proximo_contacto': datetime.now().date() + timedelta(days=2),
        'observaciones': 'En negociación final, muy probable cierre',
    },
]

created_count = 0
for data in oportunidades_data:
    if data['cliente']:
        oportunidad, created = Oportunidad.objects.get_or_create(
            cliente=data['cliente'],
            monto=data['monto'],
            defaults=data
        )
        if created:
            created_count += 1
            print(f"✅ Creada oportunidad: {oportunidad.cliente.nombre_empresa} - ${oportunidad.monto}")
        else:
            print(f"⏭️  Ya existe: {oportunidad.cliente.nombre_empresa} - ${oportunidad.monto}")

print(f"\n✨ Total creadas: {created_count} oportunidades")
