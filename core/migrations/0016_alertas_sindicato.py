from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_add_fuente_metadata_movimiento_sindicato'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AlertaSindicato',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tipo_alerta', models.CharField(max_length=60, verbose_name='Tipo alerta')),
                ('categoria', models.CharField(choices=[('TELEFONIA', 'Telefonía'), ('IMPORTACION', 'Importación'), ('CONSOLIDADO', 'Consolidado'), ('MOVIMIENTO', 'Movimiento'), ('DATOS', 'Datos')], max_length=20, verbose_name='Categoría')),
                ('prioridad', models.CharField(choices=[('BAJA', 'Baja'), ('MEDIA', 'Media'), ('ALTA', 'Alta'), ('CRITICA', 'Crítica')], default='MEDIA', max_length=10, verbose_name='Prioridad')),
                ('titulo', models.CharField(max_length=180, verbose_name='Título')),
                ('descripcion', models.TextField(blank=True, default='', verbose_name='Descripción')),
                ('periodo', models.CharField(blank=True, max_length=7, null=True, verbose_name='Período')),
                ('fecha_referencia', models.DateField(blank=True, null=True, verbose_name='Fecha referencia')),
                ('fecha_alerta', models.DateTimeField(blank=True, null=True, verbose_name='Fecha alerta')),
                ('estado', models.CharField(choices=[('PENDIENTE', 'Pendiente'), ('EN_REVISION', 'En revisión'), ('RESUELTA', 'Resuelta'), ('DESCARTADA', 'Descartada')], default='PENDIENTE', max_length=15, verbose_name='Estado')),
                ('payload', models.JSONField(blank=True, default=dict, verbose_name='Payload')),
                ('clave_unica', models.CharField(max_length=120, verbose_name='Clave única')),
                ('fecha_resolucion', models.DateTimeField(blank=True, null=True, verbose_name='Fecha resolución')),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alertas_sindicato', to='core.empresa', verbose_name='Empresa (tenant)')),
                ('movimiento', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alertas_sindicato', to='core.movimientosindicato', verbose_name='Movimiento')),
                ('resuelta_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alertas_sindicato_resueltas', to=settings.AUTH_USER_MODEL, verbose_name='Resuelta por')),
                ('socio', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alertas_sindicato', to='core.sociosindicato', verbose_name='Socio')),
            ],
            options={
                'verbose_name': 'Alerta Sindicato',
                'verbose_name_plural': 'Alertas Sindicato',
                'ordering': ['-prioridad', '-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='alertasindicato',
            constraint=models.UniqueConstraint(fields=('empresa', 'clave_unica'), name='uniq_alerta_sind_empresa_clave'),
        ),
        migrations.AddIndex(
            model_name='alertasindicato',
            index=models.Index(fields=['empresa', 'estado'], name='core_alerta_empresa_aaf1ec_idx'),
        ),
        migrations.AddIndex(
            model_name='alertasindicato',
            index=models.Index(fields=['empresa', 'categoria'], name='core_alerta_empresa_9f5f4f_idx'),
        ),
        migrations.AddIndex(
            model_name='alertasindicato',
            index=models.Index(fields=['empresa', 'prioridad'], name='core_alerta_empresa_4d0ec7_idx'),
        ),
        migrations.AddIndex(
            model_name='alertasindicato',
            index=models.Index(fields=['empresa', 'periodo'], name='core_alerta_empresa_843d83_idx'),
        ),
        migrations.AddIndex(
            model_name='alertasindicato',
            index=models.Index(fields=['empresa', 'fecha_referencia'], name='core_alerta_empresa_4f8214_idx'),
        ),
    ]
