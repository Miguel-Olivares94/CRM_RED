from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.forms import MovimientoSindicatoForm, SocioSindicatoForm, TipoBeneficioSindicatoForm
from core.models import Empresa, MovimientoSindicato, SocioSindicato, TipoBeneficioSindicato, UserProfile


User = get_user_model()


class SocioSindicatoFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa_a = Empresa.objects.create(nombre='Empresa A', tipo='CLIENTE')
        cls.empresa_b = Empresa.objects.create(nombre='Empresa B', tipo='CLIENTE')

    def test_rut_valido(self):
        form = SocioSindicatoForm(
            data={
                'rut': '12.345.678-5',
                'nombre': 'Socio Válido',
                'site': 'Pudahuel',
                'estado_laboral': SocioSindicato.ESTADO_LABORAL_ACTIVO,
                'fecha_ingreso': '2026-01-01',
                'estado': SocioSindicato.ESTADO_ACTIVO,
            },
            empresa=self.empresa_a,
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['rut'], '12345678-5')

    def test_rut_invalido(self):
        form = SocioSindicatoForm(
            data={
                'rut': '12.345.678-9',
                'nombre': 'Socio Inválido',
                'estado_laboral': SocioSindicato.ESTADO_LABORAL_ACTIVO,
                'estado': SocioSindicato.ESTADO_ACTIVO,
            },
            empresa=self.empresa_a,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('rut', form.errors)

    def test_rut_duplicado_misma_empresa(self):
        SocioSindicato.objects.create(
            empresa=self.empresa_a,
            rut='12345678-5',
            nombre='Existente',
        )
        form = SocioSindicatoForm(
            data={
                'rut': '12.345.678-5',
                'nombre': 'Duplicado',
                'estado_laboral': SocioSindicato.ESTADO_LABORAL_ACTIVO,
                'estado': SocioSindicato.ESTADO_ACTIVO,
            },
            empresa=self.empresa_a,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('rut', form.errors)

    def test_mismo_rut_permitido_en_empresa_distinta(self):
        SocioSindicato.objects.create(
            empresa=self.empresa_a,
            rut='12345678-5',
            nombre='Socio A',
        )
        form = SocioSindicatoForm(
            data={
                'rut': '12.345.678-5',
                'nombre': 'Socio B',
                'estado_laboral': SocioSindicato.ESTADO_LABORAL_ACTIVO,
                'estado': SocioSindicato.ESTADO_ACTIVO,
            },
            empresa=self.empresa_b,
        )
        self.assertTrue(form.is_valid(), form.errors)


class TipoBeneficioSindicatoFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa_a = Empresa.objects.create(nombre='Empresa A', tipo='CLIENTE')
        cls.empresa_b = Empresa.objects.create(nombre='Empresa B', tipo='CLIENTE')

    def test_codigo_normalizado_y_unico_por_empresa(self):
        TipoBeneficioSindicato.objects.create(
            empresa=self.empresa_a,
            codigo='GAS',
            nombre='Gas',
        )
        form_dup = TipoBeneficioSindicatoForm(
            data={
                'codigo': ' gas ',
                'nombre': 'Gas 2',
                'orden_export': 1,
                'estado': TipoBeneficioSindicato.ESTADO_ACTIVO,
            },
            empresa=self.empresa_a,
        )
        self.assertFalse(form_dup.is_valid())
        self.assertIn('codigo', form_dup.errors)

        form_other = TipoBeneficioSindicatoForm(
            data={
                'codigo': ' gas ',
                'nombre': 'Gas Empresa B',
                'orden_export': 1,
                'estado': TipoBeneficioSindicato.ESTADO_INACTIVO,
            },
            empresa=self.empresa_b,
        )
        self.assertTrue(form_other.is_valid(), form_other.errors)
        self.assertEqual(form_other.cleaned_data['codigo'], 'GAS')

    def test_orden_export_valido(self):
        form = TipoBeneficioSindicatoForm(
            data={
                'codigo': 'TEL',
                'nombre': 'Telefonía',
                'orden_export': 0,
                'estado': TipoBeneficioSindicato.ESTADO_ACTIVO,
            },
            empresa=self.empresa_a,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('orden_export', form.errors)


class MovimientoSindicatoFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa_a = Empresa.objects.create(nombre='Empresa A', tipo='CLIENTE')
        cls.empresa_b = Empresa.objects.create(nombre='Empresa B', tipo='CLIENTE')

        cls.user_a = User.objects.create_user(
            username='tesoreria.a@empresa-a.cl',
            email='tesoreria.a@empresa-a.cl',
            password='x',
        )
        UserProfile.objects.create(user=cls.user_a, empresa=cls.empresa_a, role='ADMIN')

        cls.socio_a = SocioSindicato.objects.create(
            empresa=cls.empresa_a,
            rut='11111111-1',
            nombre='Socio A',
        )
        cls.socio_b = SocioSindicato.objects.create(
            empresa=cls.empresa_b,
            rut='22222222-2',
            nombre='Socio B',
        )

        cls.benef_a = TipoBeneficioSindicato.objects.create(
            empresa=cls.empresa_a,
            codigo='GAS',
            nombre='Gas',
            estado=TipoBeneficioSindicato.ESTADO_ACTIVO,
        )
        cls.benef_b = TipoBeneficioSindicato.objects.create(
            empresa=cls.empresa_b,
            codigo='TEL',
            nombre='Telefonía',
            estado=TipoBeneficioSindicato.ESTADO_ACTIVO,
        )
        cls.benef_inactivo_a = TipoBeneficioSindicato.objects.create(
            empresa=cls.empresa_a,
            codigo='COP',
            nombre='Copeuch',
            estado=TipoBeneficioSindicato.ESTADO_INACTIVO,
        )

    def test_rechaza_socio_de_otra_empresa(self):
        form = MovimientoSindicatoForm(
            data={
                'socio': self.socio_b.id,
                'tipo_beneficio': self.benef_a.id,
                'periodo': '2026-06',
                'monto': '10000',
                'estado': MovimientoSindicato.ESTADO_PENDIENTE,
                'observacion': '',
                'referencia_externa': 'A-1',
            },
            user=self.user_a,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('socio', form.errors)

    def test_rechaza_beneficio_de_otra_empresa(self):
        form = MovimientoSindicatoForm(
            data={
                'socio': self.socio_a.id,
                'tipo_beneficio': self.benef_b.id,
                'periodo': '2026-06',
                'monto': '10000',
                'estado': MovimientoSindicato.ESTADO_PENDIENTE,
                'observacion': '',
                'referencia_externa': 'A-2',
            },
            user=self.user_a,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('tipo_beneficio', form.errors)

    def test_rechaza_monto_cero(self):
        form = MovimientoSindicatoForm(
            data={
                'socio': self.socio_a.id,
                'tipo_beneficio': self.benef_a.id,
                'periodo': '2026-06',
                'monto': '0',
                'estado': MovimientoSindicato.ESTADO_PENDIENTE,
                'observacion': '',
                'referencia_externa': 'A-3',
            },
            user=self.user_a,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('monto', form.errors)

    def test_rechaza_beneficio_inactivo(self):
        form = MovimientoSindicatoForm(
            data={
                'socio': self.socio_a.id,
                'tipo_beneficio': self.benef_inactivo_a.id,
                'periodo': '2026-06',
                'monto': '10000',
                'estado': MovimientoSindicato.ESTADO_PENDIENTE,
                'observacion': '',
                'referencia_externa': 'A-4',
            },
            user=self.user_a,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('tipo_beneficio', form.errors)

    def test_duplicado_con_referencia_externa_se_rechaza(self):
        MovimientoSindicato.objects.create(
            empresa=self.empresa_a,
            socio=self.socio_a,
            tipo_beneficio=self.benef_a,
            periodo='2026-06',
            monto=Decimal('10000'),
            referencia_externa='REF-1',
        )
        form = MovimientoSindicatoForm(
            data={
                'socio': self.socio_a.id,
                'tipo_beneficio': self.benef_a.id,
                'periodo': '2026-06',
                'monto': '10000',
                'estado': MovimientoSindicato.ESTADO_PENDIENTE,
                'observacion': '',
                'referencia_externa': 'REF-1',
            },
            user=self.user_a,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('referencia_externa', form.errors)

    def test_posible_duplicado_sin_referencia_se_advierte_pero_no_bloquea(self):
        MovimientoSindicato.objects.create(
            empresa=self.empresa_a,
            socio=self.socio_a,
            tipo_beneficio=self.benef_a,
            periodo='2026-07',
            monto=Decimal('15000'),
            referencia_externa='',
        )
        form = MovimientoSindicatoForm(
            data={
                'socio': self.socio_a.id,
                'tipo_beneficio': self.benef_a.id,
                'periodo': '2026-07',
                'monto': '15000',
                'estado': MovimientoSindicato.ESTADO_PENDIENTE,
                'observacion': '',
                'referencia_externa': '',
            },
            user=self.user_a,
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertGreaterEqual(len(form.warnings), 1)
        self.assertTrue(form.cleaned_data['referencia_externa'].startswith('AUTO-'))
