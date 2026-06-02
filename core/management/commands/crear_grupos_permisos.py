"""
Management command para crear los grupos de usuarios (Admin y Ejecutivo)
Uso: python manage.py crear_grupos_permisos
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Crear grupos de usuarios (Admin y Ejecutivo) con permisos apropiados'

    def handle(self, *args, **options):
        # Crear grupo Admin
        admin_group, admin_created = Group.objects.get_or_create(name='Admin')
        
        # Crear grupo Ejecutivo
        ejecutivo_group, ejecutivo_created = Group.objects.get_or_create(name='Ejecutivo')
        
        # Obtener todos los permisos (para el grupo Admin)
        all_permissions = Permission.objects.all()
        
        # Permisos para Admin (todos los permisos)
        admin_group.permissions.set(all_permissions)
        
        # Permisos para Ejecutivo (solo lectura y edición de clientes/oportunidades)
        # Permisos que tiene el ejecutivo:
        # - Ver clientes (pero filtrados)
        # - Cambiar clientes
        # - Ver oportunidades (pero filtradas)
        # - Cambiar oportunidades
        # - Agregar seguimientos
        # - Ver seguimientos
        ejecutivo_perms = Permission.objects.filter(
            codename__in=[
                'view_cliente',
                'change_cliente',
                'view_oportunidad',
                'change_oportunidad',
                'add_seguimiento',
                'view_seguimiento',
                'add_contacto',
                'view_contacto',
                'add_llamada',
                'view_llamada',
            ]
        )
        ejecutivo_group.permissions.set(ejecutivo_perms)
        
        if admin_created:
            self.stdout.write(self.style.SUCCESS('✅ Grupo "Admin" creado exitosamente'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ Grupo "Admin" ya existía'))
        
        if ejecutivo_created:
            self.stdout.write(self.style.SUCCESS('✅ Grupo "Ejecutivo" creado exitosamente'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ Grupo "Ejecutivo" ya existía'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Grupos y permisos configurados correctamente'))
        self.stdout.write('\nResumen:')
        self.stdout.write(f'  • Admin: {admin_group.permissions.count()} permisos')
        self.stdout.write(f'  • Ejecutivo: {ejecutivo_group.permissions.count()} permisos')
