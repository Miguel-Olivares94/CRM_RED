# Generated migration for UserProfile model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0004_alter_llamada_options_cliente_bam_cliente_dv_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('role', models.CharField(
                    choices=[
                        ('ADMIN', 'Administrador General'),
                        ('MANAGER', 'Gerente de Ventas'),
                        ('EJECUTIVO', 'Ejecutivo'),
                        ('OTRO', 'Otro')
                    ],
                    default='EJECUTIVO',
                    max_length=20,
                    verbose_name='Rol'
                )),
                ('supervisor', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='subordinados',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Supervisor'
                )),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='profile',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Usuario'
                )),
            ],
            options={
                'verbose_name': 'Perfil de Usuario',
                'verbose_name_plural': 'Perfiles de Usuarios',
            },
        ),
    ]
