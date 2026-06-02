"""
Management command to fix Rogers' UserProfile role from EJECUTIVO to MANAGER
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Fix Rogers\' UserProfile role to MANAGER so he can see his subordinates\' clients'

    def handle(self, *args, **options):
        try:
            # Find Rogers (roy)
            rogers = User.objects.get(username='roy')
            self.stdout.write(f'Found user: {rogers.email} (username: {rogers.username})')
            
            # Get or create UserProfile
            profile, created = UserProfile.objects.get_or_create(user=rogers)
            self.stdout.write(f'UserProfile: {"created" if created else "already exists"}')
            
            # Update role to MANAGER
            old_role = profile.role
            profile.role = 'MANAGER'
            profile.save()
            
            self.stdout.write(self.style.SUCCESS(
                f'✓ Updated Rogers\' role from "{old_role}" to "MANAGER"'
            ))
            
            # Verify he has subordinados
            subordinados = profile.subordinados.all()
            self.stdout.write(f'✓ Rogers has {subordinados.count()} subordinates')
            for sub in subordinados:
                self.stdout.write(f'  - {sub.get_full_name()} ({sub.email})')
                
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User "roy" not found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
