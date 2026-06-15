from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from core.models import Empresa, SocioSindicato, TipoBeneficioSindicato, UserProfile


User = get_user_model()


class SindiAppIdentityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa_a = Empresa.objects.create(nombre='Empresa A', tipo='CLIENTE')
        cls.empresa_b = Empresa.objects.create(nombre='Empresa B', tipo='CLIENTE')

        cls.grp_admin = Group.objects.create(name='Administracion')
        cls.grp_tesoreria = Group.objects.create(name='Tesoreria')
        cls.grp_dirigente = Group.objects.create(name='Dirigente')

        cls.tesoreria_a = User.objects.create_user(
            username='tes_sindiapp',
            email='tes_sindiapp@test.cl',
            password='secret123',
        )
        cls.tesoreria_a.groups.add(cls.grp_tesoreria)
        UserProfile.objects.create(user=cls.tesoreria_a, empresa=cls.empresa_a, role='ADMIN')

        cls.dirigente_a = User.objects.create_user(
            username='dir_sindiapp',
            email='dir_sindiapp@test.cl',
            password='secret123',
        )
        cls.dirigente_a.groups.add(cls.grp_dirigente)
        UserProfile.objects.create(user=cls.dirigente_a, empresa=cls.empresa_a, role='ADMIN')

        cls.admin_b = User.objects.create_user(
            username='admin_b_sindiapp',
            email='admin_b_sindiapp@test.cl',
            password='secret123',
        )
        cls.admin_b.groups.add(cls.grp_admin)
        UserProfile.objects.create(user=cls.admin_b, empresa=cls.empresa_b, role='ADMIN')

        cls.socio_a = SocioSindicato.objects.create(empresa=cls.empresa_a, rut='12.345.678-5', nombre='Socio A')
        SocioSindicato.objects.create(empresa=cls.empresa_b, rut='11.111.111-1', nombre='Socio B')

        TipoBeneficioSindicato.objects.create(
            empresa=cls.empresa_a,
            codigo='GAS',
            nombre='Gas',
            estado=TipoBeneficioSindicato.ESTADO_ACTIVO,
        )

    def test_sindiapp_login_carga_correctamente(self):
        resp = self.client.get(reverse('core:sindiapp_login'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'SindiApp')
        self.assertNotContains(resp, 'CRM GESTIÓN')

    def test_sindiapp_dashboard_carga_para_usuario_sindical(self):
        self.client.force_login(self.tesoreria_a)
        resp = self.client.get(reverse('core:sindiapp_dashboard'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Dashboard sindical')

    def test_sindiapp_no_muestra_menu_crm(self):
        self.client.force_login(self.tesoreria_a)
        resp = self.client.get(reverse('core:sindiapp_movimiento_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'SindiApp')
        self.assertContains(resp, 'Movimientos')
        self.assertNotContains(resp, 'Clientes')
        self.assertNotContains(resp, 'Oportunidades')
        self.assertNotContains(resp, 'Comisiones')
        self.assertNotContains(resp, 'Metas de Ventas')

    def test_rutas_sindiapp_respetan_tenant_y_permisos(self):
        self.client.force_login(self.tesoreria_a)
        resp_list = self.client.get(reverse('core:sindiapp_movimiento_list'))
        self.assertEqual(resp_list.status_code, 200)
        for mov in resp_list.context['movimientos']:
            self.assertEqual(mov.empresa, self.empresa_a)

        self.client.force_login(self.dirigente_a)
        resp_forbidden = self.client.get(reverse('core:sindiapp_movimiento_create'))
        self.assertEqual(resp_forbidden.status_code, 403)

    def test_usuario_sin_login_redirige_a_login_sindiapp(self):
        resp = self.client.get(reverse('core:sindiapp_socio_list'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('core:sindiapp_login'), resp.url)
