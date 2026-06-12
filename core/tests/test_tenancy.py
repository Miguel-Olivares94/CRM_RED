"""
Pruebas de aislamiento multi-tenant (TenantFilterMixin y mixins de rol).

Cubren el caso corregido en mixins.py: un usuario autenticado sin
UserProfile o sin empresa asignada NUNCA debe ver datos de ningún tenant.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from core.models import Cliente, Empresa, UserProfile

User = get_user_model()


class TenantFilterMixinTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa_a = Empresa.objects.create(nombre='Empresa A', tipo='CLIENTE')
        cls.empresa_b = Empresa.objects.create(nombre='Empresa B', tipo='CLIENTE')

        cls.admin_grupo = Group.objects.create(name='Admin')
        cls.ejecutivo_grupo = Group.objects.create(name='Ejecutivo')

        # Admin de Empresa A
        cls.admin_a = User.objects.create_user(
            username='admin_a@empresa-a.cl', email='admin_a@empresa-a.cl', password='x',
        )
        cls.admin_a.groups.add(cls.admin_grupo)
        UserProfile.objects.create(user=cls.admin_a, empresa=cls.empresa_a, role='ADMIN')

        # Admin de Empresa B
        cls.admin_b = User.objects.create_user(
            username='admin_b@empresa-b.cl', email='admin_b@empresa-b.cl', password='x',
        )
        cls.admin_b.groups.add(cls.admin_grupo)
        UserProfile.objects.create(user=cls.admin_b, empresa=cls.empresa_b, role='ADMIN')

        # Usuario sin UserProfile, pero con grupo Ejecutivo (caso de fallback inseguro original)
        cls.usuario_sin_perfil = User.objects.create_user(
            username='sin_perfil@empresa-a.cl', email='sin_perfil@empresa-a.cl', password='x',
        )
        cls.usuario_sin_perfil.groups.add(cls.ejecutivo_grupo)

        # Superusuario
        cls.superuser = User.objects.create_superuser(
            username='root@plataforma.cl', email='root@plataforma.cl', password='x',
        )

        cls.cliente_a = Cliente.objects.create(
            rut='1-9', nombre_empresa='Cliente de A', empresa=cls.empresa_a,
        )
        cls.cliente_b = Cliente.objects.create(
            rut='2-7', nombre_empresa='Cliente de B', empresa=cls.empresa_b,
        )

    def test_admin_solo_ve_clientes_de_su_empresa(self):
        self.client.force_login(self.admin_a)
        resp = self.client.get(reverse('core:cliente_list'))
        clientes = list(resp.context['clientes'])
        self.assertEqual(clientes, [self.cliente_a])

        self.client.force_login(self.admin_b)
        resp = self.client.get(reverse('core:cliente_list'))
        clientes = list(resp.context['clientes'])
        self.assertEqual(clientes, [self.cliente_b])

    def test_usuario_sin_userprofile_no_ve_ningun_cliente(self):
        self.client.force_login(self.usuario_sin_perfil)
        resp = self.client.get(reverse('core:cliente_list'))
        self.assertEqual(list(resp.context['clientes']), [])

    def test_superuser_ve_clientes_de_todas_las_empresas(self):
        self.client.force_login(self.superuser)
        resp = self.client.get(reverse('core:cliente_list'))
        clientes = set(resp.context['clientes'])
        self.assertEqual(clientes, {self.cliente_a, self.cliente_b})
