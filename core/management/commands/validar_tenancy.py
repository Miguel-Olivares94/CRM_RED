"""
Management command: validar_tenancy
Diagnóstico completo del estado del multi-tenancy en producción.
Uso: python manage.py validar_tenancy
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class Command(BaseCommand):
    help = "Diagnóstico completo de multi-tenancy: migraciones, empresa asignada, datos NULL, aislamiento."

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Intentar corrección automática de registros con empresa=NULL cuando sea posible.',
        )

    def handle(self, *args, **options):
        from core.models import Empresa, Cliente, MetaVentas, Comision, UserProfile

        fix = options.get('fix', False)
        ok = True

        self.stdout.write(self.style.HTTP_INFO("\n" + "="*60))
        self.stdout.write(self.style.HTTP_INFO("  DIAGNÓSTICO MULTI-TENANCY — CRM CLARO"))
        self.stdout.write(self.style.HTTP_INFO("="*60))

        # ── 1. Migración 0010 ──────────────────────────────────────────
        self.stdout.write("\n[1] Verificando migración 0010...")
        try:
            from django.db.migrations.recorder import MigrationRecorder
            aplicadas = MigrationRecorder.Migration.objects.filter(
                app='core', name='0010_add_empresa_to_metaventas_comision'
            ).exists()
            if aplicadas:
                self.stdout.write(self.style.SUCCESS("    ✓ Migración 0010 aplicada en BD"))
            else:
                self.stdout.write(self.style.ERROR("    ✗ Migración 0010 NO aplicada — ejecutar migrate"))
                ok = False
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"    ✗ Error verificando migraciones: {e}"))
            ok = False

        # ── 2. Empresas existentes ────────────────────────────────────
        self.stdout.write("\n[2] Empresas registradas:")
        empresas = Empresa.objects.all()
        if empresas.exists():
            for emp in empresas:
                total_usuarios = UserProfile.objects.filter(empresa=emp).count()
                total_clientes = Cliente.objects.filter(empresa=emp).count()
                total_metas = MetaVentas.objects.filter(empresa=emp).count()
                total_comisiones = Comision.objects.filter(empresa=emp).count()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"    ✓ [{emp.id}] {emp.nombre} — "
                        f"{total_usuarios} usuarios, {total_clientes} clientes, "
                        f"{total_metas} metas, {total_comisiones} comisiones"
                    )
                )
        else:
            self.stdout.write(self.style.WARNING("    ⚠ No hay empresas registradas — crear desde Django Admin"))
            ok = False

        # ── 3. UserProfile sin empresa ────────────────────────────────
        self.stdout.write("\n[3] Usuarios sin empresa asignada:")
        perfiles_sin_empresa = UserProfile.objects.filter(empresa__isnull=True)
        if perfiles_sin_empresa.exists():
            for p in perfiles_sin_empresa:
                self.stdout.write(
                    self.style.WARNING(f"    ⚠ {p.user.email} (id={p.user.id}) — sin empresa")
                )
            ok = False
        else:
            self.stdout.write(self.style.SUCCESS("    ✓ Todos los usuarios tienen empresa asignada"))

        # ── 4. Usuarios activos sin UserProfile ───────────────────────
        self.stdout.write("\n[4] Usuarios activos sin perfil:")
        sin_perfil = User.objects.filter(is_active=True, profile__isnull=True)
        if sin_perfil.exists():
            for u in sin_perfil:
                self.stdout.write(
                    self.style.WARNING(f"    ⚠ {u.email} (id={u.id}) — sin UserProfile")
                )
            ok = False
        else:
            self.stdout.write(self.style.SUCCESS("    ✓ Todos los usuarios activos tienen perfil"))

        # ── 5. Clientes sin empresa ───────────────────────────────────
        self.stdout.write("\n[5] Clientes sin empresa:")
        clientes_null = Cliente.objects.filter(empresa__isnull=True)
        total_clientes = Cliente.objects.count()
        if clientes_null.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"    ⚠ {clientes_null.count()} / {total_clientes} clientes sin empresa"
                )
            )
            for c in clientes_null[:10]:
                self.stdout.write(f"       - [{c.id}] {c.nombre_empresa}")
            if clientes_null.count() > 10:
                self.stdout.write(f"       ... y {clientes_null.count() - 10} más")
            if fix:
                self._fix_clientes_sin_empresa(clientes_null)
            ok = False
        else:
            self.stdout.write(
                self.style.SUCCESS(f"    ✓ Todos los clientes ({total_clientes}) tienen empresa")
            )

        # ── 6. MetaVentas sin empresa ─────────────────────────────────
        self.stdout.write("\n[6] MetaVentas sin empresa:")
        metas_null = MetaVentas.objects.filter(empresa__isnull=True)
        total_metas = MetaVentas.objects.count()
        if metas_null.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"    ⚠ {metas_null.count()} / {total_metas} metas sin empresa"
                )
            )
            for m in metas_null[:10]:
                self.stdout.write(f"       - [{m.id}] {m.usuario.email if m.usuario else 'sin usuario'}")
            if fix:
                self._fix_metas_sin_empresa(metas_null)
            ok = False
        else:
            self.stdout.write(
                self.style.SUCCESS(f"    ✓ Todas las metas ({total_metas}) tienen empresa")
            )

        # ── 7. Comisiones sin empresa ─────────────────────────────────
        self.stdout.write("\n[7] Comisiones sin empresa:")
        comisiones_null = Comision.objects.filter(empresa__isnull=True)
        total_comisiones = Comision.objects.count()
        if comisiones_null.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"    ⚠ {comisiones_null.count()} / {total_comisiones} comisiones sin empresa"
                )
            )
            for c in comisiones_null[:10]:
                self.stdout.write(f"       - [{c.id}] {c.usuario.email if c.usuario else 'sin usuario'}")
            if fix:
                self._fix_comisiones_sin_empresa(comisiones_null)
            ok = False
        else:
            self.stdout.write(
                self.style.SUCCESS(f"    ✓ Todas las comisiones ({total_comisiones}) tienen empresa")
            )

        # ── 8. Resumen final ──────────────────────────────────────────
        self.stdout.write("\n" + "="*60)
        if ok:
            self.stdout.write(self.style.SUCCESS("  RESULTADO: ✓ TENANCY OK — Sistema listo para producción"))
        else:
            self.stdout.write(self.style.ERROR("  RESULTADO: ✗ REQUIERE ATENCIÓN — Ver puntos marcados con ⚠"))
            if not fix:
                self.stdout.write(self.style.WARNING(
                    "  Ejecutar con --fix para corrección automática de registros recuperables"
                ))
        self.stdout.write("="*60 + "\n")

    # ── Métodos de corrección automática ──────────────────────────────

    def _fix_clientes_sin_empresa(self, queryset):
        """Intenta asignar empresa desde usuario_asignado o creado_por."""
        corregidos = 0
        for cliente in queryset:
            empresa = None
            for fuente in [cliente.usuario_asignado, cliente.creado_por]:
                if fuente:
                    try:
                        empresa = fuente.profile.empresa
                        if empresa:
                            break
                    except Exception:
                        continue
            if empresa:
                cliente.empresa = empresa
                cliente.save(update_fields=['empresa'])
                corregidos += 1
        self.stdout.write(self.style.SUCCESS(f"    → Corregidos automáticamente: {corregidos} clientes"))

    def _fix_metas_sin_empresa(self, queryset):
        """Intenta asignar empresa desde el usuario de la meta."""
        corregidos = 0
        for meta in queryset:
            if meta.usuario:
                try:
                    empresa = meta.usuario.profile.empresa
                    if empresa:
                        meta.empresa = empresa
                        meta.save(update_fields=['empresa'])
                        corregidos += 1
                except Exception:
                    pass
        self.stdout.write(self.style.SUCCESS(f"    → Corregidas automáticamente: {corregidos} metas"))

    def _fix_comisiones_sin_empresa(self, queryset):
        """Intenta asignar empresa desde el usuario de la comisión."""
        corregidos = 0
        for comision in queryset:
            if comision.usuario:
                try:
                    empresa = comision.usuario.profile.empresa
                    if empresa:
                        comision.empresa = empresa
                        comision.save(update_fields=['empresa'])
                        corregidos += 1
                except Exception:
                    pass
        self.stdout.write(self.style.SUCCESS(f"    → Corregidas automáticamente: {corregidos} comisiones"))
