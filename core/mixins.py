"""
Mixins para controlar acceso y filtrado por roles de usuario
"""
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Cliente


class AdminOnlyMixin(UserPassesTestMixin, LoginRequiredMixin):
    """
    Mixin que solo permite acceso a administradores.
    Los ejecutivos son redirigidos a su vista de clientes personales.
    """
    def test_func(self):
        return self.request.user.groups.filter(name='Admin').exists() or self.request.user.is_superuser
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            # Si es ejecutivo, redirige a su vista personalizada
            if self.request.user.groups.filter(name='Ejecutivo').exists():
                return redirect('core:ejecutivo_clientes')
            return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
        return redirect(reverse_lazy('core:login'))


class EjecutivoOrAdminMixin(UserPassesTestMixin, LoginRequiredMixin):
    """
    Mixin que permite acceso tanto a ejecutivos como a administradores y managers.
    Los ejecutivos solo ven sus clientes asignados.
    """
    def test_func(self):
        user_groups = self.request.user.groups.values_list('name', flat=True)
        return 'Admin' in user_groups or 'Ejecutivo' in user_groups or 'Manager' in user_groups or 'Vendedor' in user_groups or self.request.user.is_superuser
    
    def handle_no_permission(self):
        return redirect(reverse_lazy('core:login'))


class ClienteQuerysetFilterMixin:
    """
    Mixin que filtra el queryset de clientes según el rol del usuario.
    - Admin: ve todos los clientes
    - Manager: ve clientes asignados a sus ejecutivos subordinados
    - Ejecutivo: solo ve sus clientes asignados
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='Admin').exists():
            # Admin ve todos
            return queryset
        
        # Verificar UserProfile para roles nuevos
        try:
            profile = user.profile
            if profile.es_admin:
                return queryset
            elif profile.es_manager:
                # Manager ve clientes de sus ejecutivos subordinados + sus propios clientes
                subordinados_ids = user.subordinados.values_list('user_id', flat=True)
                return queryset.filter(Q(usuario_asignado_id__in=subordinados_ids) | Q(usuario_asignado=user))
            elif profile.es_ejecutivo:
                # Ejecutivo solo ve sus clientes asignados
                return queryset.filter(usuario_asignado=user)
        except:
            pass
        
        # Fallback para ejecutivos con grupo
        if user.groups.filter(name='Ejecutivo').exists():
            return queryset.filter(usuario_asignado=user)
        
        # Otros usuarios no ven nada
        return queryset.none()


class OportunidadQuerysetFilterMixin:
    """
    Mixin que filtra oportunidades según el rol del usuario.
    - Admin: ve todas las oportunidades
    - Manager: ve oportunidades de sus ejecutivos subordinados
    - Ejecutivo: solo ve sus oportunidades (cliente asignado a él)
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='Admin').exists():
            # Admin ve todas
            return queryset
        
        # Verificar UserProfile para roles nuevos
        try:
            profile = user.profile
            if profile.es_admin:
                return queryset
            elif profile.es_manager:
                # Manager ve oportunidades de sus ejecutivos subordinados + sus propios clientes
                subordinados_ids = user.subordinados.values_list('user_id', flat=True)
                return queryset.filter(Q(cliente__usuario_asignado_id__in=subordinados_ids) | Q(cliente__usuario_asignado=user))
            elif profile.es_ejecutivo:
                # Ejecutivo ve oportunidades donde es el usuario directo O tiene el cliente asignado
                return queryset.filter(Q(usuario=user) | Q(cliente__usuario_asignado=user))
        except:
            pass

        # Fallback para ejecutivos con grupo
        if user.groups.filter(name__in=['Ejecutivo', 'Vendedor']).exists():
            return queryset.filter(Q(usuario=user) | Q(cliente__usuario_asignado=user))

        # Otros usuarios no ven nada
        return queryset.none()


