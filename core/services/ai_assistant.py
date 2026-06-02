"""
Servicio centralizado de IA para el CRM.
Expone dos prompts especializados:
  - sugerir_estrategia_venta  → para el Vendedor
  - auditar_oportunidad       → para el Administrador
"""
import json
import os

import anthropic

MODEL = "claude-opus-4-5"


def _get_client() -> anthropic.Anthropic:
    """Devuelve un cliente Anthropic. Lanza ValueError si falta la API key."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY no está configurada en las variables de entorno")
    return anthropic.Anthropic(api_key=api_key)

# ──────────────────────────────────────────────────────────────
# Sistema de prompts especializados (cacheables)
# ──────────────────────────────────────────────────────────────

SYSTEM_VENDEDOR = """\
Eres un coach experto en ventas B2B para el sector telecomunicaciones en Chile.
Tu función es analizar el historial de una oportunidad comercial y generar
recomendaciones concretas y accionables para el vendedor que debe contactar
al cliente HOY.

Responde SIEMPRE con un JSON válido que tenga exactamente estas claves:
{
  "script_sugerido": "Texto de lo que debe decir el vendedor al iniciar la llamada (2-4 oraciones naturales, en primera persona)",
  "objeciones_probables": ["objeción 1", "objeción 2", "objeción 3"],
  "proximo_paso_recomendado": "Una acción concreta y fechada que el vendedor debe hacer después de esta gestión"
}

No incluyas texto fuera del JSON. No uses markdown. Solo el objeto JSON.
"""

SYSTEM_ADMIN = """\
Eres un analista senior de ventas B2B especializado en auditoría de pipeline comercial
para el sector telecomunicaciones en Chile.
Tu función es evaluar la salud de una oportunidad y detectar riesgos objetivos.

Responde SIEMPRE con un JSON válido que tenga exactamente estas claves:
{
  "probabilidad_exito": <número entero entre 0 y 100>,
  "alertas_riesgo": ["alerta 1", "alerta 2"],
  "cuellos_de_botella": ["cuello 1", "cuello 2"]
}

Basa la probabilidad en datos concretos: frecuencia de contacto, días en etapa,
historial de seguimientos y resultado de gestiones.
No incluyas texto fuera del JSON. No uses markdown. Solo el objeto JSON.
"""


def _build_contexto_oportunidad(oportunidad, gestiones, seguimientos) -> str:
    """Construye el bloque de contexto común para ambos prompts."""
    dias_sin_contacto = oportunidad.dias_sin_contacto
    alerta = oportunidad.estado_alerta

    lineas_gestion = []
    for g in gestiones:
        contacto_nombre = g.contacto.nombre if g.contacto else "Sin contacto"
        lineas_gestion.append(
            f"  - {g.fecha_hora.strftime('%d/%m/%Y')} | {g.get_tipo_display()} | "
            f"Resultado: {g.get_resultado_display()} | Contacto: {contacto_nombre} | "
            f"Nota: {(g.nota_ejecutiva or 'Sin nota')[:120]}"
        )

    lineas_seg = []
    for s in seguimientos:
        lineas_seg.append(
            f"  - {s.get_tipo_display()} | Estado: {s.get_estado_display()} | "
            f"Prioridad: {s.get_prioridad_display()} | "
            f"Vence: {s.fecha_vencimiento.strftime('%d/%m/%Y') if s.fecha_vencimiento else 'Sin fecha'} | "
            f"{(s.descripcion or '')[:100]}"
        )

    return f"""\
=== DATOS DE LA OPORTUNIDAD ===
Cliente: {oportunidad.cliente.nombre_empresa}
RUT: {oportunidad.cliente.rut}
Segmento: {oportunidad.cliente.segmento or 'No definido'}
Sector: {oportunidad.cliente.sector or 'No definido'}
Total líneas actuales del cliente: {oportunidad.cliente.q_total_lineas or 0}

Etapa actual: {oportunidad.get_etapa_display()}
Estado: {oportunidad.get_estado_display()}
Líneas en oportunidad: {oportunidad.lineas}
Probabilidad registrada: {oportunidad.probabilidad}%
Fecha de creación: {oportunidad.fecha_creacion.strftime('%d/%m/%Y')}
Fecha cierre estimada: {oportunidad.fecha_cierre_estimada.strftime('%d/%m/%Y') if oportunidad.fecha_cierre_estimada else 'Sin fecha'}
Días sin contacto: {dias_sin_contacto if dias_sin_contacto is not None else 'Nunca contactado'}
Estado de alerta: {alerta}
Productos: {oportunidad.productos or 'No especificado'}
Observaciones: {(oportunidad.observaciones or 'Sin observaciones')[:200]}

=== ÚLTIMAS GESTIONES ({len(gestiones)}) ===
{chr(10).join(lineas_gestion) if lineas_gestion else '  Sin gestiones registradas'}

=== SEGUIMIENTOS PENDIENTES ({len(seguimientos)}) ===
{chr(10).join(lineas_seg) if lineas_seg else '  Sin seguimientos pendientes'}
"""


def sugerir_estrategia_venta(oportunidad, gestiones, seguimientos) -> dict:
    """
    Endpoint Vendedor: analiza el historial y devuelve script + objeciones + próximo paso.
    """
    client = _get_client()
    contexto = _build_contexto_oportunidad(oportunidad, gestiones, seguimientos)

    prompt_usuario = f"""\
{contexto}

