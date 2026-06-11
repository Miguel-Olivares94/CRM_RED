from django.urls import path
from .views import (
    # Auth
    LoginView, LogoutView, AdminRedirectView, EjecutivoClientesView, IndexView,
    # Dashboard
    DashboardView, CreateEjecutivoView, SubordinadosManagementView,
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
