from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.test import TestCase

from core.models import (
    AuditoriaSindicato,
    ConsolidadoDetalleSindicato,
    ConsolidadoMensualSindicato,
    Empresa,
    MovimientoSindicato,
    SocioSindicato,
    TipoBeneficioSindicato,
)


User = get_user_model()


class SocioSindicatoModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa_a = Empresa.objects.create(nombre='Empresa A', tipo='CLIENTE')
        cls.empresa_b = Empresa.objects.create(nombre='Empresa B', tipo='CLIENTE')

    def test_crear_socio_con_empresa_obligatoria(self):
        socio = SocioSindicato.objects.create(
            empresa=self.empresa_a,
            rut='12345678-9',
            nombre='Socio Uno',
            estado_laboral=SocioSindicato.ESTADO_LABORAL_ACTIVO,
            estado=SocioSindicato.ESTADO_ACTIVO,
        )
        self.assertEqual(socio.empresa, self.empresa_a)

    def test_socio_falla_sin_empresa(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SocioSindicato.objects.create(
                    empresa=None,
                    rut='12312312-3',
                    nombre='Sin Empresa',
                )

    def test_unicidad_rut_por_empresa(self):
        SocioSindicato.objects.create(
            empresa=self.empresa_a,
            rut='11111111-1',
            nombre='Socio A1',
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SocioSindicato.objects.create(
                    empresa=self.empresa_a,
                    rut='11111111-1',
                    nombre='Socio A2',
                )

    def test_mismo_rut_permitido_en_empresas_distintas(self):
        SocioSindicato.objects.create(
            empresa=self.empresa_a,
            rut='22222222-2',
            nombre='Socio A',
        )
        socio_b = SocioSindicato.objects.create(
            empresa=self.empresa_b,
            rut='22222222-2',
            nombre='Socio B',
        )
        self.assertEqual(socio_b.rut, '22222222-2')

    def test_validar_estado_laboral(self):
        socio = SocioSindicato(
            empresa=self.empresa_a,
            rut='33333333-3',
            nombre='Socio Estado',
            estado_laboral='ESTADO_INVALIDO',
            estado=SocioSindicato.ESTADO_ACTIVO,
        )
        with self.assertRaises(ValidationError):
            socio.full_clean()


class TipoBeneficioSindicatoModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa_a = Empresa.objects.create(nombre='Empresa A', tipo='CLIENTE')
        cls.empresa_b = Empresa.objects.create(nombre='Empresa B', tipo='CLIENTE')

    def test_crear_beneficio_con_empresa_obligatoria(self):
        beneficio = TipoBeneficioSindicato.objects.create(
            empresa=self.empresa_a,
            codigo='GAS',
            nombre='Gas',
            estado=TipoBeneficioSindicato.ESTADO_ACTIVO,
        )
        self.assertEqual(beneficio.empresa, self.empresa_a)

    def test_beneficio_falla_sin_empresa(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                TipoBeneficioSindicato.objects.create(
                    empresa=None,
                    codigo='SINEMP',
                    nombre='Beneficio sin empresa',
                )

    def test_unicidad_codigo_por_empresa(self):
        TipoBeneficioSindicato.objects.create(
            empresa=self.empresa_a,
            codigo='TEL',
            nombre='Telefonia',
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                TipoBeneficioSindicato.objects.create(
                    empresa=self.empresa_a,
                    codigo='TEL',
                    nombre='Telefonia 2',
                )

    def test_mismo_codigo_permitido_en_empresas_distintas(self):
        TipoBeneficioSindicato.objects.create(
            empresa=self.empresa_a,
            codigo='COP',
            nombre='Copeuch',
        )
        beneficio_b = TipoBeneficioSindicato.objects.create(
            empresa=self.empresa_b,
            codigo='COP',
            nombre='Copeuch',
        )
        self.assertEqual(beneficio_b.codigo, 'COP')

    def test_estado_activo_inactivo(self):
        activo = TipoBeneficioSindicato.objects.create(
            empresa=self.empresa_a,
            codigo='OPT',
            nombre='Optica',
            estado=TipoBeneficioSindicato.ESTADO_ACTIVO,
        )
        inactivo = TipoBeneficioSindicato.objects.create(
            empresa=self.empresa_a,
            codigo='VET',
            nombre='Veterinaria',
            estado=TipoBeneficioSindicato.ESTADO_INACTIVO,
        )
        self.assertEqual(activo.estado, TipoBeneficioSindicato.ESTADO_ACTIVO)
        self.assertEqual(inactivo.estado, TipoBeneficioSindicato.ESTADO_INACTIVO)


class MovimientoSindicatoModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa = Empresa.objects.create(nombre='Empresa A', tipo='CLIENTE')
        cls.socio = SocioSindicato.objects.create(
            empresa=cls.empresa,
            rut='44444444-4',
            nombre='Socio Movimiento',
        )
        cls.beneficio = TipoBeneficioSindicato.objects.create(
            empresa=cls.empresa,
            codigo='GAS',
            nombre='Gas',
        )

    def test_crear_movimiento_misma_empresa(self):
        mov = MovimientoSindicato.objects.create(
            empresa=self.empresa,
            socio=self.socio,
            tipo_beneficio=self.beneficio,
            periodo='2026-06',
            monto=Decimal('30000'),
            referencia_externa='FOLIO-1',
        )
        self.assertEqual(mov.empresa_id, self.socio.empresa_id)
        self.assertEqual(mov.empresa_id, self.beneficio.empresa_id)

    def test_validar_monto_mayor_a_cero(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                MovimientoSindicato.objects.create(
                    empresa=self.empresa,
                    socio=self.socio,
                    tipo_beneficio=self.beneficio,
                    periodo='2026-06',
                    monto=Decimal('0'),
                    referencia_externa='FOLIO-2',
                )

    def test_validar_periodo_obligatorio(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                MovimientoSindicato.objects.create(
                    empresa=self.empresa,
                    socio=self.socio,
                    tipo_beneficio=self.beneficio,
                    periodo=None,
                    monto=Decimal('20000'),
                    referencia_externa='FOLIO-3',
                )

    def test_validar_duplicado_por_constraint_actual(self):
        MovimientoSindicato.objects.create(
            empresa=self.empresa,
            socio=self.socio,
            tipo_beneficio=self.beneficio,
            periodo='2026-07',
            monto=Decimal('25000'),
            referencia_externa='FOLIO-4',
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                MovimientoSindicato.objects.create(
                    empresa=self.empresa,
                    socio=self.socio,
                    tipo_beneficio=self.beneficio,
                    periodo='2026-07',
                    monto=Decimal('25000'),
                    referencia_externa='FOLIO-4',
                )


class ConsolidadoSindicatoModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa = Empresa.objects.create(nombre='Empresa A', tipo='CLIENTE')
        cls.socio = SocioSindicato.objects.create(
            empresa=cls.empresa,
            rut='55555555-5',
            nombre='Socio Consolidado',
        )
        cls.beneficio = TipoBeneficioSindicato.objects.create(
            empresa=cls.empresa,
            codigo='TEL',
            nombre='Telefonia',
        )

    def test_crear_consolidado_por_empresa_y_periodo(self):
        consolidado = ConsolidadoMensualSindicato.objects.create(
            empresa=self.empresa,
            periodo='2026-06',
        )
        self.assertEqual(consolidado.periodo, '2026-06')

    def test_no_duplicar_periodo_misma_empresa(self):
        ConsolidadoMensualSindicato.objects.create(empresa=self.empresa, periodo='2026-08')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ConsolidadoMensualSindicato.objects.create(empresa=self.empresa, periodo='2026-08')

    def test_crear_detalle_y_validar_totales_basicos(self):
        consolidado = ConsolidadoMensualSindicato.objects.create(
            empresa=self.empresa,
            periodo='2026-09',
        )
        ConsolidadoDetalleSindicato.objects.create(
            empresa=self.empresa,
            consolidado=consolidado,
            socio=self.socio,
            tipo_beneficio=self.beneficio,
            monto_aprobado=Decimal('15000'),
        )
        total = ConsolidadoDetalleSindicato.objects.filter(consolidado=consolidado).aggregate(
            total=Sum('monto_aprobado')
        )['total']
        self.assertEqual(total, Decimal('15000'))


class AuditoriaSindicatoModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa = Empresa.objects.create(nombre='Empresa A', tipo='CLIENTE')
        cls.user = User.objects.create_user(
            username='auditoria@empresa-a.cl',
            email='auditoria@empresa-a.cl',
            password='x',
        )

    def test_crear_auditoria_asociada_a_empresa(self):
        audit = AuditoriaSindicato.objects.create(
            empresa=self.empresa,
            usuario=self.user,
            accion='CREAR',
            entidad='MovimientoSindicato',
            entidad_id='123',
            resumen='Movimiento creado correctamente',
            payload={'monto': 10000},
        )
        self.assertEqual(audit.empresa, self.empresa)
        self.assertEqual(audit.usuario, self.user)


class AislamientoMultiempresaSindicatoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa_a = Empresa.objects.create(nombre='Empresa A', tipo='CLIENTE')
        cls.empresa_b = Empresa.objects.create(nombre='Empresa B', tipo='CLIENTE')

        cls.socio_a = SocioSindicato.objects.create(
            empresa=cls.empresa_a,
            rut='66666666-6',
            nombre='Socio A',
        )
        cls.socio_b = SocioSindicato.objects.create(
            empresa=cls.empresa_b,
            rut='77777777-7',
            nombre='Socio B',
        )

        cls.beneficio_a = TipoBeneficioSindicato.objects.create(
            empresa=cls.empresa_a,
            codigo='GAS',
            nombre='Gas',
        )
        cls.beneficio_b = TipoBeneficioSindicato.objects.create(
            empresa=cls.empresa_b,
            codigo='GAS',
            nombre='Gas',
        )

        MovimientoSindicato.objects.create(
            empresa=cls.empresa_a,
            socio=cls.socio_a,
            tipo_beneficio=cls.beneficio_a,
            periodo='2026-10',
            monto=Decimal('30000'),
            referencia_externa='A-1',
        )
        MovimientoSindicato.objects.create(
            empresa=cls.empresa_b,
            socio=cls.socio_b,
            tipo_beneficio=cls.beneficio_b,
            periodo='2026-10',
            monto=Decimal('45000'),
            referencia_externa='B-1',
        )

    def test_consultas_filtradas_por_empresa_no_mezclan_datos(self):
        socios_a = list(SocioSindicato.objects.filter(empresa=self.empresa_a))
        socios_b = list(SocioSindicato.objects.filter(empresa=self.empresa_b))

        movs_a = list(MovimientoSindicato.objects.filter(empresa=self.empresa_a))
        movs_b = list(MovimientoSindicato.objects.filter(empresa=self.empresa_b))

        self.assertEqual(socios_a, [self.socio_a])
        self.assertEqual(socios_b, [self.socio_b])
        self.assertEqual(len(movs_a), 1)
        self.assertEqual(len(movs_b), 1)
        self.assertEqual(movs_a[0].socio, self.socio_a)
        self.assertEqual(movs_b[0].socio, self.socio_b)
