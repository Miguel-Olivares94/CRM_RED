"""
Tareas automáticas de Celery para el CRM.

Este módulo contiene todas las tareas que se ejecutan de forma automática:
- Actualización de estados de alertas en oportunidades
- Generación de alertas para fechas vencidas
- Cálculo de comisiones mensuales
"""

from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from decimal import Decimal
from .models import (
    Oportunidad, Seguimiento, Comision, MetaVentas,
    Llamada, Cliente
)


@shared_task(name='core.actualizar_estados_oportunidades')
def actualizar_estados_oportunidades():
    """
    Actualiza automáticamente el estado de alerta en todas las oportunidades.
    
    Se ejecuta diariamente para revisar:
    - Días sin contacto
    - Actualizar estado_alerta (AL_DIA, ATENCION, EN_RIESGO, RIESGO_ALTO, DORMIDA)
    - Generar alertas automáticas si es necesario
    
    Returns:
        dict: Estadísticas de la ejecución (oportunidades_revisadas, alertas_generadas)
    """
    try:
        from django.db.models import Q
        from datetime import datetime
        
        # Obtener todas las oportunidades abiertas
        oportunidades = Oportunidad.objects.filter(
            estado='ABIERTA'
        ).select_related('cliente', 'usuario')
        
        estadisticas = {
            'oportunidades_revisadas': 0,
            'alertas_generadas': 0,
            'estados_actualizados': {
                'AL_DIA': 0,
                'ATENCION': 0,
                'EN_RIESGO': 0,
                'RIESGO_ALTO': 0,
                'DORMIDA': 0
            }
        }
        
        for oportunidad in oportunidades:
            dias_sin_contacto = oportunidad.dias_sin_contacto
            nuevo_estado = oportunidad.estado_alerta
            
            # Determinar si necesita crear alerta automática
            crear_alerta = False
            prioridad_alerta = 'MEDIA'
            tipo_alerta = 'ALERTA'
            
            if dias_sin_contacto > 60:
                nuevo_estado = 'DORMIDA'
                crear_alerta = True
                prioridad_alerta = 'CRITICA'
                tipo_alerta = 'ALERTA'
            elif dias_sin_contacto > 30:
                nuevo_estado = 'RIESGO_ALTO'
                crear_alerta = True
                prioridad_alerta = 'ALTA'
            elif dias_sin_contacto > 14:
                nuevo_estado = 'EN_RIESGO'
                crear_alerta = True
                prioridad_alerta = 'ALTA'
            elif dias_sin_contacto > 7:
                nuevo_estado = 'ATENCION'
                crear_alerta = True
                prioridad_alerta = 'MEDIA'
            else:
                nuevo_estado = 'AL_DIA'
                crear_alerta = False
            
            estadisticas['estados_actualizados'][nuevo_estado] += 1

            # Crear seguimiento de alerta si es necesario y no existe uno reciente
            if crear_alerta:
                seg_reciente = Seguimiento.objects.filter(
                    oportunidad=oportunidad,
                    tipo='ALERTA',
                    created_at__gte=timezone.now() - timedelta(hours=1)
                ).exists()

                if not seg_reciente:
                    Seguimiento.objects.create(
                        oportunidad=oportunidad,
                        tipo='ALERTA',
                        prioridad=prioridad_alerta,
                        estado='PENDIENTE',
                        descripcion=f"Alerta automática: {dias_sin_contacto} días sin contacto. Estado: {nuevo_estado}",
                        asignado_a=oportunidad.usuario,
                        fecha_vencimiento=timezone.now()
                    )
                    estadisticas['alertas_generadas'] += 1
            
            estadisticas['oportunidades_revisadas'] += 1
        
        # Log de la ejecución
        print(f"[CELERY] actualizar_estados_oportunidades completada: {estadisticas}")
        return estadisticas
    
    except Exception as e:
        print(f"[ERROR CELERY] actualizar_estados_oportunidades: {str(e)}")
        return {'error': str(e)}


