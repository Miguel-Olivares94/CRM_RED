from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
import json
import os
from django.utils import timezone
from core.models import Cliente, Contacto, Oportunidad, Llamada, Seguimiento, Comision

class Command(BaseCommand):
    help = "Importa datos de HERRAMIENTA 3.0 desde archivo JSON"

    def add_arguments(self, parser):
        parser.add_argument(
            "--archivo",
            type=str,
            default="herramienta_summary.json",
            help="Ruta del archivo JSON a importar"
        )

    def handle(self, *args, **options):
        archivo = options["archivo"]
        importar_datos(archivo)

def importar_datos(archivo_json="herramienta_summary.json"):
    """Importa datos desde archivo JSON a Django"""
    print("="*70)
    print("INICIANDO IMPORTACION DE DATOS DE HERRAMIENTA 3.0")
    print("="*70)
    
    # Buscar archivo en diferentes ubicaciones
    import os
    rutas_posibles = [
        archivo_json,
        os.path.join("..", archivo_json),
        os.path.join("../../", archivo_json),
        "herramienta_summary.json",
        "../herramienta_summary.json",
    ]
    
    archivo_encontrado = None
    for ruta in rutas_posibles:
        if os.path.exists(ruta):
            archivo_encontrado = ruta
            print("Archivo encontrado en: {}".format(ruta))
            break
    
    if not archivo_encontrado:
        print("Archivo no encontrado en: {}".format(rutas_posibles))
        return False
    
    try:
        with open(archivo_encontrado, "r", encoding="utf-8") as f:
            datos_raw = json.load(f)
        print("Archivo cargado con exito\n")
    except FileNotFoundError:
        print("Archivo no encontrado")
        return False
    except json.JSONDecodeError:
        print("Archivo JSON invalido")
        return False
    
    # Si datos es una lista, es el formato de hojas, convertir a diccionario simple
    if isinstance(datos_raw, list):
        print("Detectado formato de lista. Procesando hojas...\n")
        # Simplemente usar los datos como está
        datos = {"raw_hojas": datos_raw}
    else:
        datos = datos_raw

    stats = {
        "clientes_creados": 0,
        "clientes_actualizados": 0,
        "clientes_error": 0,
        "contactos_creados": 0,
        "oportunidades_creados": 0,
        "llamadas_creadas": 0,
        "seguimientos_creados": 0,
        "comisiones_creadas": 0,
    }

    print("Importando CLIENTES...")
    rut_a_cliente = {}

    try:
        for cliente_data in datos.get("clientes", []):
            rut = cliente_data.get("rut", "").strip()
            nombre = cliente_data.get("nombre_empresa", "").strip()

            if not rut or not nombre:
                stats["clientes_error"] += 1
                continue

            usuario_nombre = cliente_data.get("usuario_asignado", "SIN ASIGNAR")
            email_val = "{0}@claro.cl".format(usuario_nombre.lower().replace(" ", "."))
            usuario, _ = get_user_model().objects.get_or_create(
                email=email_val,
                defaults={
                    "first_name": usuario_nombre.split()[0] if usuario_nombre != "SIN ASIGNAR" else "Sin",
                    "last_name": " ".join(usuario_nombre.split()[1:]) if len(usuario_nombre.split()) > 1 else "Asignar"
                }
            )

            cliente, creado = Cliente.objects.update_or_create(
                rut=rut,
                defaults={
                    "nombre_empresa": nombre,
                    "sector": cliente_data.get("sector") or "No especificado",
                    "estado": cliente_data.get("estado", "ACTIVO"),
                    "usuario_asignado": usuario,
                    "created_at": cliente_data.get("fecha_registro") or timezone.now(),
                }
            )

            rut_a_cliente[rut] = cliente
            if creado:
                stats["clientes_creados"] += 1
                print("  Creado: {0} ({1})".format(nombre, rut))
            else:
                stats["clientes_actualizados"] += 1
                print("  Actualizado: {0} ({1})".format(nombre, rut))

    except Exception as e:
        print("  Error en CLIENTES: {0}".format(str(e)))
        stats["clientes_error"] += 1

    print("\nClientes procesados\n")

    print("Importando CONTACTOS...")
    try:
        for contacto_data in datos.get("contactos", []):
            id_cliente = contacto_data.get("id_cliente")
            nombre = contacto_data.get("nombre", "").strip()
            email = contacto_data.get("email", "").strip() or None
            telefono = contacto_data.get("telefono", "").strip() or None
            rol = contacto_data.get("rol", "USUARIO")

            if not nombre:
                continue

            clientes_list = list(rut_a_cliente.values())
            if id_cliente <= len(clientes_list):
                cliente = clientes_list[id_cliente - 1]
            else:
                continue

            contacto, creado = Contacto.objects.get_or_create(
                cliente=cliente,
                nombre=nombre,
                defaults={
                    "cargo": contacto_data.get("cargo", "No especificado"),
                    "email": email,
                    "telefono": telefono,
                    "rol": rol,
                }
            )

            if creado:
                stats["contactos_creados"] += 1
                print("  Creado: {0} ({1})".format(nombre, cliente.nombre_empresa))

    except Exception as e:
        print("  Error en CONTACTOS: {0}".format(str(e)))

    print("\nContactos procesados\n")

    print("Importando OPORTUNIDADES...")
    id_a_oportunidad = {}

    try:
        for opp_data in datos.get("oportunidades", []):
            rut_cliente = opp_data.get("rut_cliente", "").strip()
            id_opp = opp_data.get("id_oportunidad")

            if rut_cliente not in rut_a_cliente:
                continue

            cliente = rut_a_cliente[rut_cliente]

            usuario_nombre = opp_data.get("usuario_asignado", "SIN ASIGNAR")
            email_val = "{0}@claro.cl".format(usuario_nombre.lower().replace(" ", "."))
            usuario, _ = get_user_model().objects.get_or_create(
                email=email_val
            )

            etapa = opp_data.get("etapa", "LEAD").upper()
            etapa_map = {
                "LEAD": "LEAD",
                "CONTACTO": "CONTACTO",
                "CALIFICADO": "CALIFICADO",
                "PROPUESTA": "PROPUESTA",
                "NEGOCIACION": "NEGOCIACION",
                "CIERRE": "CIERRE",
                "GANADA": "GANADA",
                "PERDIDA": "PERDIDA",
                "DORMIDA": "DORMIDA",
            }
            etapa = etapa_map.get(etapa, "LEAD")

            oportunidad, creado = Oportunidad.objects.update_or_create(
                cliente=cliente,
                nombre="{0} - Opp #{1}".format(cliente.nombre_empresa, id_opp),
                defaults={
                    "monto": opp_data.get("monto", 0),
                    "etapa": etapa,
                    "usuario": usuario,
                    "fecha_cierre_estimada": opp_data.get("fecha_cierre_estimada"),
                    "descripcion": opp_data.get("notas", ""),
                    "created_at": opp_data.get("fecha_creacion") or timezone.now(),
                }
            )

            id_a_oportunidad[id_opp] = oportunidad
            if creado:
                stats["oportunidades_creados"] += 1
                print("  Creada: {0} - ${1} ({2})".format(cliente.nombre_empresa, opp_data.get("monto"), etapa))

    except Exception as e:
        print("  Error en OPORTUNIDADES: {0}".format(str(e)))

    print("\nOportunidades procesadas\n")

    print("Importando LLAMADAS...")
    try:
        for llamada_data in datos.get("llamadas", []):
            id_opp = llamada_data.get("id_oportunidad")

            if id_opp not in id_a_oportunidad:
                continue

            oportunidad = id_a_oportunidad[id_opp]

            tipo = llamada_data.get("tipo", "LLAMADA").upper()
            tipo_map = {
                "LLAMADA": "LLAMADA",
                "EMAIL": "EMAIL",
                "REUNION": "REUNION",
                "VIDEO": "VIDEO",
            }
            tipo = tipo_map.get(tipo, "LLAMADA")

            resultado = llamada_data.get("resultado", "EXITOSA").upper()
            resultado_map = {
                "EXITOSA": "EXITOSA",
                "FALLIDA": "FALLIDA",
                "SIN_RESPUESTA": "SIN_RESPUESTA",
                "PENDIENTE": "PENDIENTE",
            }
            resultado = resultado_map.get(resultado, "PENDIENTE")

            llamada, creado = Llamada.objects.get_or_create(
                oportunidad=oportunidad,
                fecha=llamada_data.get("fecha"),
                defaults={
                    "tipo": tipo,
                    "resultado": resultado,
                    "notas": llamada_data.get("nota", ""),
                }
            )

            if creado:
                stats["llamadas_creadas"] += 1

    except Exception as e:
        print("  Error en LLAMADAS: {0}".format(str(e)))

    print("Llamadas procesadas\n")

    print("Importando SEGUIMIENTOS...")
    try:
        for seg_data in datos.get("seguimientos", []):
            id_opp = seg_data.get("id_oportunidad")

            if id_opp not in id_a_oportunidad:
                continue

            oportunidad = id_a_oportunidad[id_opp]

            tipo = seg_data.get("tipo", "ALERTA").upper()
            tipo_map = {
                "ALERTA": "ALERTA",
                "RECORDATORIO": "RECORDATORIO",
                "TAREA": "TAREA",
                "NOTA": "NOTA",
            }
            tipo = tipo_map.get(tipo, "NOTA")

            prioridad = seg_data.get("prioridad", "MEDIA").upper()
            prioridad_map = {
                "BAJA": "BAJA",
                "MEDIA": "MEDIA",
                "ALTA": "ALTA",
                "CRITICA": "CRITICA",
            }
            prioridad = prioridad_map.get(prioridad, "MEDIA")

            seguimiento, creado = Seguimiento.objects.get_or_create(
                oportunidad=oportunidad,
                descripcion=seg_data.get("descripcion", ""),
                fecha_vencimiento=seg_data.get("fecha_vencimiento"),
                defaults={
                    "tipo": tipo,
                    "prioridad": prioridad,
                    "completado": seg_data.get("estado", "").upper() == "COMPLETADA",
                }
            )

            if creado:
                stats["seguimientos_creados"] += 1

    except Exception as e:
        print("  Error en SEGUIMIENTOS: {0}".format(str(e)))

    print("Seguimientos procesados\n")

    print("Importando COMISIONES...")
    try:
        for com_data in datos.get("comisiones", []):
            usuario_nombre = com_data.get("usuario", "").strip()
            periodo = com_data.get("periodo", "").strip()

            if not usuario_nombre or not periodo:
                continue

            email_val = "{0}@claro.cl".format(usuario_nombre.lower().replace(" ", "."))
            usuario, _ = get_user_model().objects.get_or_create(
                email=email_val
            )

            comision, creado = Comision.objects.get_or_create(
                usuario=usuario,
                periodo=periodo,
                defaults={
                    "lineas_vendidas_portabilidad": com_data.get("lineas_portabilidad", 0),
                    "lineas_vendidas_nueva": com_data.get("lineas_nueva", 0),
                    "lineas_vendidas_m2m": com_data.get("lineas_m2m", 0),
                    "comision_calculada": com_data.get("total_a_pagar", 0),
                    "estado": "CALCULADA",
                }
            )

            if creado:
                stats["comisiones_creadas"] += 1

    except Exception as e:
        print("  Error en COMISIONES: {0}".format(str(e)))

    print("Comisiones procesadas\n")

    print("="*70)
    print("IMPORTACION COMPLETADA")
    print("="*70)
    print("\nESTADISTICAS FINALES:\n")
    print("  Clientes      : {0} creados, {1} actualizados".format(stats["clientes_creados"], stats["clientes_actualizados"]))
    print("  Contactos     : {0} creados".format(stats["contactos_creados"]))
    print("  Oportunidades : {0} creadas".format(stats["oportunidades_creados"]))
    print("  Llamadas      : {0} creadas".format(stats["llamadas_creadas"]))
    print("  Seguimientos  : {0} creados".format(stats["seguimientos_creados"]))
    print("  Comisiones    : {0} creadas".format(stats["comisiones_creadas"]))
    print("\n")

    return True
