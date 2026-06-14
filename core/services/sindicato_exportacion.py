from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Optional

from django.db import transaction
from django.utils import timezone

from openpyxl import Workbook

from core.models import (
    AuditoriaSindicato,
    ConsolidadoDetalleSindicato,
    ConsolidadoMensualSindicato,
    TipoBeneficioSindicato,
)


class ConsolidadoExportacionError(Exception):
    pass


@dataclass
class ExportacionResultado:
    consolidado_id: int
    periodo: str
    filename: str
    content: bytes


def _resolver_consolidado(*, empresa, periodo: Optional[str], consolidado_id: Optional[int]):
    if not periodo and not consolidado_id:
        raise ConsolidadoExportacionError("Debes informar periodo o consolidado_id para exportar.")

    qs = ConsolidadoMensualSindicato.objects.filter(empresa=empresa)
    if consolidado_id:
        qs = qs.filter(pk=consolidado_id)
    else:
        qs = qs.filter(periodo=periodo)

    consolidado = qs.first()
    if not consolidado:
        raise ConsolidadoExportacionError("Consolidado no encontrado para la empresa indicada.")

    if consolidado.estado not in (
        ConsolidadoMensualSindicato.ESTADO_CERRADO,
        ConsolidadoMensualSindicato.ESTADO_EXPORTADO,
    ):
        raise ConsolidadoExportacionError("Solo se puede exportar un consolidado en estado CERRADO o EXPORTADO.")

    return consolidado


def _build_workbook(*, consolidado, exportado_por: str):
    wb = Workbook()
    ws = wb.active
    ws.title = "Consolidado"

    beneficios = list(
        TipoBeneficioSindicato.objects.filter(empresa=consolidado.empresa)
        .order_by("orden_export", "nombre")
        .values_list("id", "nombre")
    )

    detalles = list(
        ConsolidadoDetalleSindicato.objects.select_related("socio", "tipo_beneficio")
        .filter(consolidado=consolidado)
        .order_by("socio__rut", "tipo_beneficio__orden_export", "tipo_beneficio__nombre")
    )

    header_base = ["RUT", "Nombre", "Site", "Estado laboral"]
    header_beneficios = [nombre for _id, nombre in beneficios]
    headers = header_base + header_beneficios + ["Total General"]
    ws.append(headers)

    # Pivot socio x beneficio
    socios = {}
    for d in detalles:
        socio = d.socio
        key = socio.id
        if key not in socios:
            socios[key] = {
                "rut": socio.rut,
                "nombre": socio.nombre,
                "site": socio.site or "",
                "estado_laboral": socio.get_estado_laboral_display(),
                "beneficios": {},
                "total": 0,
            }
        socios[key]["beneficios"][d.tipo_beneficio_id] = int(d.monto_aprobado)
        socios[key]["total"] += int(d.monto_aprobado)

    for socio_id in sorted(socios.keys(), key=lambda s: (socios[s]["rut"], socios[s]["nombre"])):
        row_data = socios[socio_id]
        row = [
            row_data["rut"],
            row_data["nombre"],
            row_data["site"],
            row_data["estado_laboral"],
        ]
        for benef_id, _nombre in beneficios:
            row.append(row_data["beneficios"].get(benef_id, 0))
        row.append(row_data["total"])
        ws.append(row)

    # Fila total final
    total_por_beneficio = []
    for benef_id, _nombre in beneficios:
        total_b = sum(s["beneficios"].get(benef_id, 0) for s in socios.values())
        total_por_beneficio.append(total_b)
    total_general = sum(total_por_beneficio)

    ws.append(["TOTAL", "", "", ""] + total_por_beneficio + [total_general])

    # Hoja resumen
    ws_resumen = wb.create_sheet(title="Resumen")
    ws_resumen.append(["Campo", "Valor"])
    ws_resumen.append(["Periodo", consolidado.periodo])
    ws_resumen.append(["Empresa/Sindicato", consolidado.empresa.nombre])
    ws_resumen.append(["Total socios", consolidado.total_socios])
    ws_resumen.append(["Total general", int(consolidado.total_monto)])
    ws_resumen.append(["Fecha generación", consolidado.fecha_generacion.isoformat() if consolidado.fecha_generacion else ""])
    ws_resumen.append(["Exportado por", exportado_por])
    ws_resumen.append(["Fecha exportación", timezone.now().isoformat()])

    output = BytesIO()
    wb.save(output)
    return output.getvalue()


@transaction.atomic
def exportar_consolidado_excel(*, empresa, usuario=None, periodo: Optional[str] = None, consolidado_id: Optional[int] = None) -> ExportacionResultado:
    consolidado = _resolver_consolidado(empresa=empresa, periodo=periodo, consolidado_id=consolidado_id)

    usuario_label = "Sistema"
    if usuario is not None:
        usuario_label = usuario.get_full_name().strip() or usuario.username or usuario.email or "Usuario"

    content = _build_workbook(consolidado=consolidado, exportado_por=usuario_label)

    if consolidado.estado == ConsolidadoMensualSindicato.ESTADO_CERRADO:
        consolidado.estado = ConsolidadoMensualSindicato.ESTADO_EXPORTADO
        consolidado.save(update_fields=["estado", "updated_at"])

    AuditoriaSindicato.objects.create(
        empresa=empresa,
        usuario=usuario,
        accion="EXPORTAR_CONSOLIDADO",
        entidad="ConsolidadoMensualSindicato",
        entidad_id=str(consolidado.id),
        periodo=consolidado.periodo,
        resumen=(
            f"EXPORTAR_CONSOLIDADO {consolidado.periodo} | socios={consolidado.total_socios} "
            f"| monto={int(consolidado.total_monto)}"
        )[:255],
        payload={
            "periodo": consolidado.periodo,
            "total_socios": consolidado.total_socios,
            "total_monto": int(consolidado.total_monto),
            "estado_final": consolidado.estado,
        },
    )

    filename = f"consolidado_sindicato_{consolidado.periodo}_{consolidado.empresa.id}.xlsx"
    return ExportacionResultado(
        consolidado_id=consolidado.id,
        periodo=consolidado.periodo,
        filename=filename,
        content=content,
    )
