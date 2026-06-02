"""
Resources de django-import-export para importación de datos en admin.
"""

from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from django.contrib.auth import get_user_model
from .models import Cliente, Oportunidad

User = get_user_model()


class ClienteResource(resources.ModelResource):
    """Resource para importar/exportar clientes.

    Usa RUT como identificador unico para evitar duplicados:
    - Si el RUT ya existe → ACTUALIZA el registro existente
    - Si el RUT es nuevo  → CREA un registro nuevo
    """

    usuario_asignado = fields.Field(
        column_name='usuario_asignado',
        attribute='usuario_asignado',
        widget=ForeignKeyWidget(User, field='username')
    )

    class Meta:
        model = Cliente
        import_id_fields = ['rut']  # RUT es el identificador único
        fields = (
            'rut', 'nombre_empresa', 'sector', 'tipo_cliente',
            'estado', 'usuario_asignado', 'comuna', 'provincia', 'region',
            'observaciones', 'fecha_registro',
            'dv', 'segmento', 'subrango', 'supervisor', 'subgerencia',
            'renta_uf_total', 'q_total_lineas', 'bam', 'm2m', 'voz',
            'fijo', 'movil', 'fijo_movil', 'edv'
        )
        export_order = fields
        skip_unchanged = True
        report_skipped = True

    def before_import_row(self, row, **kwargs):
        """Limpia y valida cada fila antes de importar"""
        # Limpiar espacios en blanco
        for key in list(row.keys()):
            if isinstance(row[key], str):
                row[key] = row[key].strip()

        # Limpiar RUT: quitar puntos y dejar guion
        if row.get('rut'):
            rut = str(row['rut']).strip().replace('.', '').replace(' ', '')
            row['rut'] = rut

        # Asignar usuario admin si no se especifica
        if not row.get('usuario_asignado'):
            try:
                row['usuario_asignado'] = User.objects.filter(
                    is_superuser=True
                ).first().username
            except Exception:
                pass

    def skip_row(self, instance, original, row, import_validation_errors=None):
        """No importar si el RUT está vacío"""
        if not row.get('rut'):
            return True
        return super().skip_row(instance, original, row, import_validation_errors)


class OportunidadResource(resources.ModelResource):
    """Resource para importar/exportar oportunidades"""
    
    cliente = fields.Field(
        column_name='cliente',
        attribute='cliente',
        widget=ForeignKeyWidget(Cliente, field='nombre_empresa')
    )
    usuario = fields.Field(
        column_name='usuario',
        attribute='usuario',
        widget=ForeignKeyWidget(User, field='username')
    )

    class Meta:
        model = Oportunidad
        fields = (
            'id', 'cliente', 'usuario', 'etapa', 'probabilidad',
            'monto', 'moneda', 'estado', 'productos', 'lineas',
            'fecha_cierre_estimada', 'proximo_contacto', 'observaciones'
        )
        export_order = fields
        skip_unchanged = True
        report_skipped = True
