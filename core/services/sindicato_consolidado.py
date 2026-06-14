from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import re

from django.db import transaction
from django.utils import timezone

from core.models import (
    AuditoriaSindicato,
    ConsolidadoDetalleSindicato,
    ConsolidadoMensualSindicato,
    MovimientoSindicato,
    SocioSindicato,
    TipoBeneficioSindicato,
)

PERIODO_REGEX = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


class ConsolidadoBloqueadoError(Exception):
    pass


class ConsolidadoNoExisteError(Exception):
    pass


@dataclass
class ConsolidadoResultado:
    consolidado_id: int
    accion: str
    periodo: str
    total_socios: int
    total_monto: Decimal
    total_movimientos_origen: int
    total_detalles_generados: int
    excluidos_rechazados: int
    excluidos_desvinculados: int
    excluidos_beneficio_inactivo: int
    observados_licencia: int
    observados_movimiento: int


def _motivo_to_str(values: set[str]) -> str:
    if not values:
        return ""
    return " | ".join(sorted(values))


@transaction.atomic
def generar_o_recalcular_consolidado(*, empresa, periodo: str, usuario=None) -> ConsolidadoResultado:
    if not PERIODO_REGEX.match(periodo or ""):
        raise ValueError("Periodo inválido. Usa formato YYYY-MM.")

    consolidado, created = ConsolidadoMensualSindicato.objects.get_or_create(
        empresa=empresa,
        periodo=periodo,
        defaults={
            "estado": ConsolidadoMensualSindicato.ESTADO_ABIERTO,
            "fecha_generacion": timezone.now(),
            "total_socios": 0,
            "total_monto": Decimal("0"),
        },
    )

    if consolidado.estado in (
        ConsolidadoMensualSindicato.ESTADO_CERRADO,
        ConsolidadoMensualSindicato.ESTADO_EXPORTADO,
    ):
        raise ConsolidadoBloqueadoError("El período está cerrado o exportado y no permite recálculo.")

    accion = "GENERAR_CONSOLIDADO" if created else "RECALCULAR_CONSOLIDADO"

    # Idempotencia: siempre reconstruye desde cero el detalle del período.
    ConsolidadoDetalleSindicato.objects.filter(consolidado=consolidado).delete()

    movimientos_qs = (
        MovimientoSindicato.objects.select_related("socio", "tipo_beneficio")
        .filter(empresa=empresa, periodo=periodo)
        .order_by("id")
    )

    total_movimientos_origen = movimientos_qs.count()

    excluidos_rechazados = 0
    excluidos_desvinculados = 0
    excluidos_beneficio_inactivo = 0
    observados_licencia = 0
    observados_movimiento = 0

    aggregation = {}

    for mov in movimientos_qs:
        if mov.estado == MovimientoSindicato.ESTADO_RECHAZADO:
            excluidos_rechazados += 1
            continue

        socio = mov.socio
        beneficio = mov.tipo_beneficio

        if socio.empresa_id != empresa.id or beneficio.empresa_id != empresa.id:
            # Dato inconsistente, se descarta por seguridad de tenant.
            continue

        if socio.estado_laboral == SocioSindicato.ESTADO_LABORAL_DESVINCULADO:
            excluidos_desvinculados += 1
            continue

        if beneficio.estado != TipoBeneficioSindicato.ESTADO_ACTIVO:
            excluidos_beneficio_inactivo += 1
            continue

        key = (socio.id, beneficio.id)
        if key not in aggregation:
            aggregation[key] = {
                "socio": socio,
                "beneficio": beneficio,
                "monto": Decimal("0"),
                "motivos": set(),
            }

        aggregation[key]["monto"] += mov.monto

        if socio.estado_laboral == SocioSindicato.ESTADO_LABORAL_LICENCIA:
            aggregation[key]["motivos"].add("SOCIO_LICENCIA_MEDICA")
            observados_licencia += 1

        if mov.estado == MovimientoSindicato.ESTADO_OBSERVADO:
            aggregation[key]["motivos"].add("MOVIMIENTO_OBSERVADO")
            observados_movimiento += 1

    detalles = []
    socios_incluidos = set()
    total_monto = Decimal("0")

    for (socio_id, _benef_id), item in aggregation.items():
        monto = item["monto"]
        total_monto += monto
        socios_incluidos.add(socio_id)
        detalles.append(
            ConsolidadoDetalleSindicato(
                empresa=empresa,
                consolidado=consolidado,
                socio=item["socio"],
                tipo_beneficio=item["beneficio"],
                monto_aprobado=monto,
                motivo_ajuste=_motivo_to_str(item["motivos"]),
            )
        )

    if detalles:
        ConsolidadoDetalleSindicato.objects.bulk_create(detalles)

    consolidado.total_socios = len(socios_incluidos)
    consolidado.total_monto = total_monto
    consolidado.fecha_generacion = timezone.now()
    consolidado.save(update_fields=["total_socios", "total_monto", "fecha_generacion", "updated_at"])

    AuditoriaSindicato.objects.create(
        empresa=empresa,
        usuario=usuario,
        accion=accion,
        entidad="ConsolidadoMensualSindicato",
        entidad_id=str(consolidado.id),
        periodo=periodo,
        resumen=(
            f"{accion} {periodo} | socios={consolidado.total_socios} | "
            f"detalles={len(detalles)} | monto={int(total_monto)}"
        )[:255],
        payload={
            "periodo": periodo,
            "total_movimientos_origen": total_movimientos_origen,
            "total_detalles_generados": len(detalles),
            "total_socios": consolidado.total_socios,
            "total_monto": int(total_monto),
            "excluidos_rechazados": excluidos_rechazados,
            "excluidos_desvinculados": excluidos_desvinculados,
            "excluidos_beneficio_inactivo": excluidos_beneficio_inactivo,
            "observados_licencia": observados_licencia,
            "observados_movimiento": observados_movimiento,
        },
    )

    return ConsolidadoResultado(
        consolidado_id=consolidado.id,
        accion=accion,
        periodo=periodo,
        total_socios=consolidado.total_socios,
        total_monto=consolidado.total_monto,
        total_movimientos_origen=total_movimientos_origen,
        total_detalles_generados=len(detalles),
        excluidos_rechazados=excluidos_rechazados,
        excluidos_desvinculados=excluidos_desvinculados,
        excluidos_beneficio_inactivo=excluidos_beneficio_inactivo,
        observados_licencia=observados_licencia,
        observados_movimiento=observados_movimiento,
    )


