"""
Management command: configurar_sindiapp
Inicialización del módulo sindical para piloto con cliente.

Crea los grupos de roles requeridos por SindiApp y muestra el procedimiento
completo para dar de alta a usuarios del sindicato.

Es idempotente: puede ejecutarse múltiples veces sin duplicar datos.

Uso:
    python manage.py configurar_sindiapp
    python manage.py configurar_sindiapp --empresa="Sindicato XYZ"
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()

GRUPOS_SINDICATO = [
    {
        'nombre': 'Administracion',
        'descripcion': 'Acceso completo a SindiApp: socios, beneficios, movimientos, consolidados, documentos y auditoría.',
    },
    {
        'nombre': 'Tesoreria',
        'descripcion': 'Importar movimientos, gestionar consolidados, subir y revisar documentos. No puede editar socios ni beneficios.',
    },
    {
        'nombre': 'Dirigente',
        'descripcion': 'Visualización de socios, movimientos, consolidados y alertas. Solo lectura.',
    },
]


class Command(BaseCommand):
    help = 'Configura grupos de roles SindiApp y muestra el procedimiento de alta de usuarios para piloto.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--empresa',
            default=None,
            help='Nombre de la empresa (tenant) para filtrar usuarios existentes',
        )

    def handle(self, *args, **options):
        empresa_nombre = options.get('empresa')

        self.stdout.write(self.style.HTTP_INFO('\n╔══════════════════════════════════════════════╗'))
        self.stdout.write(self.style.HTTP_INFO('║   Configuración SindiApp — Módulo Sindical   ║'))
        self.stdout.write(self.style.HTTP_INFO('╚══════════════════════════════════════════════╝\n'))

        # ── 1. Crear grupos ──────────────────────────────────────────────
        self.stdout.write(self.style.HTTP_INFO('→ Paso 1: Creando grupos de roles sindicales\n'))
        for g in GRUPOS_SINDICATO:
            grupo, creado = Group.objects.get_or_create(nombre=g['nombre']) if False else \
                            (Group.objects.get_or_create(name=g['nombre']))
            estado = self.style.SUCCESS('CREADO') if creado else self.style.WARNING('YA EXISTÍA')
            self.stdout.write(f"  [{estado}] Grupo «{g['nombre']}»")
            self.stdout.write(f"           {g['descripcion']}")
        self.stdout.write('')

        # ── 2. Verificar grupos existentes ──────────────────────────────
        total_grupos = Group.objects.filter(
            name__in=[g['nombre'] for g in GRUPOS_SINDICATO]
        ).count()
        if total_grupos == 3:
            self.stdout.write(self.style.SUCCESS('✓ Los 3 grupos de SindiApp están configurados correctamente.\n'))
        else:
            self.stdout.write(self.style.ERROR(f'✗ Solo se encontraron {total_grupos}/3 grupos. Verifica errores arriba.\n'))
            return

        # ── 3. Usuarios existentes con rol sindical ──────────────────────
        self.stdout.write(self.style.HTTP_INFO('→ Paso 2: Usuarios actuales con rol sindical\n'))
        nombres_grupos = [g['nombre'] for g in GRUPOS_SINDICATO]
        usuarios_sind = User.objects.filter(
            groups__name__in=nombres_grupos
        ).distinct().select_related('profile').prefetch_related('groups')

        if empresa_nombre:
            usuarios_sind = usuarios_sind.filter(profile__empresa__nombre__icontains=empresa_nombre)

        if usuarios_sind.exists():
            for u in usuarios_sind:
                grupos_usr = ', '.join(u.groups.filter(name__in=nombres_grupos).values_list('name', flat=True))
                try:
                    emp = u.profile.empresa.nombre if u.profile.empresa else '(sin empresa)'
                except Exception:
                    emp = '(sin perfil)'
                self.stdout.write(f"  • {u.email or u.username:<35} grupos=[{grupos_usr}]  empresa={emp}")
            self.stdout.write('')
        else:
            self.stdout.write('  (ningún usuario con rol sindical todavía)\n')

        # ── 4. Procedimiento de alta ─────────────────────────────────────
        self._imprimir_procedimiento_alta()

    def _imprimir_procedimiento_alta(self):
        sep = '─' * 60
        self.stdout.write(self.style.HTTP_INFO(f'\n→ Paso 3: Procedimiento de alta de usuarios para piloto\n'))
        self.stdout.write(sep)

        pasos = [
            ('A', 'Ingresar al panel de administración Django',
             'https://tu-dominio.railway.app/admin/\n'
             '   Credenciales: superusuario configurado en Railway.'),

            ('B', 'Crear el usuario del sindicato',
             'Ir a: Admin → Usuarios → Agregar usuario\n'
             '   • Username: (correo del usuario)\n'
             '   • Email: (mismo correo)\n'
             '   • Password: asignar contraseña segura temporaria\n'
             '   • Guardar'),

            ('C', 'Asignar empresa (tenant) al usuario',
             'Ir a: Admin → User profiles → Agregar user profile\n'
             '   • User: (el usuario recién creado)\n'
             '   • Empresa: (empresa cliente del sindicato)\n'
             '   • Role: (dejar en blanco, el rol lo da el Grupo)\n'
             '   • Guardar'),

            ('D', 'Asignar rol (grupo) al usuario',
             'Volver a: Admin → Usuarios → (el usuario)\n'
             '   Sección "Permisos" → "Grupos":\n'
             '   • Administracion → acceso total SindiApp\n'
             '   • Tesoreria      → importación + consolidados + documentos\n'
             '   • Dirigente      → solo visualización\n'
             '   • Guardar'),

            ('E', 'Verificar acceso en SindiApp',
             'El usuario ingresa en: https://tu-dominio.railway.app/sindiapp/login/\n'
             '   con su email y contraseña asignada.\n'
             '   Debería ver el dashboard y el menú según su rol.'),

            ('F', 'Configurar datos iniciales (Administrador del sindicato)',
             'Desde SindiApp → Beneficios:\n'
             '   Crear los beneficios del sindicato (Gas, Telefonía, Copeuch, etc.)\n'
             '   con su código y orden de exportación.\n\n'
             '   Desde SindiApp → Socios:\n'
             '   Los socios se crean automáticamente en la primera importación.\n'
             '   También pueden cargarse manualmente uno a uno.'),
        ]

        for letra, titulo, detalle in pasos:
            self.stdout.write(f'\n  [{letra}] {titulo}')
            for linea in detalle.split('\n'):
                self.stdout.write(f'      {linea}')

        self.stdout.write(f'\n{sep}')
        self.stdout.write(self.style.SUCCESS('\n✓ Configuración base de SindiApp completada.'))
        self.stdout.write('  Ejecuta este comando nuevamente después de crear usuarios para verificar el estado.\n')

        self.stdout.write(self.style.HTTP_INFO('\n→ Resumen de roles y permisos:\n'))
        tabla = [
            ('Funcionalidad',               'Administración', 'Tesorería', 'Dirigente'),
            ('Ver socios y beneficios',     '✓',             '—',         '✓'),
            ('Editar socios y beneficios',  '✓',             '—',         '—'),
            ('Ver movimientos',             '✓',             '✓',         '✓'),
            ('Importar movimientos (Excel)','✓',             '✓',         '—'),
            ('Ver consolidados',            '✓',             '✓',         '✓'),
            ('Generar / cerrar consolidado','✓',             '✓',         '—'),
            ('Exportar Excel',              '✓',             '✓',         '—'),
            ('Consulta por RUT',            '✓',             '✓',         '✓'),
            ('Ver alertas',                 '✓',             '✓',         '✓'),
            ('Resolver alertas',            '✓',             '✓',         '—'),
            ('Subir / revisar documentos',  '✓',             '✓',         '—'),
            ('Ver documentos',              '✓',             '✓',         '✓'),
            ('Ver auditoría',               '✓',             '✓',         '✓'),
        ]
        col_w = [30, 16, 11, 10]
        encabezado = tabla[0]
        self.stdout.write('  ' + ''.join(f'{encabezado[i]:<{col_w[i]}}' for i in range(4)))
        self.stdout.write('  ' + '─' * sum(col_w))
        for fila in tabla[1:]:
            self.stdout.write('  ' + ''.join(f'{fila[i]:<{col_w[i]}}' for i in range(4)))
        self.stdout.write('')
