from datetime import date, datetime

from django.db.models import Count
from django.utils import timezone

from core.models import (
    AlertaSindicato,
    ConsolidadoMensualSindicato,
    Empresa,
    MovimientoSindicato,
)


def _parse_fecha(valor):
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if not valor:
        return None

    texto = str(valor).strip()
    formatos = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%d.%m.%Y",
    ]
    for fmt in formatos:
        try:
            return datetime.strptime(texto, fmt).date()
        except ValueError:
            continue
    return None


def _months_between(inicio, fin):
    if not inicio or not fin:
        return None
    meses = (fin.year - inicio.year) * 12 + (fin.month - inicio.month)
    if fin.day < inicio.day:
        meses -= 1
    return max(meses, 0)


def _upsert_alerta(empresa, clave_unica, defaults):
    defaults = {**defaults, 'fecha_alerta': timezone.now()}
    alerta, created = AlertaSindicato.objects.get_or_create(
        empresa=empresa,
        clave_unica=clave_unica,
        defaults={
            **defaults,
            'estado': AlertaSindicato.ESTADO_PENDIENTE,
            'resuelta_por': None,
            'fecha_resolucion': None,
        },
    )
    if not created:
        for field, value in defaults.items():
            setattr(alerta, field, value)
        alerta.save(update_fields=[*defaults.keys(), 'updated_at'])
    return alerta


def generar_alertas_telefonia(empresa, periodo=None):
    today = timezone.localdate()
    qs = MovimientoSindicato.objects.filter(
        empresa=empresa,
        fuente=MovimientoSindicato.FUENTE_TELEFONIA,
    ).select_related('socio')
    if periodo:
        qs = qs.filter(periodo=periodo)

    alertas = []
    for mov in qs:
        source_columns = (mov.metadata_fuente or {}).get('source_columns', {})
        raw_fecha = source_columns.get('fecha_entrega')
        fecha_entrega = _parse_fecha(raw_fecha)

        base_payload = {
            'movimiento_id': mov.id,
            'socio_id': mov.socio_id,
            'periodo': mov.periodo,
            'fuente': mov.fuente,
            'fecha_entrega_raw': raw_fecha,
        }

        if not fecha_entrega:
            clave = f"TEL-FECHA-INVALIDA-{mov.id}"
            alertas.append(
                _upsert_alerta(
                    empresa,
                    clave,
                    {
                        'socio': mov.socio,
                        'movimiento': mov,
                        'tipo_alerta': 'TELEFONIA_FECHA_INVALIDA',
                        'categoria': AlertaSindicato.CATEGORIA_TELEFONIA,
                        'prioridad': AlertaSindicato.PRIORIDAD_ALTA,
                        'titulo': 'Telefonía con fecha de entrega faltante o inválida',
                        'descripcion': (
                            f"El movimiento {mov.id} del período {mov.periodo} no tiene fecha de entrega válida."
                        ),
                        'periodo': mov.periodo,
                        'fecha_referencia': None,
                        'payload': base_payload,
                    },
                )
            )
            continue

        meses = _months_between(fecha_entrega, today)
        base_payload['meses_desde_entrega'] = meses

        if meses >= 24:
            tipo = 'TELEFONIA_VENCIDA_24'
            prioridad = AlertaSindicato.PRIORIDAD_CRITICA
            titulo = 'Telefonía vencida (24+ meses)'
            descripcion = (
                f"La cuenta de telefonía del socio {mov.socio} cumple {meses} meses desde entrega y requiere recambio."
            )
        elif meses in (21, 22):
            tipo = 'TELEFONIA_RENOVACION_21_22'
            prioridad = AlertaSindicato.PRIORIDAD_ALTA
            titulo = 'Telefonía en ventana de renovación (21-22 meses)'
            descripcion = (
                f"La cuenta de telefonía del socio {mov.socio} cumple {meses} meses desde entrega y debe renovarse."
            )
        elif meses == 20:
            tipo = 'TELEFONIA_PREVENTIVA_20'
            prioridad = AlertaSindicato.PRIORIDAD_MEDIA
            titulo = 'Telefonía con alerta preventiva (20 meses)'
            descripcion = (
                f"La cuenta de telefonía del socio {mov.socio} cumple 20 meses desde entrega."
            )
        else:
            continue

        clave = f"TEL-{tipo}-{mov.id}"
        alertas.append(
            _upsert_alerta(
                empresa,
                clave,
                {
                    'socio': mov.socio,
                    'movimiento': mov,
                    'tipo_alerta': tipo,
                    'categoria': AlertaSindicato.CATEGORIA_TELEFONIA,
                    'prioridad': prioridad,
                    'titulo': titulo,
                    'descripcion': descripcion,
                    'periodo': mov.periodo,
                    'fecha_referencia': fecha_entrega,
                    'payload': base_payload,
                },
            )
        )

    return alertas


