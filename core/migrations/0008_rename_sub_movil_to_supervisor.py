from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_add_origen_creado_por_cliente'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cliente',
            old_name='sub_movil',
            new_name='supervisor',
        ),
    ]
