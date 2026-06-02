"""
Comando para importar clientes desde archivo Excel o CSV.

Uso:
  python manage.py import_clientes archivo.xlsx --sheet="Clientes"
  python manage.py import_clientes archivo.csv
  python manage.py import_clientes archivo.xlsx --dry-run  # Vista previa sin guardar
"""

import pandas as pd
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Cliente

User = get_user_model()


class Command(BaseCommand):
    help = 'Importa clientes desde un archivo Excel o CSV'

    def add_arguments(self, parser):
        parser.add_argument('archivo', type=str, help='Ruta al archivo Excel o CSV')
        parser.add_argument(
            '--sheet',
            type=str,
            default='Clientes',
            help='Nombre de la hoja en el Excel (default: Clientes)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar vista previa sin guardar datos'
        )
        parser.add_argument(
            '--usuario',
            type=str,
            default='admin',
            help='Usuario por defecto para asignar clientes (default: admin)'
        )

    def handle(self, *args, **options):
        archivo = options['archivo']
        sheet_name = options['sheet']
        dry_run = options['dry_run']
        usuario_default = options['usuario']

        self.stdout.write(self.style.SUCCESS(f'\n=== Importador de Clientes ===\n'))
        self.stdout.write(f'Archivo: {archivo}')
        self.stdout.write(f'Hoja: {sheet_name}')
        self.stdout.write(f'Modo: {"VISTA PREVIA (DRY-RUN)" if dry_run else "GUARDAR"}')
        self.stdout.write()

        # Cargar el archivo
        try:
            if archivo.endswith('.xlsx') or archivo.endswith('.xls'):
                df = pd.read_excel(archivo, sheet_name=sheet_name)
            elif archivo.endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                self.stdout.write(self.style.ERROR('❌ Formato no soportado. Use .xlsx, .xls o .csv'))
                return

            self.stdout.write(f'✓ Archivo cargado: {len(df)} registros encontrados\n')

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'❌ Archivo no encontrado: {archivo}'))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error al leer archivo: {str(e)}'))
            return

        # Validar estructura del archivo
        columnas_requeridas = {'rut', 'nombre_empresa'}
        columnas_df = set(df.columns)
        columnas_faltantes = columnas_requeridas - columnas_df

        if columnas_faltantes:
            self.stdout.write(self.style.ERROR(
                f'❌ Faltan columnas requeridas: {", ".join(columnas_faltantes)}'
            ))
            self.stdout.write(f'Columnas disponibles: {", ".join(columnas_df)}')
            return

        # Obtener usuario por defecto
        try:
            usuario = User.objects.get(username=usuario_default)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Usuario no encontrado: {usuario_default}'))
            return

        # Procesar registros
        exitosos = 0
        errores = 0
        duplicados = 0

        self.stdout.write(self.style.SUCCESS('Procesando registros...'))
        self.stdout.write('-' * 80)

        # Mostrar columnas detectadas
        self.stdout.write(f'Columnas detectadas: {", ".join(columnas_df)}\n')

        for idx, (_, row) in enumerate(df.iterrows(), 1):
            try:
                rut = str(row['rut']).strip()
                nombre_empresa = str(row['nombre_empresa']).strip()

                # Campos opcionales
                sector = str(row.get('sector', '')).strip() if pd.notna(row.get('sector')) else ''
                tipo_cliente = str(row.get('tipo_cliente', '')).strip() if pd.notna(row.get('tipo_cliente')) else ''
                estado = str(row.get('estado', 'Activo')).strip() if pd.notna(row.get('estado')) else 'Activo'
                comuna = str(row.get('comuna', '')).strip() if pd.notna(row.get('comuna')) else ''
                provincia = str(row.get('provincia', '')).strip() if pd.notna(row.get('provincia')) else ''
                region = str(row.get('region', '')).strip() if pd.notna(row.get('region')) else ''
                observaciones = str(row.get('observaciones', '')).strip() if pd.notna(row.get('observaciones')) else ''

                # Validar datos requeridos
                if not rut or not nombre_empresa:
                    errores += 1
                    self.stdout.write(f'{idx}. ❌ RUT y nombre empresa son requeridos')
                    continue

                # Verificar duplicados
                if Cliente.objects.filter(rut=rut).exists():
                    duplicados += 1
                    self.stdout.write(self.style.WARNING(f'{idx}. ⚠ Duplicado: {rut} - {nombre_empresa}'))
                    continue

                # Preparar datos del cliente
                cliente_data = {
                    'rut': rut,
                    'nombre_empresa': nombre_empresa,
                    'sector': sector,
                    'tipo_cliente': tipo_cliente,
                    'estado': estado,
                    'comuna': comuna,
                    'provincia': provincia,
                    'region': region,
                    'observaciones': observaciones,
                    'usuario_asignado': usuario,
                }

                if not dry_run:
                    Cliente.objects.create(**cliente_data)
                
                exitosos += 1
                if idx % 100 == 0:
                    self.stdout.write(f'{idx}. ✓ {nombre_empresa}')

            except Exception as e:
                errores += 1
                self.stdout.write(self.style.ERROR(f'{idx}. ❌ Error: {str(e)}'))

        # Resumen
        self.stdout.write('-' * 80)
        self.stdout.write(self.style.SUCCESS(f'\n📊 RESUMEN DE IMPORTACIÓN:'))
        self.stdout.write(f'  Total procesados:  {len(df)}')
        self.stdout.write(self.style.SUCCESS(f'  ✓ Exitosos:        {exitosos}'))
        if duplicados > 0:
            self.stdout.write(self.style.WARNING(f'  ⚠ Duplicados:      {duplicados}'))
        if errores > 0:
            self.stdout.write(self.style.ERROR(f'  ❌ Errores:         {errores}'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f'\n⚠️  MODO DRY-RUN: Los datos NO fueron guardados'))
            self.stdout.write(f'Usa sin --dry-run para guardar: python manage.py import_clientes {archivo}')
        else:
            self.stdout.write(self.style.SUCCESS(f'\n✅ Importación completada exitosamente!'))

        self.stdout.write()
