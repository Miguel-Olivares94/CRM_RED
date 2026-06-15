from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import (
    AlertaSindicato,
    ConsolidadoMensualSindicato,
    Empresa,
    MovimientoSindicato,
    SocioSindicato,
    TipoBeneficioSindicato,
    UserProfile,
)
from core.services.sindicato_alertas import (
    generar_alertas_operativas,
    generar_alertas_sindicato,
    generar_alertas_telefonia,
)


User = get_user_model()


class SindicatoAlertasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa_a = Empresa.objects.create(nombre='Empresa A', tipo='CLIENTE')
        cls.empresa_b = Empresa.objects.create(nombre='Empresa B', tipo='CLIENTE')

        cls.grp_admin = Group.objects.create(name='Administracion')
        cls.grp_tesoreria = Group.objects.create(name='Tesoreria')
        cls.grp_dirigente = Group.objects.create(name='Dirigente')

        cls.admin_a = User.objects.create_user(username='admin_alerta', email='admin_alerta@test.cl', password='x')
        cls.admin_a.groups.add(cls.grp_admin)
        UserProfile.objects.create(user=cls.admin_a, empresa=cls.empresa_a, role='ADMIN')

        cls.tesoreria_a = User.objects.create_user(username='tes_alerta', email='tes_alerta@test.cl', password='x')
        cls.tesoreria_a.groups.add(cls.grp_tesoreria)
        UserProfile.objects.create(user=cls.tesoreria_a, empresa=cls.empresa_a, role='ADMIN')

        cls.dirigente_a = User.objects.create_user(username='dir_alerta', email='dir_alerta@test.cl', password='x')
        cls.dirigente_a.groups.add(cls.grp_dirigente)
        UserProfile.objects.create(user=cls.dirigente_a, empresa=cls.empresa_a, role='ADMIN')

        cls.socio_a = SocioSindicato.objects.create(
            empresa=cls.empresa_a,
            rut='12345678-5',
            nombre='Socio Alerta',
        )
        cls.socio_b = SocioSindicato.objects.create(
            empresa=cls.empresa_b,
            rut='11111111-1',
            nombre='Socio B',
        )

        cls.benef_tel_a = TipoBeneficioSindicato.objects.create(
            empresa=cls.empresa_a,
            codigo='TEL',
            nombre='Telefonia',
            estado=TipoBeneficioSindicato.ESTADO_ACTIVO,
        )
        cls.benef_gas_a = TipoBeneficioSindicato.objects.create(
            empresa=cls.empresa_a,
            codigo='GAS',
            nombre='Gas',
            estado=TipoBeneficioSindicato.ESTADO_ACTIVO,
        )

    def _crear_mov_tel(self, referencia, fecha_entrega, periodo='2026-01'):
        return MovimientoSindicato.objects.create(
            empresa=self.empresa_a,
            socio=self.socio_a,
            tipo_beneficio=self.benef_tel_a,
            periodo=periodo,
            monto=10000,
            fuente=MovimientoSindicato.FUENTE_TELEFONIA,
            estado=MovimientoSindicato.ESTADO_VALIDADO,
            referencia_externa=referencia,
            metadata_fuente={'source_columns': {'fecha_entrega': fecha_entrega, 'cuenta': referencia}},
        )

    def _fecha_hace_meses(self, meses):
        hoy = timezone.localdate()
        total = hoy.year * 12 + hoy.month - 1 - meses
        anio = total // 12
        mes = total % 12 + 1
        dia = min(hoy.day, 28)
        return f"{dia:02d}-{mes:02d}-{anio}"

    def test_01_alerta_telefonia_preventiva_20_meses(self):
        self._crear_mov_tel('TEL-20', self._fecha_hace_meses(20))
        generar_alertas_telefonia(self.empresa_a)
        self.assertTrue(AlertaSindicato.objects.filter(tipo_alerta='TELEFONIA_PREVENTIVA_20').exists())

    def test_02_alerta_telefonia_renovacion_21_22(self):
        self._crear_mov_tel('TEL-21', self._fecha_hace_meses(21))
        generar_alertas_telefonia(self.empresa_a)
        self.assertTrue(AlertaSindicato.objects.filter(tipo_alerta='TELEFONIA_RENOVACION_21_22').exists())

    def test_03_alerta_telefonia_vencida_24(self):
        self._crear_mov_tel('TEL-24', self._fecha_hace_meses(24))
        generar_alertas_telefonia(self.empresa_a)
        self.assertTrue(AlertaSindicato.objects.filter(tipo_alerta='TELEFONIA_VENCIDA_24').exists())

    def test_04_alerta_telefonia_fecha_invalida(self):
        self._crear_mov_tel('TEL-INV', 'fecha-no-valida')
        generar_alertas_telefonia(self.empresa_a)
        self.assertTrue(AlertaSindicato.objects.filter(tipo_alerta='TELEFONIA_FECHA_INVALIDA').exists())

    def test_05_alerta_operativa_movimientos_rechazados(self):
        MovimientoSindicato.objects.create(
            empresa=self.empresa_a,
            socio=self.socio_a,
            tipo_beneficio=self.benef_gas_a,
            periodo='2026-03',
            monto=12000,
            estado=MovimientoSindicato.ESTADO_RECHAZADO,
            referencia_externa='RCH-1',
        )
        generar_alertas_operativas(self.empresa_a)
        self.assertTrue(AlertaSindicato.objects.filter(tipo_alerta='MOVIMIENTOS_RECHAZADO').exists())

    def test_06_alerta_operativa_movimientos_sin_consolidado(self):
        MovimientoSindicato.objects.create(
            empresa=self.empresa_a,
            socio=self.socio_a,
            tipo_beneficio=self.benef_gas_a,
            periodo='2026-04',
            monto=12000,
            estado=MovimientoSindicato.ESTADO_VALIDADO,
            referencia_externa='MSC-1',
        )
        generar_alertas_operativas(self.empresa_a)
        self.assertTrue(AlertaSindicato.objects.filter(tipo_alerta='MOVIMIENTOS_SIN_CONSOLIDADO', periodo='2026-04').exists())

    def test_07_alerta_operativa_consolidado_cerrado_no_exportado(self):
        ConsolidadoMensualSindicato.objects.create(
            empresa=self.empresa_a,
            periodo='2026-05',
            estado=ConsolidadoMensualSindicato.ESTADO_CERRADO,
        )
        generar_alertas_operativas(self.empresa_a)
        self.assertTrue(AlertaSindicato.objects.filter(tipo_alerta='CONSOLIDADO_CERRADO_NO_EXPORTADO').exists())

    def test_08_generacion_idempotente_por_clave(self):
        self._crear_mov_tel('TEL-IDEMP', 'fecha-no-valida', periodo='2026-06')
        generar_alertas_sindicato(self.empresa_a, periodo='2026-06')
        generar_alertas_sindicato(self.empresa_a, periodo='2026-06')
        self.assertEqual(
            AlertaSindicato.objects.filter(
                empresa=self.empresa_a,
                tipo_alerta='TELEFONIA_FECHA_INVALIDA',
                periodo='2026-06',
            ).count(),
            1,
        )

    def test_09_listado_alertas_respeta_tenant(self):
        AlertaSindicato.objects.create(
            empresa=self.empresa_b,
            socio=self.socio_b,
            tipo_alerta='EXTERNA',
            categoria=AlertaSindicato.CATEGORIA_DATOS,
            prioridad=AlertaSindicato.PRIORIDAD_BAJA,
            titulo='Alerta Empresa B',
            descripcion='No debe verse en empresa A',
            clave_unica='B-UNICA',
        )
        self.client.force_login(self.admin_a)
        resp = self.client.get(reverse('core:sindiapp_alerta_list'))
        self.assertEqual(resp.status_code, 200)
        alertas = list(resp.context['alertas'])
        self.assertFalse(any(a.empresa_id == self.empresa_b.id for a in alertas))

    def test_10_permiso_dirigente_no_puede_resolver_alerta(self):
        alerta = AlertaSindicato.objects.create(
            empresa=self.empresa_a,
            socio=self.socio_a,
            tipo_alerta='TEST',
            categoria=AlertaSindicato.CATEGORIA_DATOS,
            prioridad=AlertaSindicato.PRIORIDAD_MEDIA,
            titulo='Test alerta',
            descripcion='Test',
            clave_unica='A-TEST-1',
        )
        self.client.force_login(self.dirigente_a)
        resp = self.client.post(
            reverse('core:sindiapp_alerta_accion', kwargs={'pk': alerta.id, 'accion': 'resolver'}),
            data={'next': reverse('core:sindiapp_alerta_list')},
        )
        self.assertEqual(resp.status_code, 403)
        alerta.refresh_from_db()
        self.assertEqual(alerta.estado, AlertaSindicato.ESTADO_PENDIENTE)