@shared_task(name='core.generar_alertas_vencidas')
def generar_alertas_vencidas():
    """
    Genera alertas automáticas para oportunidades con fecha de cierre vencida.
    
    Revisa diariamente todas las oportunidades y crea seguimientos de alerta
    para las que tienen fecha_cierre_estimada en el pasado.
    
    Returns:
        dict: Estadísticas de alertas generadas
    """
    try:
        hoy = timezone.now().date()
        
        # Buscar oportunidades vencidas sin alerta reciente
        oportunidades_vencidas = Oportunidad.objects.filter(
            estado='ABIERTA',
            fecha_cierre_estimada__lt=hoy
        ).select_related('usuario')
        
        estadisticas = {
            'alertas_generadas': 0,
            'oportunidades_vencidas': oportunidades_vencidas.count()
        }
        
        for oportunidad in oportunidades_vencidas:
            # Verificar que no exista una alerta similar reciente
            alerta_reciente = Seguimiento.objects.filter(
                oportunidad=oportunidad,
                tipo='ALERTA',
                estado='PENDIENTE',
                created_at__gte=timezone.now() - timedelta(hours=12)
            ).exists()
            
            if not alerta_reciente:
                dias_vencida = (hoy - oportunidad.fecha_cierre_estimada).days
                
                Seguimiento.objects.create(
                    oportunidad=oportunidad,
                    tipo='ALERTA',
                    prioridad='CRITICA',
                    estado='PENDIENTE',
                    descripcion=f"⚠️ VENCIDA: Oportunidad con {dias_vencida} días de atraso. "
                                f"Cliente: {oportunidad.cliente.nombre_empresa}. "
                                f"Monto: CLP {oportunidad.monto}",
                    asignado_a=oportunidad.usuario,
                    fecha_vencimiento=timezone.now()
                )

                estadisticas['alertas_generadas'] += 1

                # Enviar notificación por email al ejecutivo
                try:
                    if oportunidad.usuario.email:
                        enviar_notificacion_vencida(oportunidad, oportunidad.usuario)
                except Exception as e:
                    print(f"[WARNING] No se pudo enviar email a {oportunidad.usuario.email}: {e}")
        
        print(f"[CELERY] generar_alertas_vencidas completada: {estadisticas}")
        return estadisticas
    
    except Exception as e:
        print(f"[ERROR CELERY] generar_alertas_vencidas: {str(e)}")
        return {'error': str(e)}


@shared_task(name='core.calcular_comisiones')
def calcular_comisiones(periodo=None):
    """
    Calcula automáticamente las comisiones del período especificado.
    
    Si no se especifica período, utiliza el actual (YYYY-MM).
    Busca todas las llamadas exitosas del mes y suma líneas vendidas por ejecutivo.
    
    Args:
        periodo (str): Período en formato 'YYYY-MM' (ej: '2024-01')
    
    Returns:
        dict: Estadísticas de comisiones calculadas
    """
    try:
        from django.contrib.auth.models import User
        from datetime import date
        
        if periodo is None:
            hoy = timezone.now()
            periodo = hoy.strftime('%Y-%m')
        
        # Extraer año y mes del período
        año, mes = periodo.split('-')
        año, mes = int(año), int(mes)
        
        estadisticas = {
            'comisiones_calculadas': 0,
            'monto_total_pagado': 0,
            'usuarios_procesados': 0,
            'periodo': periodo
        }
        
        # Obtener todas las metas del período
        metas = MetaVentas.objects.filter(periodo=periodo).select_related('usuario')
        
        for meta in metas:
            usuario = meta.usuario
            
            # Obtener las llamadas exitosas del período del usuario
            llamadas_exitosas = Llamada.objects.filter(
                creado_por=usuario,
                resultado='EXITOSA',
                fecha_hora__year=año,
                fecha_hora__month=mes
            ).select_related('oportunidad')
            
            # Contar líneas vendidas por tipo
            lineas_portabilidad = 0
            lineas_nueva = 0
            lineas_m2m = 0
            
            for llamada in llamadas_exitosas:
                if llamada.oportunidad:
                    productos = llamada.oportunidad.productos.lower() if llamada.oportunidad.productos else ""
                    
                    if 'portabilidad' in productos or 'portab' in productos:
                        lineas_portabilidad += 1
                    elif 'nueva' in productos or 'new' in productos:
                        lineas_nueva += 1
                    elif 'm2m' in productos or 'maquina' in productos:
                        lineas_m2m += 1
            
            # Calcular comisión según meta
            comision_calculada = Decimal('0')
            
            # Comisión base + por cada línea
            if lineas_portabilidad > 0 or lineas_nueva > 0 or lineas_m2m > 0:
                comision_calculada = Decimal(str(meta.comision_base))
                comision_calculada += (Decimal(str(lineas_portabilidad)) * Decimal(str(meta.comision_por_linea)))
                comision_calculada += (Decimal(str(lineas_nueva)) * Decimal(str(meta.comision_por_linea)))
                comision_calculada += (Decimal(str(lineas_m2m)) * Decimal(str(meta.comision_por_linea * 0.5)))
            
            # Aplicar factor de aceleración si se cumplen metas
            bonificacion = Decimal('0')
            if meta.factor_aceleracion and meta.factor_aceleracion > 1:
                if (lineas_portabilidad >= meta.lineas_portabilidad * 0.9 or
                    lineas_nueva >= meta.lineas_nueva * 0.9 or
                    lineas_m2m >= meta.lineas_m2m * 0.9):
                    bonificacion = comision_calculada * Decimal(str(meta.factor_aceleracion - 1))
            
            total_a_pagar = comision_calculada + bonificacion
            
            # Crear o actualizar registro de comisión
            comision, creada = Comision.objects.update_or_create(
                usuario=usuario,
                periodo=periodo,
                defaults={
                    'lineas_portabilidad_vendidas': lineas_portabilidad,
                    'lineas_nueva_vendidas': lineas_nueva,
                    'lineas_m2m_vendidas': lineas_m2m,
                    'comision_calculada': comision_calculada,
                    'bonificacion_aplicada': bonificacion,
                    'total_a_pagar': total_a_pagar,
                    'meta': meta,
                    'estado': 'CALCULADA',
                    'fecha_calculo': timezone.now()
                }
            )
            
            estadisticas['comisiones_calculadas'] += 1
            estadisticas['monto_total_pagado'] += float(total_a_pagar)
        
        estadisticas['usuarios_procesados'] = len(metas)
        print(f"[CELERY] calcular_comisiones completada: {estadisticas}")
        return estadisticas
    
    except Exception as e:
        print(f"[ERROR CELERY] calcular_comisiones: {str(e)}")
        return {'error': str(e)}


