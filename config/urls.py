from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.static import serve

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    # Sirve archivos subidos por usuarios. login_required asegura que solo
    # usuarios autenticados puedan acceder a documentos privados.
    # Suficiente para piloto; migrar a almacenamiento externo (S3/Cloudinary) en producción masiva.
    re_path(r'^media/(?P<path>.+)$', login_required(serve), {'document_root': settings.MEDIA_ROOT}),
]
