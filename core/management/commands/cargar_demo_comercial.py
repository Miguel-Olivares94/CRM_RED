"""
Management command para cargar datos demo listos para presentación comercial.

Crea:
- 1 MetaVentas configurada con metas, comisión base y acelerador
- 2 Comisiones: una CALCULADA y una APROBADA
- 3 Seguimientos de alerta (simulando detección automática de inactividad)
- 1 Oportunidad adicional en riesgo (si no existe ya)

Uso:
    python manage.py cargar_demo_comercial
    python manage.py cargar_demo_comercial --reset  (elimina datos demo previos)
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Carga datos demo para presentaciones comerciales'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina datos demo previos antes de crear nuevos',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\n' + '='*60))
        self.stdout.write(self.style.MIGRATE_HEADING('  CARGANDO DATOS DEMO COMERCIAL'))
        self.stdout.write(self.style.MIGRATE_HEADING('='*60 + '\n'))

        # Obtener usuario admin
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stderr.write(self.style.ERROR('No hay usuario superadmin. Créalo primero.'))
            return

        # Obtener otros usuarios para demo
        vendedor = User.objects.exclude(is_superuser=True).first()
        if not vendedor:
            vendedor = admin_user

        if options['reset']:
            self._reset_demo_data()

        self._crear_meta_ventas(admin_user, vendedor)
        self._crear_comisiones(admin_user, vendedor)
        self._crear_seguimientos_demo(admin_user, vendedor)
        self._crear_oportunidad_en_riesgo(admin_user, vendedor)

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('  DEMO LISTA — El sistema está preparado para presentar'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write('')
        self.stdout.write('  Navega a:')
        self.stdout.write('  → /metas/          — Metas de Ventas configuradas')
        self.stdout.write('  → /comisiones/      — Comisiones calculadas y aprobadas')
        self.stdout.write('  → /seguimientos/    — Alertas automáticas de inactividad')
        self.stdout.write('  → /oportunidades/   — Pipeline con oportunidades en riesgo')
        self.stdout.write('')

    def _reset_demo_data(self):
        from core.models import MetaVentas, Comision, Seguimiento
        MetaVentas.objects.filter(periodo__startswith='DEMO-').delete()
        Comision.objects.filter(periodo__startswith='DEMO-').delete()
        Seguimiento.objects.filter(descripcion__startswith='[DEMO]').delete()
        self.stdout.write(self.style.WARNING('  → Datos demo previos eliminados'))

    def _crear_meta_ventas(self, admin_user, vendedor):
        from core.models import MetaVentas

        periodo_actual = date.today().strftime('%Y-%m')
        periodo_anterior = (date.today().replace(day=1) - timedelta(days=1)).strftime('%Y-%m')

        metas_creadas = 0

        # Meta período actual - vendedor principal
        meta, created = MetaVentas.objects.get_or_create(
            usuario=vendedor,
            periodo=periodo_actual,
            defaults={
                'meta_lineas_portabilidad': 20,
                'meta_lineas_nueva': 15,
                'meta_lineas_m2m': 10,
                'meta_monto_total': Decimal('8500000'),
                'comision_base': Decimal('350000'),
                'comision_por_linea': Decimal('12000'),
                'factor_aceleracion': Decimal('1.30'),
                'bonificacion_meta': Decimal('200000'),
            }
        )
        if created:
            metas_creadas += 1
            self.stdout.write(self.style.SUCCESS(f'  ✓ Meta {periodo_actual} creada para {vendedor.email}'))
        else:
            self.stdout.write(f'  · Meta {periodo_actual} ya existía para {vendedor.email}')

        # Meta período anterior - admin (para mostrar historial)
        meta_ant, created_ant = MetaVentas.objects.get_or_create(
            usuario=admin_user,
            periodo=periodo_anterior,
            defaults={
                'meta_lineas_portabilidad': 25,
                'meta_lineas_nueva': 20,
                'meta_lineas_m2m': 12,
                'meta_monto_total': Decimal('10000000'),
                'comision_base': Decimal('420000'),
                'comision_por_linea': Decimal('12000'),
                'factor_aceleracion': Decimal('1.50'),
                'bonificacion_meta': Decimal('300000'),
            }
        )
        if created_ant:
            metas_creadas += 1
            self.stdout.write(self.style.SUCCESS(f'  ✓ Meta {periodo_anterior} creada para {admin_user.email}'))

        self.stdout.write(f'  → {metas_creadas} metas de ventas creadas\n')

    def _crear_comisiones(self, admin_user, vendedor):
        from core.models import Comision, MetaVentas

        periodo_actual = date.today().strftime('%Y-%m')
        periodo_anterior = (date.today().replace(day=1) - timedelta(days=1)).strftime('%Y-%m')

        comisiones_creadas = 0

        # Comisión CALCULADA (mes actual - vendedor)
        meta_actual = MetaVentas.objects.filter(usuario=vendedor, periodo=periodo_actual).first()
        comision1, created1 = Comision.objects.get_or_create(
            usuario=vendedor,
            periodo=periodo_actual,
            defaults={
                'meta': meta_actual,
                'lineas_portabilidad_vendidas': 14,
                'lineas_nueva_vendidas': 9,
                'lineas_m2m_vendidas': 6,
                'monto_total_vendido': Decimal('5200000'),
                'comision_calculada': Decimal('581000'),
                'bonificacion_aplicada': Decimal('0'),
                'total_a_pagar': Decimal('581000'),
                'fecha_calculo': timezone.now(),
                'estado': 'CALCULADA',
            }
        )
        if created1:
            comisiones_creadas += 1
            self.stdout.write(self.style.SUCCESS(f'  ✓ Comisión CALCULADA ({periodo_actual}) — ${581000:,} — {vendedor.email}'))

        # Comisión APROBADA (mes anterior - admin, sobre meta alcanzada)
        meta_anterior = MetaVentas.objects.filter(usuario=admin_user, periodo=periodo_anterior).first()
        comision2, created2 = Comision.objects.get_or_create(
            usuario=admin_user,
            periodo=periodo_anterior,
            defaults={
                'meta': meta_anterior,
                'lineas_portabilidad_vendidas': 27,
                'lineas_nueva_vendidas': 22,
                'lineas_m2m_vendidas': 14,
                'monto_total_vendido': Decimal('11300000'),
                'comision_calculada': Decimal('852000'),
                'bonificacion_aplicada': Decimal('300000'),
                'total_a_pagar': Decimal('1152000'),
                'fecha_calculo': timezone.now() - timedelta(days=30),
                'estado': 'APROBADA',
            }
        )
        if created2:
            comisiones_creadas += 1
            self.stdout.write(self.style.SUCCESS(f'  ✓ Comisión APROBADA ({periodo_anterior}) — ${1152000:,} — {admin_user.email} (meta superada + bono)'))

        self.stdout.write(f'  → {comisiones_creadas} comisiones creadas\n')

    def _crear_seguimientos_demo(self, admin_user, vendedor):
        from core.models import Seguimiento, Oportunidad

        # Necesitamos oportunidades para asignar seguimientos
        oportunidades = Oportunidad.objects.filter(estado='ABIERTA').order_by('?')[:3]
        if not oportunidades:
            self.stdout.write(self.style.WARNING('  ! Sin oportunidades abiertas para seguimientos. Se crearán al crear oportunidades demo.'))
            return

        creados = 0
        alertas_config = [
            {
                'tipo': 'ALERTA',
                'prioridad': 'CRITICA',
                'estado': 'PENDIENTE',
                'descripcion': '[DEMO] Alerta automática: 47 días sin contacto. Cliente en riesgo CRÍTICO de abandono. Requiere acción inmediata.',
                'dias_vencimiento': -3,  # vencido hace 3 días
            },
            {
                'tipo': 'ALERTA',
                'prioridad': 'ALTA',
                'estado': 'PENDIENTE',
                'descripcion': '[DEMO] Alerta automática: 31 días sin contacto. Oportunidad clasificada como RIESGO ALTO. Contactar esta semana.',
                'dias_vencimiento': 1,
            },
            {
                'tipo': 'RECORDATORIO',
                'prioridad': 'MEDIA',
                'estado': 'PENDIENTE',
                'descripcion': '[DEMO] Alerta automática: 16 días sin contacto. Oportunidad EN RIESGO. Agendar llamada de seguimiento.',
                'dias_vencimiento': 3,
            },
        ]

        for i, (oportunidad, config) in enumerate(zip(oportunidades, alertas_config)):
            # Evitar duplicar
            if Seguimiento.objects.filter(oportunidad=oportunidad, descripcion=config['descripcion']).exists():
                continue

            Seguimiento.objects.create(
                oportunidad=oportunidad,
                tipo=config['tipo'],
                prioridad=config['prioridad'],
                estado=config['estado'],
                descripcion=config['descripcion'],
                fecha_vencimiento=date.today() + timedelta(days=config['dias_vencimiento']),
                asignado_a=vendedor,
                creado_por=admin_user,
            )
            creados += 1
            icono = '🔴' if config['prioridad'] == 'CRITICA' else '🟠' if config['prioridad'] == 'ALTA' else '🟡'
            self.stdout.write(self.style.SUCCESS(
                f'  ✓ Seguimiento {config["prioridad"]} — {oportunidad.cliente.nombre_empresa[:40]}'
            ))

        self.stdout.write(f'  → {creados} seguimientos de alerta demo creados\n')

    def _crear_oportunidad_en_riesgo(self, admin_user, vendedor):
        from core.models import Oportunidad, Cliente

        # Buscar un cliente existente que no tenga oportunidad abierta
        cliente_sin_oportunidad = Cliente.objects.filter(
            estado__in=['ACTIVO', 'PROSPECT']
        ).exclude(
            oportunidades__estado='ABIERTA'
        ).order_by('?').first()

        if not cliente_sin_oportunidad:
            self.stdout.write('  · Todos los clientes ya tienen oportunidades. Usando cliente existente.')
            cliente_sin_oportunidad = Cliente.objects.order_by('?').first()

        if not cliente_sin_oportunidad:
            self.stdout.write(self.style.WARNING('  ! Sin clientes para crear oportunidad demo.'))
            return

        # Crear oportunidad con último contacto hace 35 días (RIESGO_ALTO)
        oportunidad, created = Oportunidad.objects.get_or_create(
            cliente=cliente_sin_oportunidad,
            usuario=vendedor,
            estado='ABIERTA',
            defaults={
                'monto': Decimal('4500000'),
                'moneda': 'CLP',
                'etapa': 'PROPUESTA',
                'probabilidad': 60,
                'productos': 'Pack Corporativo + BAM',
                'lineas': 18,
                'fecha_ultimo_contacto': timezone.now() - timedelta(days=35),
                'fecha_cierre_estimada': date.today() + timedelta(days=30),
                'observaciones': '[DEMO] Propuesta enviada. Sin respuesta hace 35 días. Requiere seguimiento urgente.',
                'creado_por': admin_user,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(
                f'  ✓ Oportunidad EN RIESGO creada — {cliente_sin_oportunidad.nombre_empresa[:40]} — $4.500.000'
            ))
            self.stdout.write(self.style.SUCCESS(
                f'    → Último contacto: hace 35 días (se mostrará como RIESGO_ALTO en la demo)'
            ))

            # Crear seguimiento crítico para esta oportunidad
            Seguimiento.objects.create(
                oportunidad=oportunidad,
                tipo='ALERTA',
                prioridad='ALTA',
                estado='PENDIENTE',
                descripcion='[DEMO] Alerta automática: 35 días sin contacto. Propuesta enviada sin respuesta. Riesgo de perder la oportunidad.',
                fecha_vencimiento=date.today(),
                asignado_a=vendedor,
                creado_por=admin_user,
            )
        else:
            self.stdout.write(f'  · Oportunidad demo ya existía para {cliente_sin_oportunidad.nombre_empresa[:40]}')

        self.stdout.write('')
