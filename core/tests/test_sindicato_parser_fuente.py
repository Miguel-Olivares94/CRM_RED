from django.test import SimpleTestCase

from core.services.sindicato_fuentes import (
    FUENTE_CLINICA_OMI,
    FUENTE_COPEUCH,
    FUENTE_CUOTA_EXTRAORDINARIA,
    FUENTE_DEUDA_SINDICAL,
    FUENTE_DESCUENTO_DHL,
    FUENTE_GAS,
    FUENTE_GENERICA,
    FUENTE_GIMNASIO,
    FUENTE_HAPPYLAND,
    FUENTE_TELEFONIA,
    FUENTE_VETERINARIA,
    REQUIERE_CONFIRMACION_CLIENTE,
    detectar_fuente,
    normalizar_header,
    parsear_filas_por_fuente,
)


class SindicatoParserFuenteTests(SimpleTestCase):
    def test_normalizar_header_variantes_copeuch_total_descuentos(self):
        variantes = [
            'TOT. DCTOS.',
            'Total Descuentos',
            'TOTAL DCTOS',
            'Tot Dctos',
            '  Tót.   Dctos  ',
        ]
        normalizados = {normalizar_header(v) for v in variantes}
        self.assertIn('tot_dctos', normalizados)
        self.assertIn('total_descuentos', normalizados)
        self.assertIn('total_dctos', normalizados)

    def test_detecta_fuente_gas_por_headers(self):
        headers = {"rut", "nombre_apellido", "site", "vale_de_gas", "monto"}
        self.assertEqual(detectar_fuente(headers), FUENTE_GAS)

    def test_detecta_fuente_telefonia_por_headers(self):
        headers = {"rut", "razon_social", "cuenta", "pcs", "cargo_fijo", "fecha_de_entrega"}
        self.assertEqual(detectar_fuente(headers), FUENTE_TELEFONIA)

    def test_detecta_fuente_copeuch_por_headers(self):
        headers = {"rut", "nombre", "fec_ing_socio", "acciones", "prestamos", "tot_dctos"}
        self.assertEqual(detectar_fuente(headers), FUENTE_COPEUCH)

    def test_detecta_fuente_copeuch_por_header_total_descuentos(self):
        headers = {"RUT", "NOMBRE", "Total Descuentos"}
        self.assertEqual(detectar_fuente(headers), FUENTE_COPEUCH)

    def test_detecta_fuente_copeuch_por_header_total_dctos(self):
        headers = {"RUT", "NOMBRE", "TOTAL DCTOS"}
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

    def test_detecta_telefonia_con_header_total_planilla_real(self):
        """Planilla real junio 2026 usa 'Total' en lugar de 'Cargo Fijo'."""
        headers = {"RUT", "Razon social", "Total"}
        self.assertEqual(detectar_fuente(headers), FUENTE_TELEFONIA)

    def test_mapea_telefonia_real_con_columna_total(self):
        """Planilla real: RUT + Razon social + Total."""
        filas = [
            {
                "_fila": 2,
                "rut": "10356317-8",
                "razon_social": "ARRIAZA AQUEVEQUE, GLADYS PATRICIA",
                "total": "57000",
            }
        ]
        fuente, result = parsear_filas_por_fuente(filas, "tel26")
        self.assertEqual(fuente, FUENTE_TELEFONIA)
        self.assertEqual(result[0].monto_raw, "57000")
        self.assertEqual(result[0].source, FUENTE_TELEFONIA)

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

    def test_mapea_copeuch_con_alias_total_dctos(self):
        filas = [
            {
                "_fila": 5,
                "rut": "15.536.420-3",
                "nombre": "Socio Cop",
                "total_dctos": "4200",
            }
        ]

        fuente, result = parsear_filas_por_fuente(filas, "jkl012")
        self.assertEqual(fuente, FUENTE_COPEUCH)
        self.assertEqual(result[0].monto_raw, "4200")


# ---------------------------------------------------------------------------
# Tests para planillas reales del cliente - nuevas fuentes
# ---------------------------------------------------------------------------

