from __future__ import annotations

from dataclasses import dataclass


FUENTE_GAS = "GAS"
FUENTE_TELEFONIA = "TELEFONIA"
FUENTE_COPEUCH = "COPEUCH"
FUENTE_GENERICA = "GENERICA"


def normalizar_header(text: str | None) -> str:
    value = (str(text or "").strip().lower())
    value = (
        value.replace("a", "a")
        .replace("e", "e")
        .replace("i", "i")
        .replace("o", "o")
        .replace("u", "u")
        .replace("n", "n")
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace("ñ", "n")
    )
    return value.replace(" ", "_").replace("-", "_").replace(".", "")


def _resolver_valor(row: dict, aliases: list[str]) -> str:
    for key in aliases:
        val = row.get(key)
        if val is not None and str(val).strip() != "":
            return str(val).strip()
    return ""


def detectar_fuente(headers: set[str]) -> str:
    headers_norm = {normalizar_header(h) for h in headers}

    if {
        "rut",
        "nombre_apellido",
        "monto",
    }.issubset(headers_norm):
        return FUENTE_GAS

    if "rut" in headers_norm and "cargo_fijo" in headers_norm and (
        "razon_social" in headers_norm or "nombre" in headers_norm
    ):
        return FUENTE_TELEFONIA

    if "rut" in headers_norm and (
        "tot_dctos" in headers_norm or "total_descuentos" in headers_norm
    ) and "nombre" in headers_norm:
        return FUENTE_COPEUCH

    return FUENTE_GENERICA


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


def _build_auto_ref(source: str, source_tag: str, fila: int) -> str:
    prefijo = {
        FUENTE_GAS: "GAS",
        FUENTE_TELEFONIA: "TEL",
        FUENTE_COPEUCH: "COP",
    }.get(source, "SRC")
    return f"{prefijo}-{source_tag}-{fila}"


def _mapear_fila(row: dict, source: str, source_tag: str) -> FilaFuente:
    fila = row.get("_fila", "?")

    if source == FUENTE_GAS:
        rut_raw = _resolver_valor(row, ["rut"])
        nombre = _resolver_valor(row, ["nombre_apellido", "nombre", "socio", "nombre_socio"])
        monto_raw = _resolver_valor(row, ["monto", "valor"])
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
    elif source == FUENTE_TELEFONIA:
        rut_raw = _resolver_valor(row, ["rut"])
        nombre = _resolver_valor(row, ["razon_social", "nombre", "socio", "nombre_socio"])
        monto_raw = _resolver_valor(row, ["cargo_fijo", "monto", "valor"])
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
    elif source == FUENTE_COPEUCH:
        rut_raw = _resolver_valor(row, ["rut"])
        nombre = _resolver_valor(row, ["nombre", "razon_social", "socio", "nombre_socio"])
        monto_raw = _resolver_valor(row, ["tot_dctos", "total_descuentos", "monto", "valor"])
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
    else:
        rut_raw = _resolver_valor(row, ["rut"])
        nombre = _resolver_valor(row, ["nombre", "socio", "nombre_socio"])
        monto_raw = _resolver_valor(row, ["monto", "valor"])
        observacion = _resolver_valor(row, ["observacion", "observaciones"])
        referencia = _resolver_valor(row, ["referencia_externa", "referencia", "folio"])

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
    )


def parsear_filas_por_fuente(filas: list[dict], source_tag: str) -> tuple[str, list[FilaFuente]]:
    if not filas:
        return FUENTE_GENERICA, []

    headers = set()
    for fila in filas:
        headers.update(k for k in fila.keys() if k != "_fila")

    fuente = detectar_fuente(headers)
    mapped = [_mapear_fila(fila, fuente, source_tag) for fila in filas]
    return fuente, mapped
