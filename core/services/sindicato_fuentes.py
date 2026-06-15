from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata


FUENTE_GAS = "GAS"
FUENTE_TELEFONIA = "TELEFONIA"
FUENTE_COPEUCH = "COPEUCH"
FUENTE_GENERICA = "GENERICA"


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


def detectar_fuente(headers: set[str]) -> str:
    headers_norm = {normalizar_header(h) for h in headers}

    if "rut" in headers_norm and "monto" in headers_norm and (
        "nombre_apellido" in headers_norm or "nombre" in headers_norm
    ):
        return FUENTE_GAS

    if "rut" in headers_norm and "cargo_fijo" in headers_norm and (
        "razon_social" in headers_norm or "nombre" in headers_norm
    ):
        return FUENTE_TELEFONIA

    if "rut" in headers_norm and (
        "tot_dctos" in headers_norm
        or "total_descuentos" in headers_norm
        or "total_dctos" in headers_norm
        or "tot_dcto" in headers_norm
        or "total_dcto" in headers_norm
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
    source_columns: dict


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
        source_columns = {
            "rut": rut_raw,
            "nombre_apellido": nombre,
            "site": site,
            "vale_de_gas": vale,
            "monto": monto_raw,
        }
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
        source_columns = {
            "rut": rut_raw,
            "razon_social": nombre,
            "cuenta": _resolver_valor(row, ["cuenta"]),
            "pcs": _resolver_valor(row, ["pcs"]),
            "cargo_fijo": monto_raw,
            "fecha_entrega": _resolver_valor(row, ["fecha_de_entrega", "fecha_entrega"]),
        }
    elif source == FUENTE_COPEUCH:
        rut_raw = _resolver_valor(row, ["rut"])
        nombre = _resolver_valor(row, ["nombre", "razon_social", "socio", "nombre_socio"])
        monto_raw = _resolver_valor(
            row,
            [
                "tot_dctos",
                "total_descuentos",
                "total_dctos",
                "tot_dcto",
                "total_dcto",
                "monto",
                "valor",
            ],
        )
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
    else:
        rut_raw = _resolver_valor(row, ["rut"])
        nombre = _resolver_valor(row, ["nombre", "socio", "nombre_socio"])
        monto_raw = _resolver_valor(row, ["monto", "valor"])
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


def parsear_filas_por_fuente(filas: list[dict], source_tag: str) -> tuple[str, list[FilaFuente]]:
    if not filas:
        return FUENTE_GENERICA, []

    headers = set()
    for fila in filas:
        headers.update(k for k in fila.keys() if k != "_fila")

    fuente = detectar_fuente(headers)
    mapped = [_mapear_fila(fila, fuente, source_tag) for fila in filas]
    return fuente, mapped