class SindicatoParserFuenteGasRealTests(SimpleTestCase):
    """Gas real usa 'Descuento' como monto y 'Nombre y apellidos' como nombre."""

    def test_detecta_gas_con_columna_descuento(self):
        headers = {"Rut", "Nombre y apellidos", "Descuento"}
        self.assertEqual(detectar_fuente(headers), FUENTE_GAS)

    def test_detecta_gas_con_columna_descuento_y_site(self):
        headers = {"Rut", "Nombre y apellidos", "Descuento", "Site"}
        self.assertEqual(detectar_fuente(headers), FUENTE_GAS)

    def test_mapea_gas_real_con_descuento_y_nombre_y_apellidos(self):
        filas = [
            {
                "_fila": 5,
                "rut": "16629085-6",
                "nombre_y_apellidos": "RODRIGUEZ BUENO, KATHERINE MARCELA",
                "descuento": "23500",
            }
        ]
        fuente, result = parsear_filas_por_fuente(filas, "jun26")
        self.assertEqual(fuente, FUENTE_GAS)
        self.assertEqual(result[0].nombre, "RODRIGUEZ BUENO, KATHERINE MARCELA")
        self.assertEqual(result[0].monto_raw, "23500")
        self.assertEqual(result[0].source, FUENTE_GAS)

    def test_gas_real_guarda_site_en_metadata(self):
        filas = [
            {
                "_fila": 6,
                "rut": "12476297-9",
                "nombre_y_apellidos": "ZUÑIGA CABRERA, PAOLA ANDREA",
                "descuento": "23500",
                "site": "Planta Norte",
            }
        ]
        fuente, result = parsear_filas_por_fuente(filas, "jun26")
        self.assertEqual(fuente, FUENTE_GAS)
        self.assertIn("Site: Planta Norte", result[0].observacion)
        self.assertEqual(result[0].source_columns.get("site"), "Planta Norte")


class SindicatoParserFuenteVeterinariaTests(SimpleTestCase):

    def test_detecta_veterinaria(self):
        headers = {"RUT", "NOMBRE", "CUOTAS", "DESCUENTO"}
        self.assertEqual(detectar_fuente(headers), FUENTE_VETERINARIA)

    def test_mapea_veterinaria_correctamente(self):
        filas = [
            {
                "_fila": 4,
                "rut": "13883500-6",
                "nombre": "MUÑOZ ORTIZ, JACQUELINE ANDREA",
                "cuotas": "3 de 3",
                "descuento": "26666",
            }
        ]
        fuente, result = parsear_filas_por_fuente(filas, "vet26")
        self.assertEqual(fuente, FUENTE_VETERINARIA)
        self.assertEqual(result[0].monto_raw, "26666")
        self.assertEqual(result[0].nombre, "MUÑOZ ORTIZ, JACQUELINE ANDREA")
        self.assertEqual(result[0].source, FUENTE_VETERINARIA)

    def test_veterinaria_guarda_cuotas_en_observacion(self):
        filas = [{"_fila": 5, "rut": "26157088-2", "nombre": "MILLAN VARGAS, AIRAM", "cuotas": "6 de 6", "descuento": "26500"}]
        fuente, result = parsear_filas_por_fuente(filas, "vet26")
        self.assertIn("Cuotas: 6 de 6", result[0].observacion)
        self.assertEqual(result[0].source_columns.get("cuotas"), "6 de 6")

    def test_veterinaria_sin_monto_retorna_monto_vacio(self):
        filas = [{"_fila": 6, "rut": "13885164-8", "nombre": "BARRA RAMIREZ, LETICIA", "cuotas": "6 de 6"}]
        fuente, result = parsear_filas_por_fuente(filas, "vet26")
        self.assertEqual(result[0].monto_raw, "")


class SindicatoParserFuenteGimnasioTests(SimpleTestCase):

    def test_detecta_gimnasio(self):
        headers = {"RUT", "NOMBRE", "CUOTAS", "DESCONTAR"}
        self.assertEqual(detectar_fuente(headers), FUENTE_GIMNASIO)

    def test_mapea_gimnasio_con_descontar(self):
        filas = [
            {
                "_fila": 2,
                "rut": "19745228-5",
                "nombre": "VIDELA BERNAL, MATIAS MAURICIO",
                "cuotas": "2 de 3",
                "descontar": "18800",
            }
        ]
        fuente, result = parsear_filas_por_fuente(filas, "gym26")
        self.assertEqual(fuente, FUENTE_GIMNASIO)
        self.assertEqual(result[0].monto_raw, "18800")
        self.assertEqual(result[0].source, FUENTE_GIMNASIO)
        self.assertEqual(result[0].source_columns.get("descontar"), "18800")

    def test_gimnasio_guarda_cuotas_en_observacion(self):
        filas = [{"_fila": 3, "rut": "27189195-4", "nombre": "CHACON ARIAS, ALEJANDRO", "descontar": "18800", "cuotas": "1"}]
        fuente, result = parsear_filas_por_fuente(filas, "gym26")
        self.assertIn("Cuotas: 1", result[0].observacion)


