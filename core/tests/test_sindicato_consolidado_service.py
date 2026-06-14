from decimal import Decimal

from django.contrib.auth import get_user_model
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
from core.services.sindicato_consolidado import ConsolidadoBloqueadoError, generar_o_recalcular_consolidado


User = get_user_model()


class SindicatoConsolidadoServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa_a = Empresa.objects.create(nombre="Empresa A", tipo="CLIENTE")
        cls.empresa_b = Empresa.objects.create(nombre="Empresa B", tipo="CLIENTE")

        cls.user = User.objects.create_user(
            username="tesoreria.a@empresa-a.cl",
            email="tesoreria.a@empresa-a.cl",
            password="x",
        )

        cls.benef_activo_a = TipoBeneficioSindicato.objects.create(
            empresa=cls.empresa_a,
            codigo="GAS",
            nombre="Gas",
            estado=TipoBeneficioSindicato.ESTADO_ACTIVO,
            orden_export=1,
        )
        cls.benef_inactivo_a = TipoBeneficioSindicato.objects.create(
            empresa=cls.empresa_a,
            codigo="TEL",
            nombre="Telefonia",
            estado=TipoBeneficioSindicato.ESTADO_INACTIVO,
            orden_export=2,
        )
        cls.benef_activo_b = TipoBeneficioSindicato.objects.create(
            empresa=cls.empresa_b,
            codigo="GAS",
            nombre="Gas",
            estado=TipoBeneficioSindicato.ESTADO_ACTIVO,
            orden_export=1,
        )

        cls.socio_activo_a = SocioSindicato.objects.create(
            empresa=cls.empresa_a,
            rut="12345678-5",
            nombre="Socio Activo",
            estado_laboral=SocioSindicato.ESTADO_LABORAL_ACTIVO,
            estado=SocioSindicato.ESTADO_ACTIVO,
        )
        cls.socio_licencia_a = SocioSindicato.objects.create(
            empresa=cls.empresa_a,
            rut="11111111-1",
            nombre="Socio Licencia",
            estado_laboral=SocioSindicato.ESTADO_LABORAL_LICENCIA,
            estado=SocioSindicato.ESTADO_ACTIVO,
        )
        cls.socio_desvinculado_a = SocioSindicato.objects.create(
            empresa=cls.empresa_a,
            rut="22222222-2",
            nombre="Socio Desvinculado",
            estado_laboral=SocioSindicato.ESTADO_LABORAL_DESVINCULADO,
            estado=SocioSindicato.ESTADO_ACTIVO,
        )
        cls.socio_b = SocioSindicato.objects.create(
            empresa=cls.empresa_b,
            rut="99999999-9",
            nombre="Socio B",
            estado_laboral=SocioSindicato.ESTADO_LABORAL_ACTIVO,
            estado=SocioSindicato.ESTADO_ACTIVO,
        )

    def _crear_datos_periodo_2026_08(self):
        MovimientoSindicato.objects.create(
            empresa=self.empresa_a,
            socio=self.socio_activo_a,
            tipo_beneficio=self.benef_activo_a,
            periodo="2026-08",
            monto=Decimal("10000"),
            estado=MovimientoSindicato.ESTADO_VALIDADO,
            referencia_externa="A-1",
        )
        MovimientoSindicato.objects.create(
            empresa=self.empresa_a,
            socio=self.socio_activo_a,
            tipo_beneficio=self.benef_activo_a,
            periodo="2026-08",
            monto=Decimal("5000"),
            estado=MovimientoSindicato.ESTADO_PENDIENTE,
            referencia_externa="A-2",
        )
        MovimientoSindicato.objects.create(
            empresa=self.empresa_a,
            socio=self.socio_licencia_a,
            tipo_beneficio=self.benef_activo_a,
            periodo="2026-08",
            monto=Decimal("7000"),
            estado=MovimientoSindicato.ESTADO_OBSERVADO,
            referencia_externa="A-3",
        )
        MovimientoSindicato.objects.create(
            empresa=self.empresa_a,
            socio=self.socio_desvinculado_a,
            tipo_beneficio=self.benef_activo_a,
            periodo="2026-08",
            monto=Decimal("3000"),
            estado=MovimientoSindicato.ESTADO_VALIDADO,
            referencia_externa="A-4",
        )
        MovimientoSindicato.objects.create(
            empresa=self.empresa_a,
            socio=self.socio_activo_a,
            tipo_beneficio=self.benef_activo_a,
            periodo="2026-08",
            monto=Decimal("4000"),
            estado=MovimientoSindicato.ESTADO_RECHAZADO,
            referencia_externa="A-5",
        )
        MovimientoSindicato.objects.create(
            empresa=self.empresa_a,
            socio=self.socio_activo_a,
            tipo_beneficio=self.benef_inactivo_a,
            periodo="2026-08",
            monto=Decimal("9000"),
            estado=MovimientoSindicato.ESTADO_VALIDADO,
            referencia_externa="A-6",
        )

        MovimientoSindicato.objects.create(
            empresa=self.empresa_b,
            socio=self.socio_b,
            tipo_beneficio=self.benef_activo_b,
            periodo="2026-08",
            monto=Decimal("9900"),
            estado=MovimientoSindicato.ESTADO_VALIDADO,
            referencia_externa="B-1",
        )

    def test_generar_consolidado_por_empresa_periodo_con_totales(self):
        self._crear_datos_periodo_2026_08()

        resultado = generar_o_recalcular_consolidado(
            empresa=self.empresa_a,
            periodo="2026-08",
            usuario=self.user,
        )

        self.assertEqual(resultado.accion, "GENERAR_CONSOLIDADO")
        self.assertEqual(resultado.total_movimientos_origen, 6)
        self.assertEqual(resultado.total_detalles_generados, 2)
        self.assertEqual(resultado.total_socios, 2)
        self.assertEqual(resultado.total_monto, Decimal("22000"))
        self.assertEqual(resultado.excluidos_rechazados, 1)
        self.assertEqual(resultado.excluidos_desvinculados, 1)
        self.assertEqual(resultado.excluidos_beneficio_inactivo, 1)
        self.assertEqual(resultado.observados_licencia, 1)
        self.assertEqual(resultado.observados_movimiento, 1)

        consolidado = ConsolidadoMensualSindicato.objects.get(
            empresa=self.empresa_a,
            periodo="2026-08",
        )
        self.assertEqual(consolidado.total_socios, 2)
        self.assertEqual(consolidado.total_monto, Decimal("22000"))

        detalle_activo = ConsolidadoDetalleSindicato.objects.get(
            consolidado=consolidado,
            socio=self.socio_activo_a,
            tipo_beneficio=self.benef_activo_a,
        )
        self.assertEqual(detalle_activo.monto_aprobado, Decimal("15000"))
        self.assertEqual(detalle_activo.motivo_ajuste or "", "")

        detalle_licencia = ConsolidadoDetalleSindicato.objects.get(
            consolidado=consolidado,
            socio=self.socio_licencia_a,
            tipo_beneficio=self.benef_activo_a,
        )
        self.assertEqual(detalle_licencia.monto_aprobado, Decimal("7000"))
        self.assertIn("SOCIO_LICENCIA_MEDICA", detalle_licencia.motivo_ajuste)
        self.assertIn("MOVIMIENTO_OBSERVADO", detalle_licencia.motivo_ajuste)

        audit = AuditoriaSindicato.objects.filter(
            empresa=self.empresa_a,
            accion="GENERAR_CONSOLIDADO",
            periodo="2026-08",
        ).latest("created_at")
        self.assertEqual(audit.usuario, self.user)
        self.assertEqual(audit.payload["total_monto"], 22000)

    def test_recalculo_idempotente_si_esta_abierto(self):
        self._crear_datos_periodo_2026_08()

        generar_o_recalcular_consolidado(empresa=self.empresa_a, periodo="2026-08", usuario=self.user)
        generar_o_recalcular_consolidado(empresa=self.empresa_a, periodo="2026-08", usuario=self.user)

        consolidado = ConsolidadoMensualSindicato.objects.get(empresa=self.empresa_a, periodo="2026-08")
        self.assertEqual(consolidado.estado, ConsolidadoMensualSindicato.ESTADO_ABIERTO)
        self.assertEqual(consolidado.total_socios, 2)
        self.assertEqual(consolidado.total_monto, Decimal("22000"))
        self.assertEqual(ConsolidadoDetalleSindicato.objects.filter(consolidado=consolidado).count(), 2)
        self.assertEqual(
            AuditoriaSindicato.objects.filter(
                empresa=self.empresa_a,
                periodo="2026-08",
                accion__in=["GENERAR_CONSOLIDADO", "RECALCULAR_CONSOLIDADO"],
            ).count(),
            2,
        )

    def test_bloquea_generacion_si_periodo_cerrado_o_exportado(self):
        consolidado = ConsolidadoMensualSindicato.objects.create(
            empresa=self.empresa_a,
            periodo="2026-09",
            estado=ConsolidadoMensualSindicato.ESTADO_CERRADO,
            total_socios=1,
            total_monto=Decimal("1000"),
        )
        ConsolidadoDetalleSindicato.objects.create(
            empresa=self.empresa_a,
            consolidado=consolidado,
            socio=self.socio_activo_a,
            tipo_beneficio=self.benef_activo_a,
            monto_aprobado=Decimal("1000"),
        )

        with self.assertRaises(ConsolidadoBloqueadoError):
            generar_o_recalcular_consolidado(
                empresa=self.empresa_a,
                periodo="2026-09",
                usuario=self.user,
            )

        consolidado.refresh_from_db()
        self.assertEqual(consolidado.total_monto, Decimal("1000"))
        self.assertEqual(ConsolidadoDetalleSindicato.objects.filter(consolidado=consolidado).count(), 1)

    def test_aislamiento_multiempresa_en_generacion(self):
        self._crear_datos_periodo_2026_08()

        generar_o_recalcular_consolidado(empresa=self.empresa_a, periodo="2026-08", usuario=self.user)

        self.assertTrue(
            ConsolidadoMensualSindicato.objects.filter(empresa=self.empresa_a, periodo="2026-08").exists()
        )
        self.assertFalse(
            ConsolidadoMensualSindicato.objects.filter(empresa=self.empresa_b, periodo="2026-08").exists()
        )

        consolidado_a = ConsolidadoMensualSindicato.objects.get(empresa=self.empresa_a, periodo="2026-08")
        for det in ConsolidadoDetalleSindicato.objects.filter(consolidado=consolidado_a):
            self.assertEqual(det.empresa, self.empresa_a)
            self.assertEqual(det.socio.empresa, self.empresa_a)
            self.assertEqual(det.tipo_beneficio.empresa, self.empresa_a)