@transaction.atomic
def recalcular_consolidado_abierto(*, empresa, periodo: str, usuario=None) -> ConsolidadoResultado:
    if not PERIODO_REGEX.match(periodo or ""):
        raise ValueError("Periodo inválido. Usa formato YYYY-MM.")

    try:
        consolidado = ConsolidadoMensualSindicato.objects.get(empresa=empresa, periodo=periodo)
    except ConsolidadoMensualSindicato.DoesNotExist as exc:
        raise ConsolidadoNoExisteError("No existe consolidado para ese período.") from exc

    if consolidado.estado != ConsolidadoMensualSindicato.ESTADO_ABIERTO:
        raise ConsolidadoBloqueadoError("Solo se puede recalcular un consolidado en estado ABIERTO.")

    return generar_o_recalcular_consolidado(empresa=empresa, periodo=periodo, usuario=usuario)


@transaction.atomic
def cerrar_consolidado_periodo(*, empresa, periodo: str, usuario=None) -> ConsolidadoMensualSindicato:
    if not PERIODO_REGEX.match(periodo or ""):
        raise ValueError("Periodo inválido. Usa formato YYYY-MM.")

    try:
        consolidado = ConsolidadoMensualSindicato.objects.get(empresa=empresa, periodo=periodo)
    except ConsolidadoMensualSindicato.DoesNotExist as exc:
        raise ConsolidadoNoExisteError("No existe consolidado para ese período.") from exc

    if consolidado.estado in (
        ConsolidadoMensualSindicato.ESTADO_CERRADO,
        ConsolidadoMensualSindicato.ESTADO_EXPORTADO,
    ):
        raise ConsolidadoBloqueadoError("El período ya está cerrado o exportado.")

    consolidado.estado = ConsolidadoMensualSindicato.ESTADO_CERRADO
    consolidado.save(update_fields=["estado", "updated_at"])

    AuditoriaSindicato.objects.create(
        empresa=empresa,
        usuario=usuario,
        accion="CERRAR_CONSOLIDADO",
        entidad="ConsolidadoMensualSindicato",
        entidad_id=str(consolidado.id),
        periodo=periodo,
        resumen=(
            f"CERRAR_CONSOLIDADO {periodo} | socios={consolidado.total_socios} | "
            f"monto={int(consolidado.total_monto)}"
        )[:255],
        payload={
            "periodo": periodo,
            "estado": consolidado.estado,
            "total_socios": consolidado.total_socios,
            "total_monto": int(consolidado.total_monto),
        },
    )

    return consolidado
