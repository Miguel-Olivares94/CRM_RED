from django.test import SimpleTestCase

from core.services.sindicato_fuentes import (
    FUENTE_COPEUCH,
    FUENTE_GAS,
    FUENTE_GENERICA,
    FUENTE_TELEFONIA,
    detectar_fuente,
    parsear_filas_por_fuente,
)


class SindicatoParserFuenteTests(SimpleTestCase):
    def test_detecta_fuente_gas_por_headers(self):
        headers = {"rut", "nombre_apellido", "site", "vale_de_gas", "monto"}
        self.assertEqual(detectar_fuente(headers), FUENTE_GAS)

    def test_detecta_fuente_telefonia_por_headers(self):
        headers = {"rut", "razon_social", "cuenta", "pcs", "cargo_fijo", "fecha_de_entrega"}
        self.assertEqual(detectar_fuente(headers), FUENTE_TELEFONIA)

    def test_detecta_fuente_copeuch_por_headers(self):
        headers = {"rut", "nombre", "fec_ing_socio", "acciones", "prestamos", "tot_dctos"}
        self.assertEqual(detectar_fuente(headers), FUENTE_COPEUCH)

    def test_detecta_fuente_generica_si_no_calza(self):
        headers = {"foo", "bar", "baz"}
        self.assertEqual(detectar_fuente(headers), FUENTE_GENERICA)

    def test_mapea_gas_con_monto_y_observacion_extra(self):
        filas = [
            {
                "_fila": 2,
                "rut": "12.345.678-5",
                "nombre_apellido": "Socio Gas",
                "site": "Aramark",
                "vale_de_gas": "15 KILOS",
                "monto": "23500",
            }
        ]

        fuente, result = parsear_filas_por_fuente(filas, "abc123")
        self.assertEqual(fuente, FUENTE_GAS)
        self.assertEqual(result[0].nombre, "Socio Gas")
        self.assertEqual(result[0].monto_raw, "23500")
        self.assertIn("Site: Aramark", result[0].observacion)
        self.assertIn("Vale gas: 15 KILOS", result[0].observacion)
        self.assertEqual(result[0].referencia_externa, "GAS-abc123-2")
        self.assertEqual(result[0].source_columns.get("vale_de_gas"), "15 KILOS")

    def test_mapea_telefonia_con_cargo_fijo_y_observaciones(self):
        filas = [
            {
                "_fila": 3,
                "rut": "17.983.258-5",
                "razon_social": "Socio Tel",
                "cuenta": "56933115919",
                "pcs": "56933115919",
                "cargo_fijo": "13500",
                "fecha_de_entrega": "02-08-23",
            }
        ]

        fuente, result = parsear_filas_por_fuente(filas, "def456")
        self.assertEqual(fuente, FUENTE_TELEFONIA)
        self.assertEqual(result[0].monto_raw, "13500")
        self.assertIn("Cuenta: 56933115919", result[0].observacion)
        self.assertIn("PCS: 56933115919", result[0].observacion)
        self.assertIn("Fecha entrega: 02-08-23", result[0].observacion)
        self.assertEqual(result[0].referencia_externa, "56933115919")

    def test_mapea_copeuch_con_total_descuentos(self):
        filas = [
            {
                "_fila": 4,
                "rut": "15.536.420-3",
                "nombre": "Socio Cop",
                "fec_ing_socio": "28-10-25",
                "acciones": "$3.680",
                "prestamos": "$0",
                "tot_dctos": "$3.680",
            }
        ]

        fuente, result = parsear_filas_por_fuente(filas, "ghi789")
        self.assertEqual(fuente, FUENTE_COPEUCH)
        self.assertEqual(result[0].monto_raw, "$3.680")
        self.assertIn("Fecha ingreso socio: 28-10-25", result[0].observacion)
        self.assertIn("Acciones: $3.680", result[0].observacion)
        self.assertIn("Prestamos: $0", result[0].observacion)
        self.assertEqual(result[0].referencia_externa, "COP-ghi789-4")
