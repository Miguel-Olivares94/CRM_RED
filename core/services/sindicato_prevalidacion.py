from __future__ import annotations

from dataclasses import dataclass
import re

from core.models import AuditoriaSindicato, MovimientoSindicato, SocioSindicato


RE_LICENCIA = re.compile(r"licencia\s+medica|licencia\s+m[eé]dica", re.IGNORECASE)
RE_DESPEDIDO = re.compile(r"despedido", re.IGNORECASE)
RE_BAJA = re.compile(r"\bbaja\b", re.IGNORECASE)


@dataclass
class PrevalidacionResultado:
    periodo: str
    total_movimientos_revisados: int
    observados_licencia: int
    excluidos_baja_despedido: int
    socios_actualizados: int
    detalle: list[dict]


def _texto_movimiento(mov: MovimientoSindicato) -> str:
    base = (mov.observacion or "").strip()
    cols = mov.metadata_fuente.get("source_columns") if isinstance(mov.metadata_fuente, dict) else {}
    if not isinstance(cols, dict):
        cols = {}
    values = [str(v).strip() for v in cols.values() if str(v).strip()]
    if values:
        return f"{base} | {' | '.join(values)}"
    return base


def prevalidar_movimientos_para_consolidado(*, empresa, periodo: str, usuario=None) -> PrevalidacionResultado:
    movimientos = list(
        MovimientoSindicato.objects.select_related("socio")
        .filter(empresa=empresa, periodo=periodo)
        .order_by("id")
    )

    observados_licencia = 0
    excluidos_baja_despedido = 0
    socios_actualizados = 0
    detalle = []

    for mov in movimientos:
        texto = _texto_movimiento(mov)
        if not texto:
            continue

        socio = mov.socio

        if RE_DESPEDIDO.search(texto) or RE_BAJA.search(texto):
            excluidos_baja_despedido += 1
            if mov.estado != MovimientoSindicato.ESTADO_RECHAZADO:
                mov.estado = MovimientoSindicato.ESTADO_RECHAZADO
                mov.save(update_fields=["estado", "updated_at"])
            if socio.estado_laboral != SocioSindicato.ESTADO_LABORAL_DESVINCULADO:
                socio.estado_laboral = SocioSindicato.ESTADO_LABORAL_DESVINCULADO
                socio.save(update_fields=["estado_laboral", "updated_at"])
                socios_actualizados += 1
            detalle.append(
                {
                    "movimiento_id": mov.id,
                    "rut": socio.rut,
                    "accion": "EXCLUIDO_BAJA_DESPEDIDO",
                }
            )
            continue

        if RE_LICENCIA.search(texto):
            observados_licencia += 1
            if mov.estado != MovimientoSindicato.ESTADO_OBSERVADO:
                mov.estado = MovimientoSindicato.ESTADO_OBSERVADO
                mov.save(update_fields=["estado", "updated_at"])
            if socio.estado_laboral == SocioSindicato.ESTADO_LABORAL_ACTIVO:
                socio.estado_laboral = SocioSindicato.ESTADO_LABORAL_LICENCIA
                socio.save(update_fields=["estado_laboral", "updated_at"])
                socios_actualizados += 1
            detalle.append(
                {
                    "movimiento_id": mov.id,
                    "rut": socio.rut,
                    "accion": "OBSERVADO_LICENCIA_MEDICA",
                }
            )

    AuditoriaSindicato.objects.create(
        empresa=empresa,
        usuario=usuario,
        accion="PREVALIDAR_CONSOLIDADO",
        entidad="MovimientoSindicato",
        entidad_id=f"{empresa.id}:{periodo}"[:40],
        periodo=periodo,
        resumen=(
            f"PREVALIDAR {periodo} | revisados={len(movimientos)} | "
            f"licencia={observados_licencia} | excluidos={excluidos_baja_despedido}"
        )[:255],
        payload={
            "periodo": periodo,
            "total_movimientos_revisados": len(movimientos),
            "observados_licencia": observados_licencia,
            "excluidos_baja_despedido": excluidos_baja_despedido,
            "socios_actualizados": socios_actualizados,
            "detalle": detalle[:200],
        },
    )

    return PrevalidacionResultado(
        periodo=periodo,
        total_movimientos_revisados=len(movimientos),
        observados_licencia=observados_licencia,
        excluidos_baja_despedido=excluidos_baja_despedido,
        socios_actualizados=socios_actualizados,
        detalle=detalle,
    )