class SindicatoParserFuenteHappylandTests(SimpleTestCase):

    def test_detecta_happyland(self):
        headers = {"Rut", "Nombre", "CUOTA", "DESCUENTO", "COMENTARIO"}
        self.assertEqual(detectar_fuente(headers), FUENTE_HAPPYLAND)

    def test_mapea_happyland_con_comentario(self):
        filas = [
            {
                "_fila": 2,
                "rut": "16481893-4",
                "nombre": "FUENTEALBA ESCOBAR, ELIZABETH SILVANA",
                "cuota": "2 de 3",
                "descuento": "16000",
                "comentario": "Solicitó 4 tarjetas",
            }
        ]
        fuente, result = parsear_filas_por_fuente(filas, "hpl26")
        self.assertEqual(fuente, FUENTE_HAPPYLAND)
        self.assertEqual(result[0].monto_raw, "16000")
        self.assertIn("Comentario: Solicitó 4 tarjetas", result[0].observacion)
        self.assertIn("Cuota: 2 de 3", result[0].observacion)
        self.assertEqual(result[0].source, FUENTE_HAPPYLAND)


class SindicatoParserFuenteDeudaSindicalTests(SimpleTestCase):

    def test_detecta_deuda_sindical(self):
        headers = {"RUT", "Nombre", "Centro Costo", "DESCUENTO", "Comentario"}
        self.assertEqual(detectar_fuente(headers), FUENTE_DEUDA_SINDICAL)

    def test_mapea_deuda_sindical_con_centro_costo(self):
        filas = [
            {
                "_fila": 5,
                "rut": "25575228-6",
                "nombre": "ANTOINE, NERLANDE",
                "centro_costo": "SCJ",
                "descuento": "12000",
                "comentario": "TRABAJANDO",
            }
        ]
        fuente, result = parsear_filas_por_fuente(filas, "deu26")
        self.assertEqual(fuente, FUENTE_DEUDA_SINDICAL)
        self.assertEqual(result[0].monto_raw, "12000")
        self.assertIn("Centro costo: SCJ", result[0].observacion)
        self.assertIn("Comentario: TRABAJANDO", result[0].observacion)
        self.assertEqual(result[0].source_columns.get("centro_costo"), "SCJ")

    def test_deuda_sindical_sin_comentario(self):
        filas = [{"_fila": 6, "rut": "18851140-6", "nombre": "AVILA MEDINA, KATHERINE", "centro_costo": "MONDELEZ", "descuento": "20000"}]
        fuente, result = parsear_filas_por_fuente(filas, "deu26")
        self.assertEqual(result[0].monto_raw, "20000")
        self.assertIn("Centro costo: MONDELEZ", result[0].observacion)


class SindicatoParserFuenteCuotaExtraordinariaTests(SimpleTestCase):

    def test_detecta_cuota_extraordinaria(self):
        headers = {"Rut", "Nombre", "Cuota Extraor.Sindicato"}
        self.assertEqual(detectar_fuente(headers), FUENTE_CUOTA_EXTRAORDINARIA)

    def test_mapea_fiesta_con_cuota_extraor(self):
        filas = [
            {
                "_fila": 2,
                "rut": "10356317-8",
                "nombre": "ARRIAZA AQUEVEQUE, GLADYS PATRICIA",
                "cuota_extraor_sindicato": "17000",
            }
        ]
        fuente, result = parsear_filas_por_fuente(filas, "fie26")
        self.assertEqual(fuente, FUENTE_CUOTA_EXTRAORDINARIA)
        self.assertEqual(result[0].monto_raw, "17000")
        self.assertEqual(result[0].source, FUENTE_CUOTA_EXTRAORDINARIA)
        self.assertEqual(result[0].source_columns.get("cuota_extraordinaria"), "17000")

    def test_referencia_auto_usa_prefijo_fie(self):
        filas = [{"_fila": 3, "rut": "12451967-5", "nombre": "PEÑA MERINO, KARINA", "cuota_extraor_sindicato": "17000"}]
        fuente, result = parsear_filas_por_fuente(filas, "fie26")
        self.assertTrue(result[0].referencia_externa.startswith("FIE-"))


