from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata

# ---------------------------------------------------------------------------
# Constantes de fuente
# ---------------------------------------------------------------------------

FUENTE_GAS = "GAS"
FUENTE_TELEFONIA = "TELEFONIA"
FUENTE_COPEUCH = "COPEUCH"
FUENTE_VETERINARIA = "VETERINARIA"
FUENTE_GIMNASIO = "GIMNASIO"
FUENTE_HAPPYLAND = "HAPPYLAND"
FUENTE_DEUDA_SINDICAL = "DEUDA_SINDICAL"
FUENTE_CUOTA_EXTRAORDINARIA = "CUOTA_EXTRAORDINARIA"
# DHL y OMI: regla de monto pendiente de confirmación del cliente.
# Se usan reglas temporales marcadas; no cerrar consolidado sin aprobación.
FUENTE_DESCUENTO_DHL = "DESCUENTO_DHL"
FUENTE_CLINICA_OMI = "CLINICA_OMI"
FUENTE_GENERICA = "GENERICA"

# Señal para marcar filas cuya regla de monto no está confirmada por el cliente.
REQUIERE_CONFIRMACION_CLIENTE = "REQUIERE_CONFIRMACION_CLIENTE"

# Prefijos para referencias automáticas por fuente.
_PREFIJO_FUENTE: dict[str, str] = {
    FUENTE_GAS: "GAS",
    FUENTE_TELEFONIA: "TEL",
    FUENTE_COPEUCH: "COP",
    FUENTE_VETERINARIA: "VET",
    FUENTE_GIMNASIO: "GYM",
    FUENTE_HAPPYLAND: "HLP",
    FUENTE_DEUDA_SINDICAL: "DEU",
    FUENTE_CUOTA_EXTRAORDINARIA: "FIE",
    FUENTE_DESCUENTO_DHL: "DHL",
    FUENTE_CLINICA_OMI: "OMI",
}


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def normalizar_header(text: str | None) -> str:
    value = (str(text or "").strip().lower())
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    # Normaliza separadores y puntuación a un único patrón de guion bajo.
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value


def _resolver_valor(row: dict, aliases: list[str]) -> str:
    for key in aliases:
        val = row.get(key)
        if val is not None and str(val).strip() != "":
            return str(val).strip()
    return ""


# ---------------------------------------------------------------------------
# Detección de fuente por encabezados normalizados
# ---------------------------------------------------------------------------

