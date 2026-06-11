"""
Management command: setup_empresa_inicial
Inicialización única del tenant principal (Claro Chile).

Crea la empresa "Claro Chile", asigna a todos los usuarios sin empresa,
y migra todos los registros históricos (Cliente, MetaVentas, Comision)
que quedaron con empresa=NULL antes de implementar multi-tenancy.

Es idempotente: puede ejecutarse múltiples veces sin efecto si ya está configurado.

Uso:
    python manage.py setup_empresa_inicial
    python manage.py setup_empresa_inicial --nombre="Claro Chile" --rut="96896660-0"
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = (
        "Inicializa el tenant principal (Claro Chile). "
        "Crea la empresa si no existe, asigna a todos los usuarios y migra datos históricos."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--nombre',
            default='Claro Chile',
            help='Nombre de la empresa principal (default: Claro Chile)',
        )
        parser.add_argument(
            '--rut',
            default='96896660-0',
            help='RUT de la empresa (default: 96896660-0)',
        )
        parser.add_argument(
            '--dominio',
            default='claro.cl',
            help='Dominio de la empresa (default: claro.cl)',
        )

    def handle(self, *args, **options):
        from core.models import Empresa, Cliente, MetaVentas, Comision, UserProfile

        nombre = options['nombre']
        rut = options['rut']
        dominio = options['dominio']

        self.stdout.write(self.style.HTTP_INFO(f"\n→ Configurando empresa principal: {nombre}"))

        # ── 1. Crear o recuperar empresa principal ──────────────────────
        empresa, creada = Empresa.objects.get_or_create(
            nombre=nombre,
            defaults={'rut': rut, 'dominio': dominio, 'activo': True}
        )
        if creada:
            self.stdout.write(self.style.SUCCESS(f"  ✓ Empresa «{nombre}» creada (id={empresa.id})"))
        else:
            self.stdout.write(self.style.SUCCESS(f"  ✓ Empresa «{nombre}» ya existe (id={empresa.id})"))

        # ── 2. Asignar empresa a UserProfiles sin empresa ───────────────
        sin_empresa = UserProfile.objects.filter(empresa__isnull=True)
        if sin_empresa.exists():
            count = sin_empresa.update(empresa=empresa)
            self.stdout.write(
                self.style.SUCCESS(f"  ✓ {count} perfiles de usuario actualizados → empresa={empresa.nombre}")
            )
        else:
            self.stdout.write(self.style.SUCCESS("  ✓ Todos los usuarios ya tienen empresa asignada"))

        # ── 3. Crear UserProfile para usuarios activos sin perfil ───────
        sin_perfil = User.objects.filter(is_active=True, profile__isnull=True)
        if sin_perfil.exists():
            for user in sin_perfil:
                UserProfile.objects.create(user=user, empresa=empresa)
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ Creado perfil para {user.email} con empresa={empresa.nombre}")
                )
        else:
            self.stdout.write(self.style.SUCCESS("  ✓ Todos los usuarios activos tienen UserProfile"))

        # ── 4. Migrar clientes históricos sin empresa ───────────────────
        clientes_null = Cliente.objects.filter(empresa__isnull=True)
        total_c = clientes_null.count()
        if total_c > 0:
            # Intenta recuperar empresa del usuario asignado/creado_por primero
            corregidos_por_usuario = 0
            ids_sin_resolver = []
            for cliente in clientes_null:
                empresa_recuperada = None
                for fuente in [cliente.usuario_asignado, cliente.creado_por]:
                    if fuente:
                        try:
                            empresa_recuperada = fuente.profile.empresa
                            if empresa_recuperada:
                                break
                        except Exception:
                            continue
                if empresa_recuperada:
                    cliente.empresa = empresa_recuperada
                    cliente.save(update_fields=['empresa'])
                    corregidos_por_usuario += 1
                else:
                    ids_sin_resolver.append(cliente.id)

            # Los restantes (sin usuario o usuario sin empresa) → asignar al tenant principal
            if ids_sin_resolver:
                corregidos_fallback = Cliente.objects.filter(
                    id__in=ids_sin_resolver
                ).update(empresa=empresa)
            else:
                corregidos_fallback = 0

            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✓ {total_c} clientes históricos migrados: "
                    f"{corregidos_por_usuario} por usuario, "
                    f"{corregidos_fallback} asignados a {empresa.nombre} (fallback)"
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS(f"  ✓ Todos los clientes ya tienen empresa"))

        # ── 5. Migrar MetaVentas sin empresa ────────────────────────────
        metas_null = MetaVentas.objects.filter(empresa__isnull=True)
        total_m = metas_null.count()
        if total_m > 0:
            corregidas = 0
            fallback_ids = []
            for meta in metas_null:
                if meta.usuario:
                    try:
                        emp = meta.usuario.profile.empresa
                        if emp:
                            meta.empresa = emp
                            meta.save(update_fields=['empresa'])
                            corregidas += 1
                            continue
                    except Exception:
                        pass
                fallback_ids.append(meta.id)
            if fallback_ids:
                MetaVentas.objects.filter(id__in=fallback_ids).update(empresa=empresa)
            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✓ {total_m} metas migradas: "
                    f"{corregidas} por usuario, {len(fallback_ids)} fallback a {empresa.nombre}"
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS("  ✓ Todas las metas ya tienen empresa"))

        # ── 6. Migrar Comisiones sin empresa ────────────────────────────
        comisiones_null = Comision.objects.filter(empresa__isnull=True)
        total_co = comisiones_null.count()
        if total_co > 0:
            corregidas = 0
            fallback_ids = []
            for comision in comisiones_null:
                if comision.usuario:
                    try:
                        emp = comision.usuario.profile.empresa
                        if emp:
                            comision.empresa = emp
                            comision.save(update_fields=['empresa'])
                            corregidas += 1
                            continue
                    except Exception:
                        pass
                fallback_ids.append(comision.id)
            if fallback_ids:
                Comision.objects.filter(id__in=fallback_ids).update(empresa=empresa)
            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✓ {total_co} comisiones migradas: "
                    f"{corregidas} por usuario, {len(fallback_ids)} fallback a {empresa.nombre}"
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS("  ✓ Todas las comisiones ya tienen empresa"))

        # ── Resumen ──────────────────────────────────────────────────────
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("  ✓ Setup inicial completado"))
        self.stdout.write(self.style.HTTP_INFO(
            f"  Empresa: {empresa.nombre} | id={empresa.id} | "
            f"usuarios={UserProfile.objects.filter(empresa=empresa).count()} | "
            f"clientes={Cliente.objects.filter(empresa=empresa).count()}"
        ))
        self.stdout.write("")
