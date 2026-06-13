from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from .models import (
    Empresa, CampoPersonalizado, Cliente, Contacto, Oportunidad, Llamada,
    MetaVentas, Comision, Seguimiento, UserProfile,
    SocioSindicato, TipoBeneficioSindicato, MovimientoSindicato,
    AuditoriaSindicato, ConsolidadoMensualSindicato, ConsolidadoDetalleSindicato,
)
from .resources import ClienteResource, OportunidadResource


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'rut', 'dominio', 'activo', 'total_usuarios', 'total_clientes')
    search_fields = ('nombre', 'rut', 'dominio')
    list_filter = ('activo', 'tipo')
    readonly_fields = ('created_at', 'updated_at')

    def get_readonly_fields(self, request, obj=None):
        """
        Si la empresa es PLATAFORMA, el campo `tipo` es de solo lectura
        para evitar que un admin la degrade accidentalmente.
        Solo el superusuario puede ver/editar todos los campos.
        """
        readonly = list(super().get_readonly_fields(request, obj))
        if obj and obj.tipo == 'PLATAFORMA' and not request.user.is_superuser:
            readonly += ['tipo', 'nombre', 'rut', 'dominio', 'activo']
        return readonly

    def has_delete_permission(self, request, obj=None):
        """Impide eliminar la empresa PLATAFORMA desde el Admin."""
        if obj and obj.tipo == 'PLATAFORMA':
            return False
        return super().has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        """
        Garantiza que solo puede existir UNA empresa PLATAFORMA.
        Si se intenta crear una segunda, lanza error visible en el Admin.
        """
        from django.contrib import messages
        if obj.tipo == 'PLATAFORMA':
            existe = Empresa.objects.filter(tipo='PLATAFORMA').exclude(pk=obj.pk).exists()
            if existe:
                messages.error(request, 'Ya existe una empresa de tipo PLATAFORMA. Solo puede haber una.')
                return  # No guarda
        super().save_model(request, obj, form, change)

    def total_usuarios(self, obj):
        return obj.usuarios.count()
    total_usuarios.short_description = 'Usuarios'

    def total_clientes(self, obj):
        return obj.clientes.count()
    total_clientes.short_description = 'Clientes'


