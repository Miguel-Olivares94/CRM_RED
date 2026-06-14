from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import (
    AuditoriaSindicato,
    Empresa,
    MovimientoSindicato,
    SocioSindicato,
    TipoBeneficioSindicato,
)
from core.services.sindicato_prevalidacion import prevalidar_movimientos_para_consolidado


User = get_user_model()


class SindicatoPrevalidacionServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa = Empresa.objects.create(nombre='Empresa A', tipo='CLIENTE')
        cls.user = User.objects.create_user(username='tes_pre', email='tes_pre@test.cl', password='x')

        cls.benef = TipoBeneficioSindicato.objects.create(
            empresa=cls.empresa,
            codigo='GAS',
            nombre='Gas',
            estado=TipoBeneficioSindicato.ESTADO_ACTIVO,
            orden_export=1,
        )

        cls.socio_lic = SocioSindicato.objects.create(
            empresa=cls.empresa,
            rut='12345678-5',
            nombre='Socio Lic',
            estado_laboral=SocioSindicato.ESTADO_LABORAL_ACTIVO,
            estado=SocioSindicato.ESTADO_ACTIVO,
        )
        cls.socio_baja = SocioSindicato.objects.create(
            empresa=cls.empresa,
            rut='11111111-1',
            nombre='Socio Baja',
            estado_laboral=SocioSindicato.ESTADO_LABORAL_ACTIVO,
            estado=SocioSindicato.ESTADO_ACTIVO,
        )

    def test_prevalidacion_marca_licencia_como_observado(self):
        mov = MovimientoSindicato.objects.create(
            empresa=self.empresa,
            socio=self.socio_lic,
            tipo_beneficio=self.benef,
            periodo='2026-12',
            monto=10000,
            estado=MovimientoSindicato.ESTADO_PENDIENTE,
            observacion='Caso con licencia medica vigente',
            referencia_externa='PRE-LIC-1',
        )

        result = prevalidar_movimientos_para_consolidado(empresa=self.empresa, periodo='2026-12', usuario=self.user)

        mov.refresh_from_db()
        self.socio_lic.refresh_from_db()
        self.assertEqual(mov.estado, MovimientoSindicato.ESTADO_OBSERVADO)
        self.assertEqual(self.socio_lic.estado_laboral, SocioSindicato.ESTADO_LABORAL_LICENCIA)
        self.assertEqual(result.observados_licencia, 1)
        self.assertEqual(result.excluidos_baja_despedido, 0)

    def test_prevalidacion_excluye_baja_y_despedido(self):
        mov = MovimientoSindicato.objects.create(
            empresa=self.empresa,
            socio=self.socio_baja,
            tipo_beneficio=self.benef,
            periodo='2026-12',
            monto=12000,
            estado=MovimientoSindicato.ESTADO_PENDIENTE,
            observacion='Registro marcado como despedido por RRHH',
            referencia_externa='PRE-BAJA-1',
        )

        result = prevalidar_movimientos_para_consolidado(empresa=self.empresa, periodo='2026-12', usuario=self.user)

        mov.refresh_from_db()
        self.socio_baja.refresh_from_db()
        self.assertEqual(mov.estado, MovimientoSindicato.ESTADO_RECHAZADO)
        self.assertEqual(self.socio_baja.estado_laboral, SocioSindicato.ESTADO_LABORAL_DESVINCULADO)
        self.assertEqual(result.excluidos_baja_despedido, 1)

    def test_prevalidacion_crea_auditoria(self):
        MovimientoSindicato.objects.create(
            empresa=self.empresa,
            socio=self.socio_lic,
            tipo_beneficio=self.benef,
            periodo='2026-11',
            monto=9000,
            estado=MovimientoSindicato.ESTADO_PENDIENTE,
            observacion='licencia medica',
            referencia_externa='PRE-AUD-1',
        )

        prevalidar_movimientos_para_consolidado(empresa=self.empresa, periodo='2026-11', usuario=self.user)

        audit = AuditoriaSindicato.objects.filter(
            empresa=self.empresa,
            accion='PREVALIDAR_CONSOLIDADO',
            periodo='2026-11',
        ).latest('created_at')
        self.assertEqual(audit.payload.get('observados_licencia'), 1)
        self.assertEqual(audit.payload.get('excluidos_baja_despedido'), 0)