def generar_alertas_operativas(empresa, periodo=None):
    alertas = []
    movimientos = MovimientoSindicato.objects.filter(empresa=empresa)
    if periodo:
        movimientos = movimientos.filter(periodo=periodo)

    # Alertas de importación/movimientos observados o rechazados por período y estado.
    estado_rows = (
        movimientos.filter(estado__in=[MovimientoSindicato.ESTADO_OBSERVADO, MovimientoSindicato.ESTADO_RECHAZADO])
        .values('periodo', 'estado')
        .annotate(total=Count('id'))
    )
    for row in estado_rows:
        estado = row['estado']
        periodo_row = row['periodo']
        total = row['total']
        prioridad = (
            AlertaSindicato.PRIORIDAD_ALTA
            if estado == MovimientoSindicato.ESTADO_RECHAZADO
            else AlertaSindicato.PRIORIDAD_MEDIA
        )
        tipo = f"MOVIMIENTOS_{estado}"
        clave = f"OPS-{tipo}-{periodo_row}"
        alertas.append(
            _upsert_alerta(
                empresa,
                clave,
                {
                    'tipo_alerta': tipo,
                    'categoria': AlertaSindicato.CATEGORIA_IMPORTACION,
                    'prioridad': prioridad,
                    'titulo': f"Movimientos {estado.lower()} en período {periodo_row}",
                    'descripcion': (
                        f"Se detectaron {total} movimientos con estado {estado.lower()} en el período {periodo_row}."
                    ),
                    'periodo': periodo_row,
                    'fecha_referencia': None,
                    'payload': {'estado': estado, 'periodo': periodo_row, 'total': total},
                },
            )
        )

    # Alertas por períodos con movimientos pero sin consolidado generado.
    periodos_mov = set(movimientos.values_list('periodo', flat=True).distinct())
    consolidados = ConsolidadoMensualSindicato.objects.filter(empresa=empresa)
    if periodo:
        consolidados = consolidados.filter(periodo=periodo)
    periodos_consolidado = set(consolidados.values_list('periodo', flat=True).distinct())

    for periodo_sin_cons in sorted(periodos_mov - periodos_consolidado):
        total_periodo = movimientos.filter(periodo=periodo_sin_cons).count()
        clave = f"OPS-MOV-SIN-CONS-{periodo_sin_cons}"
        alertas.append(
            _upsert_alerta(
                empresa,
                clave,
                {
                    'tipo_alerta': 'MOVIMIENTOS_SIN_CONSOLIDADO',
                    'categoria': AlertaSindicato.CATEGORIA_CONSOLIDADO,
                    'prioridad': AlertaSindicato.PRIORIDAD_ALTA,
                    'titulo': f"Período {periodo_sin_cons} sin consolidado",
                    'descripcion': (
                        f"Existen {total_periodo} movimientos en {periodo_sin_cons} y aún no hay consolidado generado."
                    ),
                    'periodo': periodo_sin_cons,
                    'fecha_referencia': None,
                    'payload': {'periodo': periodo_sin_cons, 'movimientos': total_periodo},
                },
            )
        )

    # Consolidado cerrado pendiente de exportación.
    for cons in consolidados.filter(estado=ConsolidadoMensualSindicato.ESTADO_CERRADO):
        clave = f"OPS-CONS-CERRADO-NO-EXPORTADO-{cons.id}"
        alertas.append(
            _upsert_alerta(
                empresa,
                clave,
                {
                    'tipo_alerta': 'CONSOLIDADO_CERRADO_NO_EXPORTADO',
                    'categoria': AlertaSindicato.CATEGORIA_CONSOLIDADO,
                    'prioridad': AlertaSindicato.PRIORIDAD_MEDIA,
                    'titulo': f"Consolidado {cons.periodo} cerrado sin exportar",
                    'descripcion': (
                        f"El consolidado del período {cons.periodo} está cerrado y pendiente de exportación."
                    ),
                    'periodo': cons.periodo,
                    'fecha_referencia': None,
                    'payload': {'consolidado_id': cons.id, 'periodo': cons.periodo},
                },
            )
        )

    return alertas


def generar_alertas_sindicato(empresa, periodo=None):
    if not isinstance(empresa, Empresa):
        raise ValueError('empresa debe ser instancia de Empresa')

    telefonia = generar_alertas_telefonia(empresa, periodo=periodo)
    operativas = generar_alertas_operativas(empresa, periodo=periodo)
    return {
        'telefonia': len(telefonia),
        'operativas': len(operativas),
        'total': len(telefonia) + len(operativas),
    }


def marcar_alerta_en_revision(alerta, usuario):
    alerta.estado = AlertaSindicato.ESTADO_EN_REVISION
    alerta.resuelta_por = usuario
    alerta.fecha_resolucion = timezone.now()
    alerta.save(update_fields=['estado', 'resuelta_por', 'fecha_resolucion', 'updated_at'])
    return alerta


def resolver_alerta(alerta, usuario):
    alerta.estado = AlertaSindicato.ESTADO_RESUELTA
    alerta.resuelta_por = usuario
    alerta.fecha_resolucion = timezone.now()
    alerta.save(update_fields=['estado', 'resuelta_por', 'fecha_resolucion', 'updated_at'])
    return alerta


def descartar_alerta(alerta, usuario):
    alerta.estado = AlertaSindicato.ESTADO_DESCARTADA
    alerta.resuelta_por = usuario
    alerta.fecha_resolucion = timezone.now()
    alerta.save(update_fields=['estado', 'resuelta_por', 'fecha_resolucion', 'updated_at'])
    return alerta