@admin.register(Cliente)
class ClienteAdmin(ImportExportModelAdmin):
    resource_class = ClienteResource
    list_display = ("rut", "nombre_empresa", "segmento", "estado", "usuario_asignado", "fecha_registro")
    search_fields = ("rut", "nombre_empresa", "sector", "segmento", "edv")
    list_filter = ("estado", "usuario_asignado", "segmento", "bam", "fecha_registro")
    readonly_fields = ("fecha_registro", "created_at", "updated_at")
    
    fieldsets = (
        ("Información General", {
            "fields": ("rut", "nombre_empresa", "sector", "tipo_cliente", "estado")
        }),
        ("Ubicación", {
            "fields": ("comuna", "provincia", "region"),
            "classes": ("collapse",)
        }),
        ("Segmentación y Datos Técnicos", {
            "fields": ("dv", "segmento", "subrango", "supervisor", "subgerencia", "renta_uf_total", 
                      "q_total_lineas", "bam", "m2m", "voz", "fijo", "movil", "fijo_movil", "edv"),
            "classes": ("collapse",)
        }),
        ("Asignación", {
            "fields": ("usuario_asignado", "fecha_registro")
        }),
        ("Notas", {
            "fields": ("observaciones",),
            "classes": ("collapse",)
        }),
        ("Auditoría", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "cliente", "cargo", "rol", "email", "activo")
    search_fields = ("nombre", "cliente__nombre_empresa", "email")
    list_filter = ("rol", "activo", "cliente")
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        ("Información Personal", {
            "fields": ("cliente", "nombre", "cargo", "rol")
        }),
        ("Contacto", {
            "fields": ("email", "telefono_movil", "telefono_fijo")
        }),
        ("Estado", {
            "fields": ("activo", "orden")
        }),
        ("Auditoría", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(Oportunidad)
class OportunidadAdmin(ImportExportModelAdmin):
    resource_class = OportunidadResource
    list_display = (
        "cliente", "get_etapa_badge", "get_monto_display", "probabilidad", 
        "usuario", "get_alerta_badge", "fecha_cierre_estimada"
    )
    search_fields = ("cliente__nombre_empresa", "cliente__rut", "productos")
    list_filter = ("etapa", "estado", "usuario", "fecha_creacion")
    readonly_fields = ("fecha_creacion", "dias_sin_contacto", "estado_alerta", "created_at", "updated_at")
    
    fieldsets = (
        ("Cliente", {
            "fields": ("cliente", "usuario")
        }),
        ("Venta", {
            "fields": ("monto", "moneda", "lineas", "productos")
        }),
        ("Pipeline", {
            "fields": ("etapa", "estado", "probabilidad")
        }),
        ("Fechas", {
            "fields": ("fecha_creacion", "fecha_cierre_estimada", "fecha_cierre_real", "fecha_ultimo_contacto", "proximo_contacto")
        }),
        ("Seguimiento", {
            "fields": ("dias_sin_contacto", "estado_alerta", "observaciones")
        }),
        ("Comisión", {
            "fields": ("comision_estimada",)
        }),
        ("Auditoría", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def get_etapa_badge(self, obj):
        colors = {
            'LEAD': '#808080',
            'CONTACTO': '#0275d8',
            'CALIFICADO': '#5bc0de',
            'PROPUESTA': '#5cb85c',
            'NEGOCIACION': '#f0ad4e',
            'CIERRE': '#ff7043',
            'GANADA': '#51cf66',
            'PERDIDA': '#d32f2f',
            'DORMIDA': '#9e9e9e',
        }
        color = colors.get(obj.etapa, '#000')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 9px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_etapa_display()
        )
    get_etapa_badge.short_description = 'Etapa'
    
    def get_alerta_badge(self, obj):
        colors = {
            'AL_DIA': '#51cf66',
            'ATENCION': '#5cb85c',
            'EN_RIESGO': '#f0ad4e',
            'RIESGO_ALTO': '#ff7043',
            'DORMIDA': '#d32f2f',
            'SIN_CONTACTO': '#9e9e9e',
        }
        color = colors.get(obj.estado_alerta, '#000')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 9px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.estado_alerta
        )
    get_alerta_badge.short_description = 'Alerta'
    
    def get_monto_display(self, obj):
        return f"{obj.moneda} ${obj.monto:,.0f}"
    get_monto_display.short_description = 'Monto'


@admin.register(Llamada)
class LlamadaAdmin(admin.ModelAdmin):
    list_display = ("oportunidad", "contacto", "fecha_hora", "tipo", "resultado", "duracion_minutos")
    search_fields = ("oportunidad__cliente__nombre_empresa", "contacto__nombre", "nota_ejecutiva")
    list_filter = ("tipo", "resultado", "fecha_hora")
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        ("Relaciones", {
            "fields": ("oportunidad", "contacto", "creado_por")
        }),
        ("Llamada", {
            "fields": ("fecha_hora", "tipo", "duracion_minutos", "resultado")
        }),
        ("Detalles", {
            "fields": ("nota_ejecutiva", "productos_discutidos", "accion_pendiente")
        }),
        ("Seguimiento", {
            "fields": ("proximo_contacto_propuesto",)
        }),
        ("Auditoría", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(MetaVentas)
class MetaVentasAdmin(admin.ModelAdmin):
    list_display = ("usuario", "periodo", "meta_monto_total", "comision_base", "factor_aceleracion")
    list_filter = ("periodo", "usuario")
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        ("Identificación", {
            "fields": ("usuario", "periodo")
        }),
        ("Metas", {
            "fields": ("meta_lineas_portabilidad", "meta_lineas_nueva", "meta_lineas_m2m", "meta_monto_total")
        }),
        ("Comisiones", {
            "fields": ("comision_base", "comision_por_linea", "factor_aceleracion", "bonificacion_meta")
        }),
        ("Auditoría", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(Comision)
class ComisionAdmin(admin.ModelAdmin):
    list_display = (
        "usuario", "periodo", "lineas_portabilidad_vendidas", 
        "lineas_nueva_vendidas", "lineas_m2m_vendidas", 
        "get_total_display", "estado", "fecha_pago"
    )
    search_fields = ("usuario__email", "periodo")
    list_filter = ("estado", "periodo", "usuario")
    readonly_fields = ("fecha_calculo", "created_at", "updated_at")
    
    fieldsets = (
        ("Identificación", {
            "fields": ("usuario", "meta", "periodo")
        }),
        ("Ventas Realizadas", {
            "fields": (
                "lineas_portabilidad_vendidas", "lineas_nueva_vendidas", 
                "lineas_m2m_vendidas", "monto_total_vendido"
            )
        }),
        ("Cálculo de Comisión", {
            "fields": ("comision_calculada", "bonificacion_aplicada", "total_a_pagar")
        }),
        ("Estado", {
            "fields": ("estado", "fecha_pago", "fecha_calculo")
        }),
        ("Auditoría", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def get_total_display(self, obj):
        return f"${obj.total_a_pagar:,.0f}"
    get_total_display.short_description = 'Total a Pagar'


@admin.register(Seguimiento)
class SeguimientoAdmin(admin.ModelAdmin):
    list_display = (
        "oportunidad", "tipo", "get_prioridad_badge", 
        "estado", "fecha_vencimiento", "asignado_a"
    )
    search_fields = ("oportunidad__cliente__nombre_empresa", "descripcion")
    list_filter = ("tipo", "prioridad", "estado", "fecha_vencimiento")
    readonly_fields = ("fecha_creacion", "completado_en", "created_at", "updated_at")
    
    fieldsets = (
        ("Identificación", {
            "fields": ("oportunidad", "tipo")
        }),
        ("Descripción", {
            "fields": ("descripcion", "fecha_creacion")
        }),
        ("Asignación", {
            "fields": ("asignado_a", "prioridad")
        }),
        ("Fechas", {
            "fields": ("fecha_vencimiento", "estado", "completado_en")
        }),
        ("Auditoría", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def get_prioridad_badge(self, obj):
        colors = {
            'BAJA': '#51cf66',
            'MEDIA': '#5cb85c',
            'ALTA': '#f0ad4e',
            'CRITICA': '#d32f2f',
        }
        color = colors.get(obj.prioridad, '#000')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 9px; border-radius: 3px;">{}</span>',
            color,
            obj.get_prioridad_display()
        )
    get_prioridad_badge.short_description = 'Prioridad'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("get_full_name", "empresa", "role", "supervisor", "get_subordinados_count")
    search_fields = ("user__email", "user__first_name", "user__last_name")
    list_filter = ("role", "empresa", "supervisor")
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        ("Usuario", {
            "fields": ("user", "role", "empresa")
        }),
        ("Jerarquía", {
            "fields": ("supervisor",)
        }),
        ("Auditoría", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.email
    get_full_name.short_description = 'Nombre Usuario'
    
    def get_subordinados_count(self, obj):
        count = obj.user.subordinados.count()
        return format_html(
            '<span style="background-color: #5cb85c; color: white; padding: 3px 9px; border-radius: 3px;">{}</span>',
            count
        )
    get_subordinados_count.short_description = 'Subordinados'


@admin.register(CampoPersonalizado)
class CampoPersonalizadoAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'entidad', 'nombre', 'clave', 'tipo', 'obligatorio', 'orden', 'activo')
    list_filter = ('empresa', 'entidad', 'tipo', 'activo')
    search_fields = ('nombre', 'clave', 'empresa__nombre')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('orden', 'activo')
    ordering = ('empresa', 'entidad', 'orden', 'nombre')

    fieldsets = (
        ('Identificación', {
            'fields': ('empresa', 'entidad', 'nombre', 'clave'),
        }),
        ('Configuración del campo', {
            'fields': ('tipo', 'opciones', 'obligatorio', 'orden', 'activo'),
            'description': (
                'Para tipo Lista, ingresar opciones como lista JSON. '
                'Ejemplo: ["Opción A", "Opción B", "Opción C"]'
            ),
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        """Superusuario ve todos. Admin no-superuser solo ve campos de su empresa."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            empresa = request.user.profile.empresa
            return qs.filter(empresa=empresa)
        except Exception:
            return qs.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Al crear un campo, restringe el selector de empresa a la del usuario."""
        if db_field.name == 'empresa' and not request.user.is_superuser:
            try:
                kwargs['queryset'] = Empresa.objects.filter(pk=request.user.profile.empresa.pk)
            except Exception:
                pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(SocioSindicato)
class SocioSindicatoAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombre', 'empresa', 'estado_laboral', 'estado')
    list_filter = ('empresa', 'estado_laboral', 'estado')
    search_fields = ('rut', 'nombre')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TipoBeneficioSindicato)
class TipoBeneficioSindicatoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'empresa', 'orden_export', 'estado')
    list_filter = ('empresa', 'estado')
    search_fields = ('codigo', 'nombre')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MovimientoSindicato)
class MovimientoSindicatoAdmin(admin.ModelAdmin):
    list_display = ('periodo', 'socio', 'tipo_beneficio', 'monto', 'estado', 'empresa')
    list_filter = ('empresa', 'periodo', 'estado', 'tipo_beneficio')
    search_fields = ('socio__rut', 'socio__nombre', 'referencia_externa')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AuditoriaSindicato)
class AuditoriaSindicatoAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'empresa', 'usuario', 'accion', 'entidad', 'entidad_id')
    list_filter = ('empresa', 'accion', 'entidad', 'created_at')
    search_fields = ('resumen', 'entidad_id', 'usuario__email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ConsolidadoMensualSindicato)
class ConsolidadoMensualSindicatoAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'periodo', 'estado', 'total_socios', 'total_monto', 'fecha_generacion')
    list_filter = ('empresa', 'estado', 'periodo')
    search_fields = ('periodo',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ConsolidadoDetalleSindicato)
class ConsolidadoDetalleSindicatoAdmin(admin.ModelAdmin):
    list_display = ('consolidado', 'socio', 'tipo_beneficio', 'monto_aprobado', 'empresa')
    list_filter = ('empresa', 'consolidado__periodo', 'tipo_beneficio')
    search_fields = ('socio__rut', 'socio__nombre')
    readonly_fields = ('created_at', 'updated_at')