class SindicatoParserFuenteDescuentoDHLTests(SimpleTestCase):
    """DHL usa regla TEMPORAL hasta confirmación del cliente."""

    def test_detecta_descuento_dhl(self):
        headers = {"Rut Socio", "Nombre Socio", "Total A Pagar", "Monto Recepcionado"}
        self.assertEqual(detectar_fuente(headers), FUENTE_DESCUENTO_DHL)

    def test_mapea_dhl_con_total_a_pagar(self):
        filas = [
            {
                "_fila": 9,
                "rut_socio": "25180085-5",
                "nombre_socio": "ASCONA HUARANCA JULIO CESAR",
                "total_a_pagar": "75205",
                "monto_recepcionado": "0",
                "_valor_cuota": "69205",
                "_capital": "5000",
                "_cuota_gastos": "1000",
                "_ahorro": "0",
                "plazo_credito": "36",
                "n_credito": "622802",
            }
        ]
        fuente, result = parsear_filas_por_fuente(filas, "dhl26")
        self.assertEqual(fuente, FUENTE_DESCUENTO_DHL)
        # Regla temporal: Total a pagar
        self.assertEqual(result[0].monto_raw, "75205")
        self.assertEqual(result[0].rut_raw, "25180085-5")
        self.assertEqual(result[0].source, FUENTE_DESCUENTO_DHL)

    def test_dhl_guarda_monto_recepcionado_en_metadata(self):
        filas = [{"_fila": 9, "rut_socio": "25180085-5", "nombre_socio": "ASCONA", "total_a_pagar": "75205", "monto_recepcionado": "0"}]
        fuente, result = parsear_filas_por_fuente(filas, "dhl26")
        # monto_recepcionado NO debe ser el monto del movimiento, solo metadata
        self.assertEqual(result[0].monto_raw, "75205")
        self.assertEqual(result[0].source_columns.get("monto_recepcionado"), "0")

    def test_dhl_marca_requiere_confirmacion_cliente(self):
        filas = [{"_fila": 9, "rut_socio": "11353919-4", "nombre_socio": "BURGOS", "total_a_pagar": "221947", "monto_recepcionado": "0"}]
        fuente, result = parsear_filas_por_fuente(filas, "dhl26")
        self.assertIn(REQUIERE_CONFIRMACION_CLIENTE, result[0].source_columns)

    def test_referencia_auto_usa_prefijo_dhl(self):
        filas = [{"_fila": 10, "rut_socio": "16117304-5", "nombre_socio": "CANDIA", "total_a_pagar": "111786"}]
        fuente, result = parsear_filas_por_fuente(filas, "dhl26")
        self.assertTrue(result[0].referencia_externa.startswith("DHL-"))


