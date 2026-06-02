from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import random
import string


class Command(BaseCommand):
    help = 'Crea los 7 vendedores de Roy en el grupo Ejecutivo'

    def handle(self, *args, **options):
        # Datos de los vendedores
        vendedores = [
            {
                'nombre': 'CARLOS JAVIER CARRASCO GOYO',
                'rut': '26844775-K',
                'email': 'carlos.carrasco@claro.cl'
            },
            {
                'nombre': 'ERNESTO CRISTOPHER LINDERMANN',
                'rut': '16622726-7',
                'email': 'ernesto.lindermann@claro.cl'
            },
            {
                'nombre': 'FELIPE IGNACIO MONJE GOMEZ',
                'rut': '19329554-1',
                'email': 'felipe.monje@claro.cl'
            },
            {
                'nombre': 'LUISA ANDREA OLIVARES MEJIAS',
                'rut': '12636055-K',
                'email': 'luisa.olivares@claro.cl'
            },
            {
                'nombre': 'MANUEL ALEJANDRO NAVARRETE BOB',
                'rut': '16113894-0',
                'email': 'manuel.navarrete@claro.cl'
            },
            {
                'nombre': 'SOLANGE ROMANET ZAMORA GAUNA',
                'rut': '14459521-1',
                'email': 'solange.romanet@claro.cl'
            },
            {
                'nombre': 'VICTOR MOISES HENRIQUEZ ABARCA',
                'rut': '12892752-2',
                'email': 'victor.henriquez@claro.cl'
            },
        ]

        # Obtener el grupo Ejecutivo
        try:
            grupo_ejecutivo = Group.objects.get(name='Ejecutivo')
            self.stdout.write(self.style.SUCCESS('✅ Grupo Ejecutivo encontrado'))
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Grupo Ejecutivo no existe. Créalo primero.'))
            return

        creados = 0
        actualizados = 0
        errores = 0

        self.stdout.write('\n' + '='*70)
        self.stdout.write('CREANDO VENDEDORES DE ROY')
        self.stdout.write('='*70 + '\n')

        for vendedor in vendedores:
            username = vendedor['email'].split('@')[0]  # Usar parte del email como usuario
            nombre = vendedor['nombre']
            email = vendedor['email']

            try:
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'first_name': nombre.split()[0],  # Primer nombre
                        'last_name': ' '.join(nombre.split()[1:]),  # Resto de nombres
                        'is_staff': True,
                        'is_active': True,
                    }
                )

                if created:
                    # Generar contraseña segura
                    password = ''.join(random.choices(string.ascii_letters + string.digits + '!@#$%^&*', k=12))
                    user.set_password(password)
                    user.save()

                    # Asignar al grupo Ejecutivo
                    user.groups.add(grupo_ejecutivo)

                    self.stdout.write(f'✅ Creado: {nombre}')
                    self.stdout.write(f'   Usuario: {username}')
                    self.stdout.write(f'   Email: {email}')
                    self.stdout.write(f'   Contraseña: {password}\n')

                    creados += 1
                else:
                    # Si ya existe, asegurarse de que esté en el grupo
                    if grupo_ejecutivo not in user.groups.all():
                        user.groups.add(grupo_ejecutivo)
                        self.stdout.write(f'🔄 Actualizado (grupo añadido): {nombre}\n')
                        actualizados += 1
                    else:
                        self.stdout.write(f'ℹ️  Ya existe: {nombre}\n')

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error con {nombre}: {str(e)}\n'))
                errores += 1

        self.stdout.write('='*70)
        self.stdout.write(f'📊 Creados: {creados}')
        self.stdout.write(f'🔄 Actualizados: {actualizados}')
        self.stdout.write(f'❌ Errores: {errores}')
        self.stdout.write('='*70)
