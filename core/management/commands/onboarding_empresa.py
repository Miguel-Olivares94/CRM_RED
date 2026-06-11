"""
Management command: onboarding_empresa
Crea una nueva empresa cliente + su usuario administrador de forma segura.

Es idempotente: puede ejecutarse múltiples veces. Si la empresa o el usuario
ya existen, los recupera y actualiza solo lo necesario.

Uso:
    python manage.py onboarding_empresa \\
        --nombre="Entel Chile" \\
        --rut="76354771-9" \\
        --dominio="entel.cl" \\
        --admin-email="admin@entel.cl" \\
        --admin-password="Entel2026!"

Garantías de seguridad:
    - El admin de empresa NO recibe is_staff=True → sin acceso a Django Admin.
    - El admin de empresa NO recibe is_superuser=True.
    - La empresa creada siempre es tipo=CLIENTE (nunca PLATAFORMA).
    - No modifica empresas existentes tipo=PLATAFORMA.
    - No modifica datos de otras empresas.
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea una nueva empresa cliente y su usuario administrador.'

    def add_arguments(self, parser):
        parser.add_argument('--nombre', required=True, help='Nombre de la empresa cliente')
        parser.add_argument('--rut', default=None, help='RUT de la empresa (opcional)')
        parser.add_argument('--dominio', default=None, help='Dominio de email, ej: empresa.cl (opcional)')
        parser.add_argument('--admin-email', required=True, dest='admin_email',
                            help='Email del usuario administrador de la empresa')
        parser.add_argument('--admin-password', required=True, dest='admin_password',
                            help='Contraseña del usuario administrador')
        parser.add_argument('--admin-nombre', default='', dest='admin_nombre',
                            help='Nombre completo del admin (opcional)')

    @transaction.atomic
    def handle(self, *args, **options):
        from core.models import Empresa, UserProfile

        nombre = options['nombre'].strip()
        rut = options['rut']
        dominio = options['dominio']
        admin_email = options['admin_email'].strip().lower()
        admin_password = options['admin_password']
        admin_nombre = options['admin_nombre'].strip()

        self.stdout.write(self.style.HTTP_INFO(f"\n{'='*60}"))
        self.stdout.write(self.style.HTTP_INFO(f"  ONBOARDING: {nombre}"))
        self.stdout.write(self.style.HTTP_INFO(f"{'='*60}"))

        # ── Guardia: no crear una segunda PLATAFORMA ──────────────────
        if Empresa.objects.filter(tipo='PLATAFORMA', nombre=nombre).exists():
            raise CommandError(
                f"«{nombre}» es la empresa PLATAFORMA. No se puede recraar con este comando."
            )

        # ── 1. Crear o recuperar empresa CLIENTE ──────────────────────
        defaults = {'tipo': 'CLIENTE', 'activo': True}
        if rut:
            defaults['rut'] = rut
        if dominio:
            defaults['dominio'] = dominio

        empresa, empresa_creada = Empresa.objects.get_or_create(
            nombre=nombre,
            defaults=defaults,
        )

        if empresa.tipo == 'PLATAFORMA':
            raise CommandError(
                f"«{nombre}» ya existe como empresa PLATAFORMA. "
                "No se puede convertir con este comando."
            )

        if empresa_creada:
            self.stdout.write(self.style.SUCCESS(
                f"  ✓ Empresa «{nombre}» creada (id={empresa.id}, tipo=CLIENTE)"
            ))
        else:
            self.stdout.write(
                f"  · Empresa «{nombre}» ya existía (id={empresa.id}, tipo={empresa.tipo})"
            )
            # Actualizar RUT/dominio si se pasaron y estaban vacíos
            actualizar = False
            if rut and not empresa.rut:
                empresa.rut = rut
                actualizar = True
            if dominio and not empresa.dominio:
                empresa.dominio = dominio
                actualizar = True
            if actualizar:
                empresa.save()
                self.stdout.write(f"  · Empresa actualizada con nuevos datos")

        # ── 2. Crear o recuperar usuario admin de empresa ─────────────
        user, user_creado = User.objects.get_or_create(
            email=admin_email,
            defaults={
                'username': admin_email,
                'is_active': True,
                'is_staff': False,       # Sin acceso a Django Admin
                'is_superuser': False,   # Sin superpoderes
            }
        )

        if user_creado:
            user.set_password(admin_password)
            if admin_nombre:
                partes = admin_nombre.split(' ', 1)
                user.first_name = partes[0]
                user.last_name = partes[1] if len(partes) > 1 else ''
            user.save()
            self.stdout.write(self.style.SUCCESS(
                f"  ✓ Usuario «{admin_email}» creado "
                f"(is_staff=False, is_superuser=False)"
            ))
        else:
            self.stdout.write(
                f"  · Usuario «{admin_email}» ya existía (id={user.id})"
            )
            # Asegurar que no tiene acceso a Django Admin
            if user.is_staff or user.is_superuser:
                self.stdout.write(self.style.WARNING(
                    f"  ⚠ El usuario ya tenía is_staff={user.is_staff} / "
                    f"is_superuser={user.is_superuser} — se respetan los permisos existentes"
                ))

        # ── 3. Crear o actualizar UserProfile ─────────────────────────
        profile, profile_creado = UserProfile.objects.get_or_create(
            user=user,
            defaults={'empresa': empresa, 'role': 'ADMIN'},
        )

        if profile_creado:
            self.stdout.write(self.style.SUCCESS(
                f"  ✓ UserProfile creado: role=ADMIN, empresa={empresa.nombre}"
            ))
        else:
            cambios = []
            if profile.empresa != empresa:
                profile.empresa = empresa
                cambios.append(f"empresa→{empresa.nombre}")
            if profile.role != 'ADMIN':
                profile.role = 'ADMIN'
                cambios.append("role→ADMIN")
            if cambios:
                profile.save()
                self.stdout.write(self.style.WARNING(
                    f"  · UserProfile actualizado: {', '.join(cambios)}"
                ))
            else:
                self.stdout.write(f"  · UserProfile ya correcto")

        # ── 4. Asignar grupo Admin (Django Groups) ─────────────────────
        grupo_admin, _ = Group.objects.get_or_create(name='Admin')
        if not user.groups.filter(name='Admin').exists():
            user.groups.add(grupo_admin)
            self.stdout.write(self.style.SUCCESS(
                f"  ✓ Usuario agregado al grupo Django «Admin»"
            ))
        else:
            self.stdout.write(f"  · Ya pertenece al grupo «Admin»")

        # ── 5. Verificaciones de seguridad finales ─────────────────────
        self.stdout.write("")
        self.stdout.write(self.style.HTTP_INFO("  Verificaciones de seguridad:"))

        assert not user.is_staff,      "ERROR: el usuario tiene is_staff=True"
        assert not user.is_superuser,  "ERROR: el usuario tiene is_superuser=True"
        assert profile.empresa == empresa, "ERROR: empresa del perfil no coincide"
        assert empresa.tipo == 'CLIENTE',  "ERROR: la empresa no es tipo CLIENTE"

        self.stdout.write(self.style.SUCCESS("  ✓ is_staff=False"))
        self.stdout.write(self.style.SUCCESS("  ✓ is_superuser=False"))
        self.stdout.write(self.style.SUCCESS("  ✓ Sin acceso a Django Admin"))
        self.stdout.write(self.style.SUCCESS(f"  ✓ empresa.tipo = CLIENTE"))
        self.stdout.write(self.style.SUCCESS(f"  ✓ Empresa ≠ PLATAFORMA"))

        # ── Resumen ────────────────────────────────────────────────────
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"{'='*60}"))
        self.stdout.write(self.style.SUCCESS(f"  ONBOARDING COMPLETADO"))
        self.stdout.write(self.style.SUCCESS(f"{'='*60}"))
        self.stdout.write(f"  Empresa : {empresa.nombre} (id={empresa.id})")
        self.stdout.write(f"  Tipo    : {empresa.tipo}")
        self.stdout.write(f"  Admin   : {admin_email}")
        self.stdout.write(f"  Grupos  : Admin")
        self.stdout.write(f"  Staff   : No")
        self.stdout.write(f"  Clientes: {empresa.clientes.count()}")
        self.stdout.write("")
        self.stdout.write("  Login en producción:")
        self.stdout.write(f"    Email    : {admin_email}")
        self.stdout.write(f"    Password : (la que indicaste)")
        self.stdout.write("")