@shared_task(name='core.enviar_resumen_diario')
def enviar_resumen_diario():
    """
    Envía resumen diario de actividades a cada ejecutivo.
    
    Incluye:
    - Oportunidades nuevas del día
    - Alertas generadas
    - Llamadas registradas
    - Vencimientos próximos
    """
    try:
        from django.contrib.auth.models import User
        
        hoy = timezone.now().date()
        
        usuarios = User.objects.filter(is_active=True, is_staff=False)
        
        estadisticas = {
            'emails_enviados': 0,
            'errores': 0
        }
        
        for usuario in usuarios:
            if not usuario.email:
                continue
            
            # Recopilar datos del día para este usuario
            oportunidades_hoy = Oportunidad.objects.filter(
                usuario=usuario,
                created_at__date=hoy
            ).count()

            llamadas_hoy = Llamada.objects.filter(
                creado_por=usuario,
                fecha_hora__date=hoy
            ).count()

            alertas_hoy = Seguimiento.objects.filter(
                asignado_a=usuario,
                tipo='ALERTA',
                created_at__date=hoy
            ).count()

            oportunidades_vencimiento = Oportunidad.objects.filter(
                usuario=usuario,
                estado='ABIERTA',
                fecha_cierre_estimada__range=[hoy, hoy + timedelta(days=3)]
            ).count()
            
            # Preparar contenido del email
            asunto = f"📊 Resumen CRM - {hoy.strftime('%d/%m/%Y')}"
            
            mensaje = f"""
Hola {usuario.get_full_name()},

Aquí está tu resumen de actividades del día:

📈 ACTIVIDADES DEL DÍA:
- Oportunidades nuevas: {oportunidades_hoy}
- Llamadas registradas: {llamadas_hoy}
- Alertas generadas: {alertas_hoy}
- Oportunidades por vencer en 3 días: {oportunidades_vencimiento}

---
Este es un mensaje automático del sistema CRM CLARO.
            """
            
            try:
                send_mail(
                    asunto,
                    mensaje,
                    settings.DEFAULT_FROM_EMAIL,
                    [usuario.email],
                    fail_silently=False
                )
                estadisticas['emails_enviados'] += 1
            except Exception as e:
                print(f"[ERROR] No se pudo enviar email a {usuario.email}: {e}")
                estadisticas['errores'] += 1
        
        print(f"[CELERY] enviar_resumen_diario completada: {estadisticas}")
        return estadisticas
    
    except Exception as e:
        print(f"[ERROR CELERY] enviar_resumen_diario: {str(e)}")
        return {'error': str(e)}


def enviar_notificacion_vencida(oportunidad, usuario):
    """Helper para enviar email de oportunidad vencida"""
    asunto = f"⚠️ ALERTA: Oportunidad vencida - {oportunidad.cliente.nombre_empresa}"
    
    mensaje = f"""
Hola {usuario.get_full_name()},

⚠️ OPORTUNIDAD VENCIDA ⚠️

Cliente: {oportunidad.cliente.nombre_empresa}
Monto: CLP {oportunidad.monto}
Etapa: {oportunidad.get_etapa_display()}
Fecha cierre estimada: {oportunidad.fecha_cierre_estimada.strftime('%d/%m/%Y')}

Por favor, revisar esta oportunidad en el CRM y tomar acciones correctivas.

---
Este es un mensaje automático del sistema CRM CLARO.
    """
    
    send_mail(
        asunto,
        mensaje,
        settings.DEFAULT_FROM_EMAIL,
        [usuario.email],
        fail_silently=False
    )
