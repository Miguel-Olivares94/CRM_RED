"""
Management command para configurar la jerarquía de supervisores
Asigna Roy como MANAGER supervisor de los 7 vendedores
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile


class Command(BaseCommand):
    help = 'Configura la jerarquía de supervisores: Roy supervisa a los 7 vendedores'

    def handle(self, *args, **options):
        try:
            # Obtener Roy (usando el email correcto)
            roy = User.objects.get(email='rogers.orostica@gmail.com')
            
            # Vendedores a supervisar
            vendedores_emails = [
                'carlos.carrasco@claro.cl',
                'ernesto.lindermann@claro.cl',
                'felipe.monje@claro.cl',
                'luisa.olivares@claro.cl',
                'manuel.navarrete@claro.cl',
                'solange.romanet@claro.cl',
                'victor.henriquez@claro.cl',
            ]
            
            # 1. Crear o actualizar profile de Roy como MANAGER
            roy_profile, created = UserProfile.objects.get_or_create(user=roy)
            roy_profile.role = 'MANAGER'
            roy_profile.supervisor = None  # Roy no tiene supervisor (él es manager)
            roy_profile.save()
            
            if created:
                self.stdout.write(f"✓ Creado profile para Roy como MANAGER")
            else:
                self.stdout.write(f"✓ Actualizado profile de Roy a MANAGER")
            
            # 2. Asignar los 7 vendedores a Roy como supervisor
            for email in vendedores_emails:
                try:
                    vendedor = User.objects.get(email=email)
                    vendedor_profile, created = UserProfile.objects.get_or_create(user=vendedor)
                    vendedor_profile.role = 'EJECUTIVO'
                    vendedor_profile.supervisor = roy
                    vendedor_profile.save()
                    
                    status = "✓ Creado" if created else "✓ Actualizado"
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"{status} profile para {vendedor.get_full_name()} "
                            f"(supervisor: {roy.get_full_name()})"
                        )
                    )
                except User.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f"⚠ Vendedor no encontrado: {email}")
                    )
            
            self.stdout.write(
                self.style.SUCCESS("\n✓ Jerarquía configurada exitosamente")
            )
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("✗ Roy no encontrado. Asegúrate de que exista un usuario con email='rogers.orostica@gmail.com'")
            )