class SindicatoParserFuenteClinicaOMITests(SimpleTestCase):
    """OMI usa regla TEMPORAL (valor_cuota) hasta confirmación del cliente."""

    def test_detecta_clinica_omi(self):
        headers = {"RUT funcionario", "Monto tratamiento", "valor cuota", "Numero de Presupuesto"}
        self.assertEqual(detectar_fuente(headers), FUENTE_CLINICA_OMI)

    def test_detecta_clinica_omi_por_numero_presupuesto(self):
        headers = {"Numero de Presupuesto", "valor cuota"}
        self.assertEqual(detectar_fuente(headers), FUENTE_CLINICA_OMI)

    def test_mapea_omi_con_valor_cuota(self):
        filas = [
            {
                "_fila": 11,
                "rut_funcionario": "21266983-0",
                "nombre_funcionario": "Danilo",
                "apellido_funcionario": "Castillo Yañez",
                "monto_tratamiento": "978300",
                "valor_cuota": "81525",
                "numero_de_presupuesto": "24972",
                "nombre_beneficiario": "Danilo",
                "apellido_beneficiario": "Castillo Yañez",
            }
        ]
        fuente, result = parsear_filas_por_fuente(filas, "omi26")
        self.assertEqual(fuente, FUENTE_CLINICA_OMI)
        # Regla temporal: valor_cuota como monto mensual
        self.assertEqual(result[0].monto_raw, "81525")
        self.assertEqual(result[0].rut_raw, "21266983-0")
        self.assertEqual(result[0].source, FUENTE_CLINICA_OMI)

    def test_omi_guarda_monto_tratamiento_en_metadata(self):
        filas = [{"_fila": 11, "rut_funcionario": "17948980-5", "nombre_funcionario": "Arturo", "monto_tratamiento": "862800", "valor_cuota": "86280"}]
        fuente, result = parsear_filas_por_fuente(filas, "omi26")
        # monto_tratamiento es referencia de deuda, no entra al consolidado directamente
        self.assertEqual(result[0].monto_raw, "86280")
        self.assertEqual(result[0].source_columns.get("monto_tratamiento"), "862800")

    def test_omi_marca_requiere_confirmacion_cliente(self):
        filas = [{"_fila": 12, "rut_funcionario": "18676296-7", "nombre_funcionario": "German", "monto_tratamiento": "201900", "valor_cuota": "20190"}]
        fuente, result = parsear_filas_por_fuente(filas, "omi26")
        self.assertIn(REQUIERE_CONFIRMACION_CLIENTE, result[0].source_columns)

    def test_referencia_usa_numero_presupuesto(self):
        filas = [{"_fila": 11, "rut_funcionario": "21266983-0", "nombre_funcionario": "Danilo", "valor_cuota": "81525", "numero_de_presupuesto": "24972"}]
        fuente, result = parsear_filas_por_fuente(filas, "omi26")
        self.assertEqual(result[0].referencia_externa, "24972")
        self.assertTrue(result[0].referencia_informada)


class SindicatoParserFuenteDeteccionNoAmbiguaTests(SimpleTestCase):
    """Verifica que fuentes no se confunden entre sí con datos reales."""

    def test_gas_no_confunde_con_deuda_sindical(self):
        # Deuda sindical tiene centro_costo; gas no
        headers_deuda = {"RUT", "Nombre", "Centro Costo", "DESCUENTO"}
        headers_gas = {"Rut", "Nombre y apellidos", "Descuento"}
        self.assertEqual(detectar_fuente(headers_deuda), FUENTE_DEUDA_SINDICAL)
        self.assertEqual(detectar_fuente(headers_gas), FUENTE_GAS)

    def test_gym_no_confunde_con_veterinaria(self):
        # Gym tiene DESCONTAR; Veterinaria tiene CUOTAS + DESCUENTO (sin DESCONTAR)
        headers_gym = {"RUT", "NOMBRE", "CUOTAS", "DESCONTAR"}
        headers_vet = {"RUT", "NOMBRE", "CUOTAS", "DESCUENTO"}
        self.assertEqual(detectar_fuente(headers_gym), FUENTE_GIMNASIO)
        self.assertEqual(detectar_fuente(headers_vet), FUENTE_VETERINARIA)

    def test_happyland_no_confunde_con_deuda(self):
        # Happyland tiene COMENTARIO pero no Centro Costo
        headers_hpl = {"Rut", "Nombre", "CUOTA", "DESCUENTO", "COMENTARIO"}
        self.assertEqual(detectar_fuente(headers_hpl), FUENTE_HAPPYLAND)

    def test_dhl_no_confunde_con_gas(self):
        headers_dhl = {"Rut Socio", "Nombre Socio", "Total A Pagar", "Monto Recepcionado"}
        self.assertEqual(detectar_fuente(headers_dhl), FUENTE_DESCUENTO_DHL)

    def test_dhl_simple_cuota_monto_detecta_como_dhl(self):
        """Planilla DHL simple (RUT, NOMBRE, CUOTA, MONTO) debe detectar como DESCUENTO_DHL."""
        headers = {"RUT", "NOMBRE", "CUOTA", "MONTO"}
        self.assertEqual(detectar_fuente(headers), FUENTE_DESCUENTO_DHL)

    def test_omi_no_confunde_con_dhl(self):
        headers_omi = {"RUT funcionario", "Monto tratamiento", "valor cuota"}
        self.assertNotEqual(detectar_fuente(headers_omi), FUENTE_DESCUENTO_DHL)
        self.assertEqual(detectar_fuente(headers_omi), FUENTE_CLINICA_OMI)

    def test_copeuch_prevalece_sobre_generica(self):
        headers = {"RUT", "NOMBRE", "TOT. DCTOS."}
        self.assertEqual(detectar_fuente(headers), FUENTE_COPEUCH)

    def test_fuente_generica_si_headers_desconocidos(self):
        self.assertEqual(detectar_fuente({"col_a", "col_b", "col_c"}), FUENTE_GENERICA)

    def test_lista_vacia_retorna_generica(self):
        fuente, rows = parsear_filas_por_fuente([], "tag")
        self.assertEqual(fuente, FUENTE_GENERICA)
        self.assertEqual(rows, [])


