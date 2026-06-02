from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Cliente


class Command(BaseCommand):
    help = 'Assign one client from Roy to vendedor@claro.cl'

    def handle(self, *args, **options):
        try:
            # Get users
            roy = User.objects.get(email='rogers.orostica@gmail.com')
            vendedor = User.objects.get(email='vendedor@claro.cl')
            
            # Get first client from Roy
            cliente = Cliente.objects.filter(usuario_asignado=roy).first()
            
            if cliente:
                cliente.usuario_asignado = vendedor
                cliente.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Cliente asignado exitosamente:'))
                self.stdout.write(f'  RUT: {cliente.rut}')
                self.stdout.write(f'  Empresa: {cliente.nombre_empresa}')
                self.stdout.write(f'  Asignado a: {vendedor.email}')
            else:
                self.stdout.write(self.style.ERROR('No hay clientes para asignar'))
        except User.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f'Usuario no encontrado: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
