from django.urls import path
from .views import (
    # Auth
    LoginView, LogoutView, AdminRedirectView, EjecutivoClientesView, IndexView,
    SindiAppLoginView,
    # Dashboard
    DashboardView, CreateEjecutivoView, SubordinadosManagementView,
    SindiAppDashboardView,
    # Cliente
    ClienteListView, ClienteCreateView, ClienteDetailView, ClienteUpdateView, ClienteDeleteView,
    ClienteImportView, ClientesProspectadosView,
    # Contacto
    ContactoListView, ContactoCreateView, ContactoDetailView, ContactoUpdateView, ContactoDeleteView,
    # Oportunidad
    OportunidadListView, OportunidadCreateView, OportunidadDetailView, OportunidadUpdateView, OportunidadDeleteView, OportunidadContactosAPIView,
    # Llamada
    LlamadaListView, LlamadaCreateView, LlamadaDetailView, LlamadaUpdateView, LlamadaDeleteView,
    # MetaVentas
    MetaVentasListView, MetaVentasCreateView, MetaVentasUpdateView,
    # Comisión
    ComisionListView, ComisionDetailView,
    # Seguimiento
    SeguimientoListView, SeguimientoCreateView, SeguimientoUpdateView, SeguimientoDeleteView,
    # Admin utilities
    FixRogersRoleView,
    AsignarEquipoView,
    DiagnosticoTenancyView,
    SocioSindicatoListView,
    SocioSindicatoCreateView,
    SocioSindicatoUpdateView,
    TipoBeneficioSindicatoListView,
    TipoBeneficioSindicatoCreateView,
    TipoBeneficioSindicatoUpdateView,
    MovimientoSindicatoListView,
    MovimientoSindicatoCreateView,
    MovimientoSindicatoUpdateView,
    MovimientoSindicatoImportView,
    ConsultaRutSindicatoView,
    ConsolidadoSindicatoHistorialView,
    ConsolidadoSindicatoDetalleView,
    ConsolidadoSindicatoGenerarView,
    ConsolidadoSindicatoRecalcularView,
    ConsolidadoSindicatoCerrarPeriodoView,
    ConsolidadoSindicatoExportarView,
    SindiAppSocioSindicatoListView,
    SindiAppSocioSindicatoCreateView,
    SindiAppSocioSindicatoUpdateView,
    SindiAppTipoBeneficioSindicatoListView,
    SindiAppTipoBeneficioSindicatoCreateView,
    SindiAppTipoBeneficioSindicatoUpdateView,
    SindiAppMovimientoSindicatoListView,
    SindiAppMovimientoSindicatoCreateView,
    SindiAppMovimientoSindicatoUpdateView,
    SindiAppMovimientoSindicatoImportView,
    SindiAppConsultaRutSindicatoView,
    SindiAppConsolidadoSindicatoHistorialView,
    SindiAppConsolidadoSindicatoDetalleView,
    SindiAppConsolidadoSindicatoGenerarView,
    SindiAppConsolidadoSindicatoRecalcularView,
    SindiAppConsolidadoSindicatoCerrarPeriodoView,
    SindiAppConsolidadoSindicatoExportarView,
    SindiAppConsolidadoSindicatoExportacionListView,
    SindiAppAuditoriaListView,
    SindiAppAlertaSindicatoListView,
    SindiAppAlertaSindicatoAccionView,
    DocumentoSindicatoListView,
    DocumentoSindicatoSubirView,
    DocumentoSindicatoRevisarView,
    DocumentoSindicatoConfirmarView,
    DocumentoSindicatoRechazarView,
)
from .views import api_comunas
from .views_ai import AuditarOportunidadView, PrepararContactoView, SugerirEstrategiaView

app_name = "core"

