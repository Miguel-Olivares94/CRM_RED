from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile
import secrets
import string


class Command(BaseCommand):
    help = "Crear managers para Magdalena, Carmen Gloria, Cristian y Lissette"

    def handle(self, *args, **options):
        managers_data = [
            {
                'email': 'magdalena@claro.cl',
                'username': 'magdalena',
                'first_name': 'Magdalena',
                'last_name': 'Manager'
            },
            {
                'email': 'carmen.gloria@claro.cl',
                'username': 'carmen.gloria',
                'first_name': 'Carmen Gloria',
                'last_name': 'Manager'
            },
            {
                'email': 'cristian@claro.cl',
                'username': 'cristian',
                'first_name': 'Cristian',
                'last_name': 'Manager'
            },
            {
                'email': 'lissette@claro.cl',
                'username': 'lissette',
                'first_name': 'Lissette',
                'last_name': 'Manager'
            }
        ]

        for manager_data in managers_data:
            try:
                # Crear usuario
                user, created = User.objects.get_or_create(
                    email=manager_data['email'],
                    defaults={
                        'username': manager_data['username'],
                        'first_name': manager_data['first_name'],
                        'last_name': manager_data['last_name']
                    }
                )

                if created:
                    # Generar contraseña segura
                    password = ''.join(
                        secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*')
                        for _ in range(16)
                    )
                    user.set_password(password)
                    user.save()
                    pwd_display = password
                else:
                    pwd_display = "(usuario existente)"

                # Crear o actualizar UserProfile
                profile, profile_created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'role': 'MANAGER',
                        'supervisor': None
                    }
                )

                if not profile_created and profile.role != 'MANAGER':
                    profile.role = 'MANAGER'
                    profile.supervisor = None
                    profile.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Manager creado: {user.get_full_name()} ({user.email}) | Contraseña: {pwd_display}"
                    )
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Error creando {manager_data['email']}: {str(e)}")
                )

        self.stdout.write(self.style.SUCCESS("\n✓ Todos los managers creados exitosamente"))
