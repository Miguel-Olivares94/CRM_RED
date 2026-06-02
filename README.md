# CRM Starter - Django

Estructura inicial para comenzar la aplicación web basada en tu Excel.

## Incluye
- Modelos principales del CRM
- Formularios base
- Vistas iniciales
- URLs
- Administración en Django Admin
- Plantillas Bootstrap

## Pasos sugeridos
1. Crear proyecto Django:
   ```bash
   django-admin startproject config .
   ```
2. Copiar la carpeta `core` dentro del proyecto.
3. Agregar `core` a `INSTALLED_APPS`.
4. Incluir `path('', include('core.urls'))` en `config/urls.py`.
5. Ejecutar migraciones:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
6. Crear superusuario:
   ```bash
   python manage.py createsuperuser
   ```
7. Levantar servidor:
   ```bash
   python manage.py runserver
   ```

## Módulos iniciales
- Clientes
- Contactos
- Cartera asignada
- Gestión de llamadas
- Seguimientos
- Funnel
- Comisiones
