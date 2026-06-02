"""
Configuración de Celery para el proyecto CRM.

Este módulo configura Celery para ejecutar tareas automáticas de forma asincrónica.
Requiere Redis corriendo en localhost:6379 (o configurar CELERY_BROKER_URL)
"""

import os
from celery import Celery
from celery.schedules import crontab


# Configurar Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Crear instancia Celery
app = Celery('crm_starter')

# Cargar configuración de Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks desde todas las apps
app.autodiscover_tasks()


# Configuración de Beat (tareas programadas)
app.conf.beat_schedule = {
    # Actualizar estados de alertas diariamente a las 08:00
    'actualizar-estados-cada-8-horas': {
        'task': 'core.actualizar_estados_oportunidades',
        'schedule': crontab(hour='*/8'),  # Cada 8 horas
        'options': {'queue': 'default'}
    },
    # Generar alertas de vencidas diariamente a las 09:00
    'generar-alertas-vencidas-diario': {
        'task': 'core.generar_alertas_vencidas',
        'schedule': crontab(hour=9, minute=0),  # Cada día a las 09:00
        'options': {'queue': 'default'}
    },
    # Calcular comisiones el primer día del mes a las 10:00
    'calcular-comisiones-mensual': {
        'task': 'core.calcular_comisiones',
        'schedule': crontab(day_of_month=1, hour=10, minute=0),  # Primer día del mes a las 10:00
        'options': {'queue': 'default'}
    },
    # Enviar resumen diario a las 17:00
    'enviar-resumen-diario': {
        'task': 'core.enviar_resumen_diario',
        'schedule': crontab(hour=17, minute=0),  # Cada día a las 17:00
        'options': {'queue': 'default'}
    }
}


@app.task(bind=True)
def debug_task(self):
    """Tarea de prueba para verificar que Celery está funcionando"""
    print(f'Request: {self.request!r}')
