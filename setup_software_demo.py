"""
Script de prueba Fase 2: crea empresa Software Demo con 5 campos personalizados.
Ejecutar con: python setup_software_demo.py
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Empresa, CampoPersonalizado, UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 55)
print("  SETUP Empresa Software Demo — Fase 2")
print("=" * 55)

# ── 1. Crear empresa ──────────────────────────────────────
empresa, creada = Empresa.objects.get_or_create(
    nombre='Software Demo',
    defaults={'rut': '99.999.999-9', 'dominio': 'softdemo.cl', 'tipo': 'CLIENTE'},
)
print(f"\n[1] Empresa: {empresa}  ({'CREADA' if creada else 'ya existía'})")

# ── 2. Crear usuario admin para Software Demo ─────────────
user, u_creado = User.objects.get_or_create(
    username='admin@softdemo.cl',
    defaults={'email': 'admin@softdemo.cl', 'is_staff': False, 'is_superuser': False},
)
if u_creado:
    user.set_password('SoftDemo2026!')
    user.save()

from django.contrib.auth.models import Group
grupo_admin, _ = Group.objects.get_or_create(name='Admin')
user.groups.add(grupo_admin)

profile, _ = UserProfile.objects.get_or_create(
    user=user,
    defaults={'empresa': empresa, 'role': 'ADMIN'},
)
if not profile.empresa:
    profile.empresa = empresa
    profile.save()

print(f"[2] Usuario: {user.email}  ({'CREADO' if u_creado else 'ya existía'})")

# ── 3. Crear campos personalizados ────────────────────────
CAMPOS = [
    {
        'entidad': 'CLIENTE', 'nombre': 'Tipo de sistema requerido',
        'clave': 'tipo_sistema', 'tipo': 'SELECT',
        'opciones': ['ERP', 'CRM', 'BI / Reportes', 'Desarrollo a medida', 'SaaS genérico'],
        'obligatorio': False, 'orden': 1,
    },
    {
        'entidad': 'CLIENTE', 'nombre': 'Presupuesto estimado (CLP)',
        'clave': 'presupuesto_clp', 'tipo': 'NUMBER',
        'obligatorio': False, 'orden': 2,
    },
    {
        'entidad': 'CLIENTE', 'nombre': 'Fecha de demo',
        'clave': 'fecha_demo', 'tipo': 'DATE',
        'obligatorio': False, 'orden': 3,
    },
    {
        'entidad': 'CLIENTE', 'nombre': 'Necesidades del cliente',
        'clave': 'necesidades', 'tipo': 'TEXT',
        'obligatorio': False, 'orden': 4,
    },
    {
        'entidad': 'CLIENTE', 'nombre': '¿Tiene contrato vigente?',
        'clave': 'contrato_vigente', 'tipo': 'BOOL',
        'obligatorio': False, 'orden': 5,
    },
]

print(f"\n[3] Campos personalizados:")
for c in CAMPOS:
    obj, creado_c = CampoPersonalizado.objects.update_or_create(
        empresa=empresa,
        entidad=c['entidad'],
        clave=c['clave'],
        defaults={
            'nombre': c['nombre'],
            'tipo': c['tipo'],
            'opciones': c.get('opciones'),
            'obligatorio': c['obligatorio'],
            'orden': c['orden'],
            'activo': True,
        }
    )
    print(f"    {'CREADO' if creado_c else 'OK  '} | {obj.entidad} | {obj.nombre} ({obj.tipo})")

# ── 4. Verificar ──────────────────────────────────────────
total = CampoPersonalizado.objects.filter(empresa=empresa).count()
print(f"\n[4] Total campos para Software Demo: {total}")
print(f"    Login:    admin@softdemo.cl / SoftDemo2026!")
print(f"    URL test: /clientes/nuevo/")
print("\n" + "=" * 55)
print("  SETUP COMPLETADO")
print("=" * 55)
