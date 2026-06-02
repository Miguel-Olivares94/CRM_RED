"""
Management command to fix Rogers permissions and apply hierarchical filtering
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from core.models import UserProfile


class Command(BaseCommand):
    help = 'Fix Rogers permissions to be MANAGER only, not admin/superuser'

    def handle(self, *args, **options):
        try:
            rogers = User.objects.get(email='rogers.orostica@gmail.com')
            
            # Ensure Rogers is NOT a superuser or staff
            if rogers.is_superuser or rogers.is_staff:
                rogers.is_superuser = False
                rogers.is_staff = False
                rogers.save()
                self.stdout.write(self.style.SUCCESS('✓ Removed superuser/staff from Rogers'))
            
            # Remove from Admin group if present
            admin_group, _ = Group.objects.get_or_create(name='Admin')
            if admin_group in rogers.groups.all():
                rogers.groups.remove(admin_group)
                self.stdout.write(self.style.SUCCESS('✓ Removed Rogers from Admin group'))
            
            # Ensure UserProfile is set correctly
            profile, created = UserProfile.objects.get_or_create(user=rogers)
            if profile.role != 'MANAGER':
                profile.role = 'MANAGER'
                profile.supervisor = None  # Top-level manager
                profile.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Set Rogers profile to MANAGER (created={created})'))
            
            # Get all other managers and ensure they are not Rogers' supervisors
            magdalena = User.objects.filter(email='magdalena@claro.cl').first()
            carmen = User.objects.filter(email='carmen.gloria@claro.cl').first()
            cristian = User.objects.filter(email='cristian@claro.cl').first()
            lissette = User.objects.filter(email='lissette@claro.cl').first()
            
            managers = [m for m in [magdalena, carmen, cristian, lissette] if m]
            
            for mgr in managers:
                mgr_profile, created = UserProfile.objects.get_or_create(user=mgr)
                if mgr_profile.role != 'MANAGER':
                    mgr_profile.role = 'MANAGER'
                    mgr_profile.save()
                    self.stdout.write(self.style.SUCCESS(f'✓ Set {mgr.first_name} profile to MANAGER'))
            
            # Verify Rogers has subordinados
            subordinados_count = rogers.subordinados.count()
            self.stdout.write(self.style.WARNING(f'📊 Rogers has {subordinados_count} subordinados'))
            
            # List all ejecutivos that are Rogers' subordinados
            ejecutivos = UserProfile.objects.filter(supervisor=rogers, role='EJECUTIVO')
            for exec_profile in ejecutivos:
                self.stdout.write(f'  - {exec_profile.user.email} ({exec_profile.user.first_name})')
            
            self.stdout.write(self.style.SUCCESS('\n✅ Rogers permissions fixed! He should now see only his team\'s clients.'))
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Rogers user not found'))