urlpatterns = [
    # Admin redirect with Spanish
    path("admin-es/", AdminRedirectView.as_view(), name="admin_spanish"),
    
    # Autenticación
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("sindiapp/login/", SindiAppLoginView.as_view(), name="sindiapp_login"),
    
    # Dashboard - Home redirige según el rol
    path("", IndexView.as_view(), name="index"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("ejecutivo/", EjecutivoClientesView.as_view(), name="ejecutivo_clientes"),
    path("crear-ejecutivo/", CreateEjecutivoView.as_view(), name="crear_ejecutivo"),
    path("vendedores/", SubordinadosManagementView.as_view(), name="subordinados_management"),
    
    # Clientes
    path("clientes/", ClienteListView.as_view(), name="cliente_list"),
    path("clientes/importar/", ClienteImportView.as_view(), name="cliente_import"),
    path("clientes/prospectados/", ClientesProspectadosView.as_view(), name="clientes_prospectados"),
    path("clientes/nuevo/", ClienteCreateView.as_view(), name="cliente_create"),
    path("clientes/<int:pk>/", ClienteDetailView.as_view(), name="cliente_detail"),
    path("clientes/<int:pk>/editar/", ClienteUpdateView.as_view(), name="cliente_update"),
    path("clientes/<int:pk>/eliminar/", ClienteDeleteView.as_view(), name="cliente_delete"),
    
    # Contactos
    path("contactos/", ContactoListView.as_view(), name="contacto_list"),
    path("contactos/nuevo/", ContactoCreateView.as_view(), name="contacto_create"),
    path("contactos/<int:pk>/", ContactoDetailView.as_view(), name="contacto_detail"),
    path("contactos/<int:pk>/editar/", ContactoUpdateView.as_view(), name="contacto_update"),
    path("contactos/<int:pk>/eliminar/", ContactoDeleteView.as_view(), name="contacto_delete"),
    
    # Oportunidades
    path("oportunidades/", OportunidadListView.as_view(), name="oportunidad_list"),
    path("oportunidades/nueva/", OportunidadCreateView.as_view(), name="oportunidad_create"),
    path("oportunidades/<int:pk>/", OportunidadDetailView.as_view(), name="oportunidad_detail"),
    path("oportunidades/<int:pk>/editar/", OportunidadUpdateView.as_view(), name="oportunidad_update"),
    path("oportunidades/<int:pk>/eliminar/", OportunidadDeleteView.as_view(), name="oportunidad_delete"),
    path("api/oportunidades/<int:pk>/contactos/", OportunidadContactosAPIView.as_view(), name="oportunidad_contactos_api"),
    
    # Gestiones (ex Llamadas)
    path("gestiones/", LlamadaListView.as_view(), name="llamada_list"),
    path("gestiones/nueva/", LlamadaCreateView.as_view(), name="llamada_create"),
    path("gestiones/<int:pk>/", LlamadaDetailView.as_view(), name="llamada_detail"),
    path("gestiones/<int:pk>/editar/", LlamadaUpdateView.as_view(), name="llamada_update"),
    path("gestiones/<int:pk>/eliminar/", LlamadaDeleteView.as_view(), name="llamada_delete"),
    
    # Metas de Ventas
    path("metas/", MetaVentasListView.as_view(), name="meta_ventas_list"),
    path("metas/nueva/", MetaVentasCreateView.as_view(), name="meta_ventas_create"),
    path("metas/<int:pk>/editar/", MetaVentasUpdateView.as_view(), name="meta_ventas_update"),
    
    # Comisiones
    path("comisiones/", ComisionListView.as_view(), name="comision_list"),
    path("comisiones/<int:pk>/", ComisionDetailView.as_view(), name="comision_detail"),
    
    # Seguimientos
    path("seguimientos/", SeguimientoListView.as_view(), name="seguimiento_list"),
    path("seguimientos/nuevo/", SeguimientoCreateView.as_view(), name="seguimiento_create"),
    path("seguimientos/<int:pk>/editar/", SeguimientoUpdateView.as_view(), name="seguimiento_update"),
    path("seguimientos/<int:pk>/eliminar/", SeguimientoDeleteView.as_view(), name="seguimiento_delete"),
    
    # Admin utilities
    path("admin-fix-rogers/", FixRogersRoleView.as_view(), name="fix_rogers_role"),
    path("equipo/asignar/", AsignarEquipoView.as_view(), name="asignar_equipo"),
    path("herramientas/validar-tenancy/", DiagnosticoTenancyView.as_view(), name="diagnostico_tenancy"),

    # API
    path("api/comunas/", api_comunas, name="api_comunas"),

    # ── SindiApp (interfaz cliente) ──────────────────────────────────
    path('sindiapp/dashboard/', SindiAppDashboardView.as_view(), name='sindiapp_dashboard'),
    path('sindiapp/socios/', SindiAppSocioSindicatoListView.as_view(), name='sindiapp_socio_list'),
    path('sindiapp/socios/nuevo/', SindiAppSocioSindicatoCreateView.as_view(), name='sindiapp_socio_create'),
    path('sindiapp/socios/<int:pk>/editar/', SindiAppSocioSindicatoUpdateView.as_view(), name='sindiapp_socio_update'),
    path('sindiapp/beneficios/', SindiAppTipoBeneficioSindicatoListView.as_view(), name='sindiapp_beneficio_list'),
    path('sindiapp/beneficios/nuevo/', SindiAppTipoBeneficioSindicatoCreateView.as_view(), name='sindiapp_beneficio_create'),
    path('sindiapp/beneficios/<int:pk>/editar/', SindiAppTipoBeneficioSindicatoUpdateView.as_view(), name='sindiapp_beneficio_update'),
    path('sindiapp/movimientos/', SindiAppMovimientoSindicatoListView.as_view(), name='sindiapp_movimiento_list'),
    path('sindiapp/importar/', SindiAppMovimientoSindicatoImportView.as_view(), name='sindiapp_movimiento_import'),
    path('sindiapp/movimientos/nuevo/', SindiAppMovimientoSindicatoCreateView.as_view(), name='sindiapp_movimiento_create'),
    path('sindiapp/movimientos/<int:pk>/editar/', SindiAppMovimientoSindicatoUpdateView.as_view(), name='sindiapp_movimiento_update'),
    path('sindiapp/consulta-rut/', SindiAppConsultaRutSindicatoView.as_view(), name='sindiapp_consulta_rut'),
    path('sindiapp/consolidados/', SindiAppConsolidadoSindicatoHistorialView.as_view(), name='sindiapp_consolidado_historial'),
    path('sindiapp/consolidados/<int:pk>/', SindiAppConsolidadoSindicatoDetalleView.as_view(), name='sindiapp_consolidado_detalle'),
    path('sindiapp/consolidados/generar/', SindiAppConsolidadoSindicatoGenerarView.as_view(), name='sindiapp_consolidado_generar'),
    path('sindiapp/consolidados/recalcular/', SindiAppConsolidadoSindicatoRecalcularView.as_view(), name='sindiapp_consolidado_recalcular'),
    path('sindiapp/consolidados/cerrar/', SindiAppConsolidadoSindicatoCerrarPeriodoView.as_view(), name='sindiapp_consolidado_cerrar'),
    path('sindiapp/consolidados/<int:pk>/exportar/', SindiAppConsolidadoSindicatoExportarView.as_view(), name='sindiapp_consolidado_exportar'),
    path('sindiapp/exportacion/', SindiAppConsolidadoSindicatoExportacionListView.as_view(), name='sindiapp_exportacion_list'),
    path('sindiapp/alertas/', SindiAppAlertaSindicatoListView.as_view(), name='sindiapp_alerta_list'),
    path('sindiapp/alertas/<int:pk>/<str:accion>/', SindiAppAlertaSindicatoAccionView.as_view(), name='sindiapp_alerta_accion'),
    path('sindiapp/auditoria/', SindiAppAuditoriaListView.as_view(), name='sindiapp_auditoria_list'),
    path('sindiapp/documentos/', DocumentoSindicatoListView.as_view(), name='sindiapp_documento_list'),
    path('sindiapp/documentos/subir/', DocumentoSindicatoSubirView.as_view(), name='sindiapp_documento_subir'),
    path('sindiapp/documentos/<int:pk>/revisar/', DocumentoSindicatoRevisarView.as_view(), name='sindiapp_documento_revisar'),
    path('sindiapp/documentos/<int:pk>/confirmar/', DocumentoSindicatoConfirmarView.as_view(), name='sindiapp_documento_confirmar'),
    path('sindiapp/documentos/<int:pk>/rechazar/', DocumentoSindicatoRechazarView.as_view(), name='sindiapp_documento_rechazar'),

    # ── Módulo Sindicato MVP ─────────────────────────────────────────
    path('sindicato/socios/', SocioSindicatoListView.as_view(), name='sindicato_socio_list'),
    path('sindicato/socios/nuevo/', SocioSindicatoCreateView.as_view(), name='sindicato_socio_create'),
    path('sindicato/socios/<int:pk>/editar/', SocioSindicatoUpdateView.as_view(), name='sindicato_socio_update'),
    path('sindicato/beneficios/', TipoBeneficioSindicatoListView.as_view(), name='sindicato_beneficio_list'),
    path('sindicato/beneficios/nuevo/', TipoBeneficioSindicatoCreateView.as_view(), name='sindicato_beneficio_create'),
    path('sindicato/beneficios/<int:pk>/editar/', TipoBeneficioSindicatoUpdateView.as_view(), name='sindicato_beneficio_update'),
    path('sindicato/movimientos/', MovimientoSindicatoListView.as_view(), name='sindicato_movimiento_list'),
    path('sindicato/importar/', MovimientoSindicatoImportView.as_view(), name='sindicato_movimiento_import'),
    path('sindicato/movimientos/nuevo/', MovimientoSindicatoCreateView.as_view(), name='sindicato_movimiento_create'),
    path('sindicato/movimientos/<int:pk>/editar/', MovimientoSindicatoUpdateView.as_view(), name='sindicato_movimiento_update'),
    path('sindicato/consulta-rut/', ConsultaRutSindicatoView.as_view(), name='sindicato_consulta_rut'),
    path('sindicato/consolidados/', ConsolidadoSindicatoHistorialView.as_view(), name='sindicato_consolidado_historial'),
    path('sindicato/consolidados/<int:pk>/', ConsolidadoSindicatoDetalleView.as_view(), name='sindicato_consolidado_detalle'),
    path('sindicato/consolidados/generar/', ConsolidadoSindicatoGenerarView.as_view(), name='sindicato_consolidado_generar'),
    path('sindicato/consolidados/recalcular/', ConsolidadoSindicatoRecalcularView.as_view(), name='sindicato_consolidado_recalcular'),
    path('sindicato/consolidados/cerrar/', ConsolidadoSindicatoCerrarPeriodoView.as_view(), name='sindicato_consolidado_cerrar'),
    path('sindicato/consolidados/<int:pk>/exportar/', ConsolidadoSindicatoExportarView.as_view(), name='sindicato_consolidado_exportar'),

    # ── Asistente / Copiloto de IA ────────────────────────────────────
    path(
        "api/v1/ventas/preparar-contacto/<int:id_contacto>/",
        PrepararContactoView.as_view(),
        name="ai_preparar_contacto",
    ),
    path(
        "api/v1/ventas/sugerir-estrategia/<int:id_oportunidad>/",
        SugerirEstrategiaView.as_view(),
        name="ai_sugerir_estrategia",
    ),
    path(
        "api/v1/admin/auditar-oportunidad/<int:id_oportunidad>/",
        AuditarOportunidadView.as_view(),
        name="ai_auditar_oportunidad",
    ),
]