class SindicatoParserFuenteE2EImportacionTests(SimpleTestCase):
    """Tests de importación E2E: cada planilla genera movimientos válidos
    con fuente, metadata y comportamiento de rechazo correctos."""

    def _fila(self, idx, **kwargs):
        return {"_fila": idx, **kwargs}

    # ---- Gas real -----------------------------------------------------------
    def test_gas_real_fila_valida_crea_movimiento_con_fuente(self):
        filas = [self._fila(5, rut="16629085-6", nombre_y_apellidos="RODRIGUEZ, KATHERINE", descuento="23500")]
        fuente, result = parsear_filas_por_fuente(filas, "jun26")
        self.assertEqual(fuente, FUENTE_GAS)
        self.assertEqual(result[0].source, FUENTE_GAS)
        self.assertEqual(result[0].monto_raw, "23500")
        self.assertNotEqual(result[0].rut_raw, "")

    def test_gas_fila_sin_monto_retorna_monto_vacio(self):
        filas = [self._fila(6, rut="12345678-5", nombre="Socio", descuento="")]
        fuente, result = parsear_filas_por_fuente(filas, "jun26")
        self.assertEqual(result[0].monto_raw, "")

    # ---- Veterinaria --------------------------------------------------------
    def test_veterinaria_fila_valida_tiene_fuente_correcta(self):
        filas = [self._fila(4, rut="13883500-6", nombre="MUÑOZ, JACQUELINE", cuotas="3 de 3", descuento="26666")]
        fuente, result = parsear_filas_por_fuente(filas, "vet26")
        self.assertEqual(result[0].source, FUENTE_VETERINARIA)
        self.assertEqual(result[0].monto_raw, "26666")

    # ---- Gym ----------------------------------------------------------------
    def test_gimnasio_fila_valida_metadata_source_columns(self):
        filas = [self._fila(2, rut="19745228-5", nombre="VIDELA BERNAL, MATIAS", cuotas="2 de 3", descontar="18800")]
        fuente, result = parsear_filas_por_fuente(filas, "gym26")
        self.assertEqual(result[0].source, FUENTE_GIMNASIO)
        self.assertIn("descontar", result[0].source_columns)

    # ---- Happyland ----------------------------------------------------------
    def test_happyland_fila_valida_fuente_y_metadata(self):
        filas = [self._fila(2, rut="16481893-4", nombre="FUENTEALBA, ELIZABETH", cuota="2 de 3", descuento="16000", comentario="ok")]
        fuente, result = parsear_filas_por_fuente(filas, "hpl26")
        self.assertEqual(result[0].source, FUENTE_HAPPYLAND)
        self.assertEqual(result[0].source_columns.get("comentario"), "ok")

    # ---- Deuda Sindical -----------------------------------------------------
    def test_deuda_sindical_fuente_y_centro_costo_en_metadata(self):
        filas = [self._fila(5, rut="25575228-6", nombre="ANTOINE, NERLANDE", centro_costo="SCJ", descuento="12000")]
        fuente, result = parsear_filas_por_fuente(filas, "deu26")
        self.assertEqual(result[0].source, FUENTE_DEUDA_SINDICAL)
        self.assertEqual(result[0].source_columns.get("centro_costo"), "SCJ")

    # ---- Fiesta / Cuota Extraordinaria --------------------------------------
    def test_cuota_extraordinaria_fuente_y_monto(self):
        filas = [self._fila(2, rut="10356317-8", nombre="ARRIAZA, GLADYS", cuota_extraor_sindicato="17000")]
        fuente, result = parsear_filas_por_fuente(filas, "fie26")
        self.assertEqual(result[0].source, FUENTE_CUOTA_EXTRAORDINARIA)
        self.assertEqual(result[0].monto_raw, "17000")

    # ---- DHL ----------------------------------------------------------------
    def test_dhl_fuente_monto_y_marca_confirmacion(self):
        filas = [self._fila(9, rut_socio="25180085-5", nombre_socio="ASCONA", total_a_pagar="75205", monto_recepcionado="0")]
        fuente, result = parsear_filas_por_fuente(filas, "dhl26")
        self.assertEqual(result[0].source, FUENTE_DESCUENTO_DHL)
        self.assertEqual(result[0].monto_raw, "75205")
        self.assertIn(REQUIERE_CONFIRMACION_CLIENTE, result[0].source_columns)
        # monto_recepcionado solo en metadata
        self.assertEqual(result[0].source_columns.get("monto_recepcionado"), "0")
        self.assertNotEqual(result[0].monto_raw, "0")

    def test_dhl_simple_rut_nombre_cuota_monto(self):
        """DHL simple (RUT, NOMBRE, CUOTA, MONTO) → fuente DHL, monto del campo MONTO."""
        filas = [self._fila(7, rut="18.701.664-9", nombre="PATRICIA VERA", cuota="4 DE 5", monto="62000")]
        fuente, result = parsear_filas_por_fuente(filas, "dhl26")
        self.assertEqual(result[0].source, FUENTE_DESCUENTO_DHL)
        self.assertEqual(result[0].monto_raw, "62000")
        self.assertIn(REQUIERE_CONFIRMACION_CLIENTE, result[0].source_columns)

    def test_telefonia_real_con_columna_total(self):
        """Planilla real jun 2026: RUT + Razon social + Total."""
        filas = [self._fila(2, rut="10356317-8", razon_social="ARRIAZA AQUEVEQUE, GLADYS", total="57000")]
        fuente, result = parsear_filas_por_fuente(filas, "tel26")
        self.assertEqual(result[0].source, FUENTE_TELEFONIA)
        self.assertEqual(result[0].monto_raw, "57000")

    # ---- OMI ----------------------------------------------------------------
    def test_omi_fuente_monto_cuota_y_marca_confirmacion(self):
        filas = [self._fila(11, rut_funcionario="21266983-0", nombre_funcionario="Danilo", monto_tratamiento="978300", valor_cuota="81525")]
        fuente, result = parsear_filas_por_fuente(filas, "omi26")
        self.assertEqual(result[0].source, FUENTE_CLINICA_OMI)
        self.assertEqual(result[0].monto_raw, "81525")
        self.assertIn(REQUIERE_CONFIRMACION_CLIENTE, result[0].source_columns)
        # monto_tratamiento no es el monto del descuento mensual
        self.assertNotEqual(result[0].monto_raw, "978300")
        self.assertEqual(result[0].source_columns.get("monto_tratamiento"), "978300")

    # ---- Prefijos automáticos de referencia ---------------------------------
    def test_referencias_auto_usan_prefijo_correcto_por_fuente(self):
        casos = [
            ({"rut": "1-9", "nombre": "A", "descuento": "1", "nombre_y_apellidos": "A"}, "GAS-"),
            ({"rut": "1-9", "nombre": "A", "cuotas": "1", "descuento": "1"}, "VET-"),
            ({"rut": "1-9", "nombre": "A", "descontar": "1", "cuotas": "1"}, "GYM-"),
            ({"rut": "1-9", "nombre": "A", "centro_costo": "X", "descuento": "1"}, "DEU-"),
            ({"rut": "1-9", "nombre": "A", "cuota_extraor_sindicato": "1"}, "FIE-"),
            ({"rut_socio": "1-9", "nombre_socio": "A", "total_a_pagar": "1"}, "DHL-"),
            ({"rut_funcionario": "1-9", "nombre_funcionario": "A", "valor_cuota": "1"}, "OMI-"),
        ]
        for row_extra, prefijo_esperado in casos:
            filas = [{"_fila": 1, **row_extra}]
            fuente, result = parsear_filas_por_fuente(filas, "tag")
            with self.subTest(prefijo=prefijo_esperado):
                self.assertTrue(
                    result[0].referencia_externa.startswith(prefijo_esperado),
                    f"Esperado prefijo '{prefijo_esperado}' pero ref='{result[0].referencia_externa}' (fuente={fuente})",
                )
