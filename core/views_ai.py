"""
Endpoints del Asistente / Copiloto de IA.

GET /api/v1/ventas/sugerir-estrategia/<id_oportunidad>/
  → Vendedor: script + objeciones + próximo paso

GET /api/v1/admin/auditar-oportunidad/<id_oportunidad>/
  → Admin/Manager: probabilidad real + alertas de riesgo + cuellos de botella
"""
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

from .models import Contacto, Llamada, Oportunidad, Seguimiento
from .services.ai_assistant import (
    auditar_oportunidad,
    preparar_contacto_vendedor,
    sugerir_estrategia_venta,
)


class SugerirEstrategiaView(LoginRequiredMixin, View):
    """
    Endpoint para Vendedores.
    Requiere autenticación. El ejecutivo solo puede consultar sus propias oportunidades;
    admin y manager pueden consultar cualquiera.
    """

    def get(self, request, id_oportunidad):
        user = request.user
        user_groups = user.groups.values_list("name", flat=True)
        is_admin = user.is_superuser or "Admin" in user_groups or "Manager" in user_groups

        try:
            oportunidad = Oportunidad.objects.select_related(
                "cliente", "usuario"
            ).get(pk=id_oportunidad)
        except Oportunidad.DoesNotExist:
            return JsonResponse({"error": "Oportunidad no encontrada"}, status=404)

        if not is_admin and oportunidad.usuario != user:
            return JsonResponse({"error": "Sin permiso para esta oportunidad"}, status=403)

        gestiones = list(
            Llamada.objects.filter(oportunidad=oportunidad)
            .select_related("contacto")
            .order_by("-fecha_hora")[:10]
        )
        seguimientos = list(
            Seguimiento.objects.filter(
                oportunidad=oportunidad,
                estado__in=["PENDIENTE", "EN_PROGRESO"],
            ).order_by("fecha_vencimiento")[:5]
        )

        try:
            resultado = sugerir_estrategia_venta(oportunidad, gestiones, seguimientos)
        except Exception as exc:
            return JsonResponse({"error": f"Error en el servicio de IA: {str(exc)}"}, status=502)

        return JsonResponse({
            "oportunidad_id": oportunidad.pk,
            "cliente": oportunidad.cliente.nombre_empresa,
            "etapa": oportunidad.get_etapa_display(),
            **resultado,
        })


class PrepararContactoView(LoginRequiredMixin, View):
    """
    Endpoint para Vendedores.
    Analiza el perfil de un contacto y sugiere cómo abordarlo.
    """

    def get(self, request, id_contacto):
        user = request.user
        user_groups = user.groups.values_list("name", flat=True)
        is_admin = user.is_superuser or "Admin" in user_groups or "Manager" in user_groups

        try:
            contacto = Contacto.objects.select_related("cliente").get(pk=id_contacto)
        except Contacto.DoesNotExist:
            return JsonResponse({"error": "Contacto no encontrado"}, status=404)

        if not is_admin and contacto.cliente.usuario_asignado != user:
            return JsonResponse({"error": "Sin permiso para este contacto"}, status=403)

        llamadas = list(
            Llamada.objects.filter(contacto=contacto)
            .order_by("-fecha_hora")[:10]
        )
        oportunidades = list(
            Oportunidad.objects.filter(
                cliente=contacto.cliente, estado="ABIERTA"
            ).order_by("-fecha_creacion")[:5]
        )

        try:
            resultado = preparar_contacto_vendedor(contacto, llamadas, oportunidades)
        except Exception as exc:
            return JsonResponse({"error": f"Error en el servicio de IA: {str(exc)}"}, status=502)

        return JsonResponse({
            "contacto_id": contacto.pk,
            "nombre": contacto.nombre,
            "empresa": contacto.cliente.nombre_empresa,
            **resultado,
        })


class AuditarOportunidadView(LoginRequiredMixin, View):
    """
    Endpoint para Administradores y Managers.
    Analiza la salud de la venta con criterio objetivo.
    """

    def get(self, request, id_oportunidad):
        user = request.user
        user_groups = user.groups.values_list("name", flat=True)
        is_admin = user.is_superuser or "Admin" in user_groups or "Manager" in user_groups

        if not is_admin:
            return JsonResponse({"error": "Acceso restringido a administradores"}, status=403)

        try:
            oportunidad = Oportunidad.objects.select_related(
                "cliente", "usuario"
            ).get(pk=id_oportunidad)
        except Oportunidad.DoesNotExist:
            return JsonResponse({"error": "Oportunidad no encontrada"}, status=404)

        gestiones = list(
            Llamada.objects.filter(oportunidad=oportunidad)
            .select_related("contacto")
            .order_by("-fecha_hora")[:15]
        )
        seguimientos = list(
            Seguimiento.objects.filter(oportunidad=oportunidad)
            .order_by("-fecha_vencimiento")[:10]
        )

        try:
            resultado = auditar_oportunidad(oportunidad, gestiones, seguimientos)
        except Exception as exc:
            return JsonResponse({"error": f"Error en el servicio de IA: {str(exc)}"}, status=502)

        return JsonResponse({
            "oportunidad_id": oportunidad.pk,
            "cliente": oportunidad.cliente.nombre_empresa,
            "ejecutivo": oportunidad.usuario.get_full_name() or oportunidad.usuario.email,
            "etapa": oportunidad.get_etapa_display(),
            "estado": oportunidad.get_estado_display(),
            **resultado,
        })