def detectar_fuente(headers: set[str]) -> str:
    """Detecta la fuente de la planilla a partir del conjunto de encabezados.

    El orden de evaluación importa: las fuentes más específicas van primero
    para evitar falsos positivos sobre la fuente GENERICA.
    """
    headers_norm = {normalizar_header(h) for h in headers}

    # ---- Copeuch (tiene columnas financieras únicas) ----
    if "rut" in headers_norm and (
        "tot_dctos" in headers_norm
        or "total_descuentos" in headers_norm
        or "total_dctos" in headers_norm
        or "tot_dcto" in headers_norm
        or "total_dcto" in headers_norm
    ) and "nombre" in headers_norm:
        return FUENTE_COPEUCH

    # ---- Telefonía ----
    # Señal primaria: cargo_fijo (planillas con columna explícita de cargo).
    # Señal secundaria: razon_social + total (planilla real del cliente junio 2026
    # usa "Razon social" y "Total" en lugar de "Cargo Fijo").
    if "rut" in headers_norm and (
        "cargo_fijo" in headers_norm
        or ("razon_social" in headers_norm and "total" in headers_norm)
    ) and (
        "razon_social" in headers_norm or "nombre" in headers_norm
    ):
        return FUENTE_TELEFONIA

    # ---- Clínica OMI (presupuesto + beneficiario + funcionario) ----
    if (
        "rut_funcionario" in headers_norm
        or "numero_de_presupuesto" in headers_norm
    ) and (
        "monto_tratamiento" in headers_norm
        or "valor_cuota" in headers_norm
    ):
        return FUENTE_CLINICA_OMI

    # ---- DHL planilla envío (crédito con columnas de capital/ahorro) ----
    if "rut_socio" in headers_norm and (
        "total_a_pagar" in headers_norm
        or "monto_recepcionado" in headers_norm
        or "_valor_cuota" in headers_norm
        or "valor_cuota" in headers_norm
    ):
        return FUENTE_DESCUENTO_DHL

    # ---- Fiesta / Cuota Extraordinaria ----
    if "rut" in headers_norm and (
        "cuota_extraor_sindicato" in headers_norm
        or "cuota_extraordinaria" in headers_norm
        or "cuota_extraor" in headers_norm
    ):
        return FUENTE_CUOTA_EXTRAORDINARIA

    # ---- Descuento DHL simple (RUT + NOMBRE + CUOTA + MONTO sin columnas de crédito) ----
    # Esta planilla tiene estructura mínima y no trae Rut Socio/Total A Pagar.
    # Se detecta por la combinación de "cuota" (texto libre) + "monto" + ausencia de señales de crédito.
    # Nota: no confundir con FUENTE_CUOTA_EXTRAORDINARIA (que tiene cuota_extraor_sindicato).
    if "rut" in headers_norm and "cuota" in headers_norm and "monto" in headers_norm and (
        "nombre" in headers_norm
    ) and "tot_dctos" not in headers_norm and "cargo_fijo" not in headers_norm:
        return FUENTE_DESCUENTO_DHL

    # ---- Deuda Sindical (tiene centro_costo) ----
    if "rut" in headers_norm and "centro_costo" in headers_norm and (
        "descuento" in headers_norm or "monto" in headers_norm
    ):
        return FUENTE_DEUDA_SINDICAL

    # ---- Gym (DESCONTAR es señal específica; excluye DHL simple que no tiene descontar) ----
    if "rut" in headers_norm and "descontar" in headers_norm and (
        "nombre" in headers_norm or "cuotas" in headers_norm
    ):
        return FUENTE_GIMNASIO

    # ---- Happyland (CUOTA + COMENTARIO + DESCUENTO sin centro_costo) ----
    if "rut" in headers_norm and "comentario" in headers_norm and (
        "descuento" in headers_norm or "cuota" in headers_norm
    ) and "nombre" in headers_norm:
        return FUENTE_HAPPYLAND

    # ---- Veterinaria (DESCUENTO + CUOTAS sin otras señales) ----
    if "rut" in headers_norm and "cuotas" in headers_norm and (
        "descuento" in headers_norm
    ) and "nombre" in headers_norm:
        return FUENTE_VETERINARIA

    # ---- Gas (monto o descuento + nombre) ----
    # Acepta tanto "monto" como "descuento" (planillas reales del cliente usan "Descuento").
    # Acepta tanto "nombre_apellido" como "nombre_y_apellidos" / "nombre".
    if "rut" in headers_norm and (
        "monto" in headers_norm
        or "descuento" in headers_norm
    ) and (
        "nombre_apellido" in headers_norm
        or "nombre_y_apellidos" in headers_norm
        or "nombre" in headers_norm
    ):
        return FUENTE_GAS

    return FUENTE_GENERICA


# ---------------------------------------------------------------------------
# Dataclass de fila parseada
# ---------------------------------------------------------------------------

@dataclass
class FilaFuente:
    fila: int
    source: str
    rut_raw: str
    nombre: str
    monto_raw: str
    observacion: str
    referencia_externa: str
    referencia_informada: bool
    source_columns: dict


# ---------------------------------------------------------------------------
# Utilidades internas
# ---------------------------------------------------------------------------

def _build_auto_ref(source: str, source_tag: str, fila: int) -> str:
    prefijo = _PREFIJO_FUENTE.get(source, "SRC")
    return f"{prefijo}-{source_tag}-{fila}"


# ---------------------------------------------------------------------------
# Mapeo de fila por fuente
# ---------------------------------------------------------------------------