=== INSTRUCCIÓN ===
Genera la estrategia de contacto para HOY. El vendedor va a llamar o visitar a este cliente.
Considera la etapa actual, el historial de contactos y el tiempo sin contacto.
"""

    mensaje = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_VENDEDOR,
        messages=[{"role": "user", "content": prompt_usuario}],
    )

    texto = next(
        (b.text for b in mensaje.content if b.type == "text"), "{}"
    )
    try:
        return json.loads(texto)
    except json.JSONDecodeError as exc:
        raise ValueError(f"La IA devolvió una respuesta no válida: {exc}") from exc


SYSTEM_CONTACTO = """\
Eres un coach experto en ventas B2B para el sector telecomunicaciones en Chile.
Tu función es analizar el perfil de un contacto clave dentro de una empresa cliente
y ayudar al vendedor a preparar su próxima interacción con esa persona.

Responde SIEMPRE con un JSON válido que tenga exactamente estas claves:
{
  "perfil_contacto": "Análisis breve de quién es esta persona en el proceso de decisión (2-3 oraciones)",
  "como_abordar": "Cómo debe el vendedor comunicarse y relacionarse con este contacto específicamente (2-3 oraciones)",
  "temas_de_interes": ["tema relevante 1", "tema relevante 2", "tema relevante 3"],
  "proximo_paso": "Acción concreta y fechada que el vendedor debe ejecutar con este contacto"
}

No incluyas texto fuera del JSON. No uses markdown. Solo el objeto JSON.
"""


def preparar_contacto_vendedor(contacto, llamadas, oportunidades) -> dict:
    """
    Endpoint Contacto: analiza el perfil del contacto y cómo abordarle.
    """
    client = _get_client()

    lineas_llamadas = []
    for g in llamadas:
        lineas_llamadas.append(
            f"  - {g.fecha_hora.strftime('%d/%m/%Y')} | {g.get_tipo_display()} | "
            f"Resultado: {g.get_resultado_display()} | "
            f"Nota: {(g.nota_ejecutiva or 'Sin nota')[:100]}"
        )

    lineas_opp = []
    for o in oportunidades:
        lineas_opp.append(
            f"  - {o.get_etapa_display()} | {o.lineas} líneas | "
            f"Probabilidad: {o.probabilidad}% | Productos: {o.productos or 'No definido'}"
        )

    contexto = f"""\
=== PERFIL DEL CONTACTO ===
Nombre: {contacto.nombre}
Cargo: {contacto.cargo or 'Sin cargo'}
Rol en decisión: {contacto.get_rol_display() if hasattr(contacto, 'get_rol_display') else contacto.rol}
Estado: {'Activo' if contacto.activo else 'Inactivo'}
Email: {contacto.email or 'Sin email'}

=== EMPRESA CLIENTE ===
Empresa: {contacto.cliente.nombre_empresa}
RUT: {contacto.cliente.rut}
Sector: {contacto.cliente.sector or 'No definido'}
Segmento: {contacto.cliente.segmento or 'No definido'}
Total líneas actuales: {contacto.cliente.q_total_lineas or 0}
BAM: {contacto.cliente.bam or 0} | M2M: {contacto.cliente.m2m or 0} | VOZ/GPS: {contacto.cliente.voz or 0}

=== OPORTUNIDADES ACTIVAS DEL CLIENTE ({len(oportunidades)}) ===
{chr(10).join(lineas_opp) if lineas_opp else '  Sin oportunidades activas'}

=== HISTORIAL DE GESTIONES CON ESTE CONTACTO ({len(llamadas)}) ===
{chr(10).join(lineas_llamadas) if lineas_llamadas else '  Sin gestiones registradas con este contacto'}
"""

    prompt_usuario = f"""\
{contexto}

=== INSTRUCCIÓN ===
Analiza el perfil de este contacto y ayuda al vendedor a preparar su próxima interacción.
Considera su cargo, rol en la decisión y el historial de gestiones.
"""

    mensaje = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_CONTACTO,
        messages=[{"role": "user", "content": prompt_usuario}],
    )

    texto = next((b.text for b in mensaje.content if b.type == "text"), "{}")
    try:
        return json.loads(texto)
    except json.JSONDecodeError as exc:
        raise ValueError(f"La IA devolvió una respuesta no válida: {exc}") from exc


def auditar_oportunidad(oportunidad, gestiones, seguimientos) -> dict:
    """
    Endpoint Admin: evalúa salud de la venta y detecta riesgos objetivos.
    """
    client = _get_client()
    contexto = _build_contexto_oportunidad(oportunidad, gestiones, seguimientos)

    prompt_usuario = f"""\
{contexto}

=== INSTRUCCIÓN ===
Audita esta oportunidad con criterio analítico. Evalúa:
1. Frecuencia y calidad de las gestiones registradas
2. Tiempo en la etapa actual vs. ciclo de ventas típico
3. Alineación entre probabilidad registrada y evidencia real
4. Riesgos de abandono o pérdida de la oportunidad
5. Posibles cuellos de botella en el proceso

Sé específico y basa cada observación en los datos provistos.
"""

    mensaje = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_ADMIN,
        messages=[{"role": "user", "content": prompt_usuario}],
    )

    texto = next(
        (b.text for b in mensaje.content if b.type == "text"), "{}"
    )
    try:
        return json.loads(texto)
    except json.JSONDecodeError as exc:
        raise ValueError(f"La IA devolvió una respuesta no válida: {exc}") from exc
