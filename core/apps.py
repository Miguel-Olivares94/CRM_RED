from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    
    def ready(self):
        # Personalizar el formulario de login del admin
        from django.contrib.admin.views.decorators import staff_member_required
        from django.contrib.admin import AdminSite
        from django.contrib.auth.forms import AuthenticationForm
        from django import forms
        
        class CustomAdminAuthenticationForm(AuthenticationForm):
            """Cambiar etiqueta de username a Email"""
            username = forms.CharField(
                label="Email",
                max_length=254,
                widget=forms.TextInput(attrs={
                    'autofocus': True,
                    'class': 'vTextField',
                })
            )
        
        # Reemplazar el formulario de login en el AdminSite por defecto
        AdminSite.login_form = CustomAdminAuthenticationForm
        
        # Personalizar títulos
        from django.contrib import admin
        admin.site.site_header = "Administración CRM"
        admin.site.site_title = "CRM Claro"
        admin.site.index_title = "Bienvenido a la Administración CRM"

        # Registrar signals
        import core.signals  # noqa: F401