class ContactoQuerysetFilterMixin:
    """
    Mixin que filtra contactos según el rol del usuario.
    - Admin: ve todos los contactos
    - Manager: ve contactos de sus ejecutivos subordinados
    - Ejecutivo: solo ve contactos de sus clientes asignados
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='Admin').exists():
            # Admin ve todos
            return queryset
        
        # Verificar UserProfile para roles nuevos
        try:
            profile = user.profile
            if profile.es_admin:
                return queryset
            elif profile.es_manager:
                # Manager ve contactos de sus ejecutivos subordinados + sus propios clientes
                subordinados_ids = user.subordinados.values_list('user_id', flat=True)
                return queryset.filter(Q(cliente__usuario_asignado_id__in=subordinados_ids) | Q(cliente__usuario_asignado=user))
            elif profile.es_ejecutivo:
                # Ejecutivo solo ve contactos de sus clientes asignados
                return queryset.filter(cliente__usuario_asignado=user)
        except:
            pass
        
        # Fallback para ejecutivos con grupo
        if user.groups.filter(name='Ejecutivo').exists():
            return queryset.filter(cliente__usuario_asignado=user)
        
        # Otros usuarios no ven nada
        return queryset.none()


class LlamadaQuerysetFilterMixin:
    """
    Mixin que filtra llamadas según el rol del usuario.
    - Admin: ve todas las llamadas
    - Manager: ve llamadas de sus ejecutivos subordinados
    - Ejecutivo: solo ve llamadas de sus oportunidades (cliente asignado a él)
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='Admin').exists():
            # Admin ve todas
            return queryset
        
        # Verificar UserProfile para roles nuevos
        try:
            profile = user.profile
            if profile.es_admin:
                return queryset
            elif profile.es_manager:
                # Manager ve llamadas de sus ejecutivos subordinados + sus propios clientes
                subordinados_ids = user.subordinados.values_list('user_id', flat=True)
                return queryset.filter(Q(oportunidad__cliente__usuario_asignado_id__in=subordinados_ids) | Q(oportunidad__cliente__usuario_asignado=user))
            elif profile.es_ejecutivo:
                return queryset.filter(
                    Q(oportunidad__usuario=user) | Q(oportunidad__cliente__usuario_asignado=user)
                )
        except:
            pass

        # Fallback para ejecutivos con grupo
        if user.groups.filter(name__in=['Ejecutivo', 'Vendedor']).exists():
            return queryset.filter(
                Q(oportunidad__usuario=user) | Q(oportunidad__cliente__usuario_asignado=user)
            )

        # Otros usuarios no ven nada
        return queryset.none()


class SeguimientoQuerysetFilterMixin:
    """
    Mixin que filtra seguimientos según el rol del usuario.
    - Admin: ve todos los seguimientos
    - Manager: ve seguimientos de sus ejecutivos subordinados
    - Ejecutivo: solo ve seguimientos de sus oportunidades (cliente asignado a él)
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='Admin').exists():
            # Admin ve todos
            return queryset
        
        # Verificar UserProfile para roles nuevos
        try:
            profile = user.profile
            if profile.es_admin:
                return queryset
            elif profile.es_manager:
                # Manager ve seguimientos de sus ejecutivos subordinados + sus propios clientes
                subordinados_ids = user.subordinados.values_list('user_id', flat=True)
                return queryset.filter(Q(oportunidad__cliente__usuario_asignado_id__in=subordinados_ids) | Q(oportunidad__cliente__usuario_asignado=user))
            elif profile.es_ejecutivo:
                return queryset.filter(
                    Q(oportunidad__usuario=user) | Q(oportunidad__cliente__usuario_asignado=user)
                )
        except:
            pass

        # Fallback para ejecutivos con grupo
        if user.groups.filter(name__in=['Ejecutivo', 'Vendedor']).exists():
            return queryset.filter(
                Q(oportunidad__usuario=user) | Q(oportunidad__cliente__usuario_asignado=user)
            )

        # Otros usuarios no ven nada
        return queryset.none()


class ComisionQuerysetFilterMixin:
    """
    Mixin que filtra comisiones según el rol del usuario.
    - Admin: ve todas las comisiones
    - Manager: ve comisiones de sus ejecutivos subordinados
    - Ejecutivo: solo ve sus propias comisiones
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='Admin').exists():
            # Admin ve todas
            return queryset
        
        # Verificar UserProfile para roles nuevos
        try:
            profile = user.profile
            if profile.es_admin:
                return queryset
            elif profile.es_manager:
                # Manager ve comisiones de sus ejecutivos subordinados + las suyas propias
                subordinados_ids = user.subordinados.values_list('user_id', flat=True)
                return queryset.filter(Q(usuario_id__in=subordinados_ids) | Q(usuario=user))
            elif profile.es_ejecutivo:
                # Ejecutivo solo ve sus propias comisiones
                return queryset.filter(usuario=user)
        except:
            pass
        
        # Fallback para ejecutivos con grupo
        if user.groups.filter(name='Ejecutivo').exists():
            return queryset.filter(usuario=user)
        
        # Otros usuarios no ven nada
        return queryset.none()


def user_is_ejecutivo(user):
    """Función auxiliar para verificar si un usuario es ejecutivo"""
    return user.groups.filter(name='Ejecutivo').exists()


def user_is_admin(user):
    """Función auxiliar para verificar si un usuario es admin"""
    return user.is_superuser or user.groups.filter(name='Admin').exists()


def get_user_role(user):
    """Obtiene el rol del usuario"""
    if user.is_superuser:
        return 'superadmin'
    elif user.groups.filter(name='Admin').exists():
        return 'admin'
    elif user.groups.filter(name='Manager').exists():
        return 'manager'
    elif user.groups.filter(name='Ejecutivo').exists():
        return 'ejecutivo'
    elif user.groups.filter(name='Vendedor').exists():
        return 'vendedor'
    return 'user'


class ManagerOnlyMixin(UserPassesTestMixin, LoginRequiredMixin):
    """
    Mixin que solo permite acceso a usuarios con rol MANAGER en UserProfile.
    """
    def test_func(self):
        try:
            from .models import UserProfile
            profile = self.request.user.profile
            return profile.role == 'MANAGER'
        except:
            return False
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return HttpResponseForbidden("Solo los managers pueden acceder a esta sección.")
        return redirect(reverse_lazy('core:login'))