def _mapear_fila(row: dict, source: str, source_tag: str) -> FilaFuente:  # noqa: C901
    fila = row.get("_fila", "?")

    # ---- Gas ----------------------------------------------------------------
    if source == FUENTE_GAS:
        rut_raw = _resolver_valor(row, ["rut"])
        nombre = _resolver_valor(row, [
            "nombre_apellido", "nombre_y_apellidos", "nombre_y_apellido",
            "nombre", "socio", "nombre_socio",
        ])
        # Planillas reales del cliente usan "Descuento"; también acepta "Monto".
        monto_raw = _resolver_valor(row, ["descuento", "monto", "valor"])
        observacion = _resolver_valor(row, ["observacion", "observaciones"])
        referencia = _resolver_valor(row, ["referencia_externa", "referencia", "folio"])
        extras = []
        site = _resolver_valor(row, ["site"])
        vale = _resolver_valor(row, ["vale_de_gas", "tipo_de_vale", "tipo_vale"])
        if site:
            extras.append(f"Site: {site}")
        if vale:
            extras.append(f"Vale gas: {vale}")
        if extras:
            observacion = f"{observacion} | {' | '.join(extras)}".strip(" |")
        source_columns = {
            "rut": rut_raw,
            "nombre_apellido": nombre,
            "site": site,
            "vale_de_gas": vale,
            "monto": monto_raw,
        }

    # ---- Telefonía ----------------------------------------------------------
    elif source == FUENTE_TELEFONIA:
        rut_raw = _resolver_valor(row, ["rut"])
        nombre = _resolver_valor(row, ["razon_social", "nombre", "socio", "nombre_socio"])
        # Planilla real usa "Total"; también soporta "cargo_fijo" para planillas clásicas.
        monto_raw = _resolver_valor(row, ["cargo_fijo", "total", "monto", "valor"])
        observacion = _resolver_valor(row, ["observacion", "observaciones"])
        referencia = _resolver_valor(row, ["referencia_externa", "referencia", "folio", "cuenta"])
        extras = []
        for campo, etiqueta in (
            ("cuenta", "Cuenta"),
            ("pcs", "PCS"),
            ("fecha_de_entrega", "Fecha entrega"),
            ("fecha_entrega", "Fecha entrega"),
        ):
            valor = _resolver_valor(row, [campo])
            if valor:
                extras.append(f"{etiqueta}: {valor}")
        if extras:
            observacion = f"{observacion} | {' | '.join(extras)}".strip(" |")
        source_columns = {
            "rut": rut_raw,
            "razon_social": nombre,
            "cuenta": _resolver_valor(row, ["cuenta"]),
            "pcs": _resolver_valor(row, ["pcs"]),
            "cargo_fijo": monto_raw,
            "fecha_entrega": _resolver_valor(row, ["fecha_de_entrega", "fecha_entrega"]),
        }

    # ---- Copeuch ------------------------------------------------------------
    elif source == FUENTE_COPEUCH:
        rut_raw = _resolver_valor(row, ["rut"])
        nombre = _resolver_valor(row, ["nombre", "razon_social", "socio", "nombre_socio"])
        monto_raw = _resolver_valor(row, [
            "tot_dctos", "total_descuentos", "total_dctos",
            "tot_dcto", "total_dcto", "monto", "valor",
        ])
        observacion = _resolver_valor(row, ["observacion", "observaciones"])
        referencia = _resolver_valor(row, ["referencia_externa", "referencia", "folio"])
        extras = []
        for campo, etiqueta in (
            ("fec_ing_socio", "Fecha ingreso socio"),
            ("fecha_ingreso_socio", "Fecha ingreso socio"),
            ("acciones", "Acciones"),
            ("prestamos", "Prestamos"),
        ):
            valor = _resolver_valor(row, [campo])
            if valor:
                extras.append(f"{etiqueta}: {valor}")
        if extras:
            observacion = f"{observacion} | {' | '.join(extras)}".strip(" |")
        source_columns = {
            "rut": rut_raw,
            "nombre": nombre,
            "fecha_ingreso_socio": _resolver_valor(row, ["fec_ing_socio", "fecha_ingreso_socio"]),
            "acciones": _resolver_valor(row, ["acciones"]),
            "prestamos": _resolver_valor(row, ["prestamos"]),
            "total_descuentos": monto_raw,
        }

    # ---- Veterinaria --------------------------------------------------------
    elif source == FUENTE_VETERINARIA:
        rut_raw = _resolver_valor(row, ["rut"])
        nombre = _resolver_valor(row, ["nombre", "socio", "nombre_socio"])
        monto_raw = _resolver_valor(row, ["descuento", "monto", "valor"])
        observacion = _resolver_valor(row, ["observacion", "observaciones"])
        referencia = _resolver_valor(row, ["referencia_externa", "referencia", "folio"])
        cuotas = _resolver_valor(row, ["cuotas", "cuota"])
        if cuotas:
            observacion = f"{observacion} | Cuotas: {cuotas}".strip(" |")
        source_columns = {
            "rut": rut_raw,
            "nombre": nombre,
            "cuotas": cuotas,
            "descuento": monto_raw,
        }

    # ---- Gimnasio -----------------------------------------------------------
    elif source == FUENTE_GIMNASIO:
        rut_raw = _resolver_valor(row, ["rut"])
        nombre = _resolver_valor(row, ["nombre", "socio", "nombre_socio"])
        # Planilla real usa "DESCONTAR"
        monto_raw = _resolver_valor(row, ["descontar", "descuento", "monto", "valor"])
        observacion = _resolver_valor(row, ["observacion", "observaciones"])
        referencia = _resolver_valor(row, ["referencia_externa", "referencia", "folio"])
        cuotas = _resolver_valor(row, ["cuotas", "cuota"])
        if cuotas:
            observacion = f"{observacion} | Cuotas: {cuotas}".strip(" |")
        source_columns = {
            "rut": rut_raw,
            "nombre": nombre,
            "cuotas": cuotas,
            "descontar": monto_raw,
        }

    # ---- Happyland ----------------------------------------------------------
    elif source == FUENTE_HAPPYLAND:
        rut_raw = _resolver_valor(row, ["rut"])
        nombre = _resolver_valor(row, ["nombre", "socio", "nombre_socio"])
        monto_raw = _resolver_valor(row, ["descuento", "monto", "valor"])
        observacion = _resolver_valor(row, ["observacion", "observaciones"])
        referencia = _resolver_valor(row, ["referencia_externa", "referencia", "folio"])
        cuota = _resolver_valor(row, ["cuota", "cuotas"])
        comentario = _resolver_valor(row, ["comentario", "observaciones"])
        extras = []
        if cuota:
            extras.append(f"Cuota: {cuota}")
        if comentario:
            extras.append(f"Comentario: {comentario}")
        if extras:
            observacion = f"{observacion} | {' | '.join(extras)}".strip(" |")
        source_columns = {
            "rut": rut_raw,
            "nombre": nombre,
            "cuota": cuota,
            "comentario": comentario,
            "descuento": monto_raw,
        }

    # ---- Deuda Sindical -----------------------------------------------------
    elif source == FUENTE_DEUDA_SINDICAL:
        rut_raw = _resolver_valor(row, ["rut"])
        nombre = _resolver_valor(row, ["nombre", "socio", "nombre_socio"])
        monto_raw = _resolver_valor(row, ["descuento", "monto", "valor"])
        observacion = _resolver_valor(row, ["observacion", "observaciones"])
        referencia = _resolver_valor(row, ["referencia_externa", "referencia", "folio"])
        centro_costo = _resolver_valor(row, ["centro_costo", "centro"])
        comentario = _resolver_valor(row, ["comentario", "comentarios"])
        extras = []
        if centro_costo:
            extras.append(f"Centro costo: {centro_costo}")
        if comentario:
            extras.append(f"Comentario: {comentario}")
        if extras:
            observacion = f"{observacion} | {' | '.join(extras)}".strip(" |")
        source_columns = {
            "rut": rut_raw,
            "nombre": nombre,
            "centro_costo": centro_costo,
            "comentario": comentario,
            "descuento": monto_raw,
        }

    # ---- Cuota Extraordinaria (Fiesta) --------------------------------------
    elif source == FUENTE_CUOTA_EXTRAORDINARIA:
        rut_raw = _resolver_valor(row, ["rut"])
        nombre = _resolver_valor(row, ["nombre", "socio", "nombre_socio"])
        # Planilla real usa "Cuota Extraor.Sindicato"
        monto_raw = _resolver_valor(row, [
            "cuota_extraor_sindicato", "cuota_extraordinaria",
            "cuota_extraor", "monto", "valor",
        ])
        observacion = _resolver_valor(row, ["observacion", "observaciones"])
        referencia = _resolver_valor(row, ["referencia_externa", "referencia", "folio"])
        source_columns = {
            "rut": rut_raw,
            "nombre": nombre,
            "cuota_extraordinaria": monto_raw,
        }

    # ---- Descuento DHL (planilla envío) -------------------------------------
    # REGLA TEMPORAL PENDIENTE DE CONFIRMACIÓN DEL CLIENTE.
    # Dos variantes de planilla DHL conviven:
    # A) Planilla envío (crédito): Rut Socio, Nombre Socio, Total A Pagar, Monto Recepcionado...
    # B) Planilla simple: RUT, NOMBRE, CUOTA, MONTO (sin columnas de crédito).
    # En ambos casos se usa el monto nominal como descuento hasta confirmación cliente.
    elif source == FUENTE_DESCUENTO_DHL:
        rut_raw = _resolver_valor(row, ["rut_socio", "rut"])
        nombre = _resolver_valor(row, ["nombre_socio", "nombre", "socio"])
        # Variante A: total_a_pagar; Variante B: monto/cuota.
        monto_raw = _resolver_valor(row, ["total_a_pagar", "_valor_cuota", "valor_cuota", "monto", "cuota"])
        observacion = _resolver_valor(row, ["observacion", "observaciones"])
        referencia = _resolver_valor(row, [
            "referencia_externa", "n_credito", "n__credito", "referencia", "folio",
        ])
        monto_recepcionado = _resolver_valor(row, ["monto_recepcionado"])
        valor_cuota = _resolver_valor(row, ["_valor_cuota", "valor_cuota"])
        capital = _resolver_valor(row, ["_capital"])
        cuota_gastos = _resolver_valor(row, ["_cuota_gastos"])
        ahorro = _resolver_valor(row, ["_ahorro"])
        plazo = _resolver_valor(row, ["plazo_credito"])
        nro_credito = _resolver_valor(row, ["n_credito", "n__credito"])
        cuota_texto = _resolver_valor(row, ["cuota"])
        source_columns = {
            "rut_socio": rut_raw,
            "nombre_socio": nombre,
            "total_a_pagar": monto_raw,
            "valor_cuota": valor_cuota,
            "monto_recepcionado": monto_recepcionado,
            "capital": capital,
            "cuota_gastos": cuota_gastos,
            "ahorro": ahorro,
            "plazo_credito": plazo,
            "nro_credito": nro_credito,
            "cuota_texto": cuota_texto,
            REQUIERE_CONFIRMACION_CLIENTE: "monto_dhl_pendiente_confirmacion",
        }

    # ---- Clínica OMI --------------------------------------------------------
    # REGLA TEMPORAL PENDIENTE DE CONFIRMACIÓN DEL CLIENTE.
    # Se usa "valor_cuota" como descuento mensual hasta confirmación.
    # "monto_tratamiento" se guarda solo en metadata como referencia de deuda total.
    elif source == FUENTE_CLINICA_OMI:
        rut_raw = _resolver_valor(row, ["rut_funcionario", "rut"])
        nombre_funcionario = _resolver_valor(row, ["nombre_funcionario", "nombre"])
        apellido_funcionario = _resolver_valor(row, ["apellido_funcionario"])
        nombre = f"{nombre_funcionario} {apellido_funcionario}".strip() or nombre_funcionario
        # Regla temporal: valor_cuota es el descuento mensual hasta confirmación cliente.
        monto_raw = _resolver_valor(row, ["valor_cuota", "monto", "monto_tratamiento"])
        observacion = _resolver_valor(row, ["observacion", "observaciones"])
        referencia = _resolver_valor(row, [
            "referencia_externa", "numero_de_presupuesto", "referencia", "folio",
        ])
        monto_tratamiento = _resolver_valor(row, ["monto_tratamiento"])
        numero_cuota = _resolver_valor(row, ["numero_de_cuota"])
        nombre_beneficiario = _resolver_valor(row, ["nombre_beneficiario"])
        apellido_beneficiario = _resolver_valor(row, ["apellido_beneficiario"])
        presupuesto = _resolver_valor(row, ["numero_de_presupuesto"])
        source_columns = {
            "rut_funcionario": rut_raw,
            "nombre_funcionario": nombre,
            "monto_tratamiento": monto_tratamiento,
            "valor_cuota": monto_raw,
            "numero_cuota": numero_cuota,
            "nombre_beneficiario": f"{nombre_beneficiario} {apellido_beneficiario}".strip(),
            "numero_presupuesto": presupuesto,
            REQUIERE_CONFIRMACION_CLIENTE: "monto_omi_pendiente_confirmacion",
        }

    # ---- Genérica (fallback) ------------------------------------------------
    else:
        rut_raw = _resolver_valor(row, ["rut"])
        nombre = _resolver_valor(row, ["nombre", "socio", "nombre_socio"])
        monto_raw = _resolver_valor(row, ["monto", "valor", "descuento"])
        observacion = _resolver_valor(row, ["observacion", "observaciones"])
        referencia = _resolver_valor(row, ["referencia_externa", "referencia", "folio"])
        source_columns = {
            "rut": rut_raw,
            "nombre": nombre,
            "monto": monto_raw,
        }

    referencia_informada = bool(referencia)
    if not referencia:
        referencia = _build_auto_ref(source, source_tag, int(fila))

    return FilaFuente(
        fila=int(fila),
        source=source,
        rut_raw=rut_raw,
        nombre=nombre,
        monto_raw=monto_raw,
        observacion=observacion,
        referencia_externa=referencia,
        referencia_informada=referencia_informada,
        source_columns=source_columns,
    )


# ---------------------------------------------------------------------------
# Punto de entrada público
# ---------------------------------------------------------------------------

def parsear_filas_por_fuente(filas: list[dict], source_tag: str) -> tuple[str, list[FilaFuente]]:
    if not filas:
        return FUENTE_GENERICA, []

    headers = set()
    for fila in filas:
        headers.update(k for k in fila.keys() if k != "_fila")

    fuente = detectar_fuente(headers)
    mapped = [_mapear_fila(fila, fuente, source_tag) for fila in filas]
    return fuente, mapped
