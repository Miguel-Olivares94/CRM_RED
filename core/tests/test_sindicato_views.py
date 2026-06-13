from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from core.models import Empresa, MovimientoSindicato, SocioSindicato, TipoBeneficioSindicato, UserProfile


User = get_user_model()


class SindicatoViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa_a = Empresa.objects.create(nombre='Empresa A', tipo='CLIENTE')
        cls.empresa_b = Empresa.objects.create(nombre='Empresa B', tipo='CLIENTE')

        cls.grp_admin = Group.objects.create(name='Administracion')
        cls.grp_tesoreria = Group.objects.create(name='Tesoreria')
        cls.grp_dirigente = Group.objects.create(name='Dirigente')

        cls.admin_a = User.objects.create_user(username='admin_a', email='admin_a@test.cl', password='x')
        cls.admin_a.groups.add(cls.grp_admin)
        UserProfile.objects.create(user=cls.admin_a, empresa=cls.empresa_a, role='ADMIN')

        cls.tesoreria_a = User.objects.create_user(username='tes_a', email='tes_a@test.cl', password='x')
        cls.tesoreria_a.groups.add(cls.grp_tesoreria)
        UserProfile.objects.create(user=cls.tesoreria_a, empresa=cls.empresa_a, role='ADMIN')

        cls.dirigente_a = User.objects.create_user(username='dir_a', email='dir_a@test.cl', password='x')
        cls.dirigente_a.groups.add(cls.grp_dirigente)
        UserProfile.objects.create(user=cls.dirigente_a, empresa=cls.empresa_a, role='ADMIN')

        cls.admin_b = User.objects.create_user(username='admin_b', email='admin_b@test.cl', password='x')
        cls.admin_b.groups.add(cls.grp_admin)
        UserProfile.objects.create(user=cls.admin_b, empresa=cls.empresa_b, role='ADMIN')

        cls.socio_a = SocioSindicato.objects.create(
            empresa=cls.empresa_a,
            rut='12345678-5',
            nombre='Socio A',
        )
        cls.socio_b = SocioSindicato.objects.create(
            empresa=cls.empresa_b,
            rut='11111111-1',
            nombre='Socio B',
        )

        cls.benef_a = TipoBeneficioSindicato.objects.create(
            empresa=cls.empresa_a,
            codigo='GAS',
            nombre='Gas',
            estado=TipoBeneficioSindicato.ESTADO_ACTIVO,
        )
        cls.benef_b = TipoBeneficioSindicato.objects.create(
            empresa=cls.empresa_b,
            codigo='TEL',
            nombre='Telefonia',
            estado=TipoBeneficioSindicato.ESTADO_ACTIVO,
        )

        MovimientoSindicato.objects.create(
            empresa=cls.empresa_a,
            socio=cls.socio_a,
            tipo_beneficio=cls.benef_a,
            periodo='2026-06',
            monto=10000,
            observacion='ok',
            referencia_externa='A-1',
        )
        MovimientoSindicato.objects.create(
            empresa=cls.empresa_b,
            socio=cls.socio_b,
            tipo_beneficio=cls.benef_b,
            periodo='2026-06',
            monto=20000,
            observacion='ok',
            referencia_externa='B-1',
        )

    def test_usuario_no_autenticado_redirige_login(self):
        resp = self.client.get(reverse('core:sindicato_socio_list'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('core:login'), resp.url)

    def test_usuario_autenticado_ve_datos_su_empresa(self):
        self.client.force_login(self.admin_a)
        resp = self.client.get(reverse('core:sindicato_socio_list'))
        self.assertEqual(resp.status_code, 200)
        socios = list(resp.context['socios'])
        self.assertEqual(socios, [self.socio_a])

    def test_empresa_a_no_puede_editar_socio_empresa_b(self):
        self.client.force_login(self.admin_a)
        resp = self.client.get(reverse('core:sindicato_socio_update', kwargs={'pk': self.socio_b.pk}))
        self.assertEqual(resp.status_code, 404)

    def test_listados_no_mezclan_tenant(self):
        self.client.force_login(self.tesoreria_a)
        resp = self.client.get(reverse('core:sindicato_movimiento_list'))
        self.assertEqual(resp.status_code, 200)
        movs = list(resp.context['movimientos'])
        self.assertEqual(len(movs), 1)
        self.assertEqual(movs[0].empresa, self.empresa_a)

    def test_consulta_rut_no_devuelve_datos_otro_tenant(self):
        self.client.force_login(self.tesoreria_a)
        resp = self.client.get(reverse('core:sindicato_consulta_rut'), {'rut': '11.111.111-1'})
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.context['socio'])

    def test_permisos_admin_crud_socios_beneficios(self):
        self.client.force_login(self.admin_a)
        resp_list = self.client.get(reverse('core:sindicato_socio_list'))
        resp_new = self.client.get(reverse('core:sindicato_socio_create'))
        resp_benef = self.client.get(reverse('core:sindicato_beneficio_create'))
        self.assertEqual(resp_list.status_code, 200)
        self.assertEqual(resp_new.status_code, 200)
        self.assertEqual(resp_benef.status_code, 200)

    def test_permisos_tesoreria_crud_movimientos_y_consulta(self):
        self.client.force_login(self.tesoreria_a)
        resp_mov = self.client.get(reverse('core:sindicato_movimiento_create'))
        resp_cons = self.client.get(reverse('core:sindicato_consulta_rut'))
        resp_socio_create = self.client.get(reverse('core:sindicato_socio_create'))
        self.assertEqual(resp_mov.status_code, 200)
        self.assertEqual(resp_cons.status_code, 200)
        self.assertEqual(resp_socio_create.status_code, 403)

    def test_permisos_dirigente_solo_lectura_y_consulta(self):
        self.client.force_login(self.dirigente_a)
        resp_socio_list = self.client.get(reverse('core:sindicato_socio_list'))
        resp_mov_list = self.client.get(reverse('core:sindicato_movimiento_list'))
        resp_cons = self.client.get(reverse('core:sindicato_consulta_rut'))
        resp_mov_create = self.client.get(reverse('core:sindicato_movimiento_create'))
        self.assertEqual(resp_socio_list.status_code, 200)
        self.assertEqual(resp_mov_list.status_code, 200)
        self.assertEqual(resp_cons.status_code, 200)
        self.assertEqual(resp_mov_create.status_code, 403)

    def test_create_movimiento_usa_empresa_usuario(self):
        self.client.force_login(self.tesoreria_a)
        resp = self.client.post(
            reverse('core:sindicato_movimiento_create'),
            data={
                'socio': self.socio_a.pk,
                'tipo_beneficio': self.benef_a.pk,
                'periodo': '2026-07',
                'monto': '15000',
                'estado': 'PENDIENTE',
                'observacion': 'nuevo',
                'referencia_externa': 'A-2',
                'empresa_id': self.empresa_b.pk,  # intento de inyección
            },
        )
        self.assertEqual(resp.status_code, 302)
        mov = MovimientoSindicato.objects.get(referencia_externa='A-2')
        self.assertEqual(mov.empresa, self.empresa_a)

    def test_update_movimiento_no_permite_otro_tenant(self):
        mov_b = MovimientoSindicato.objects.get(empresa=self.empresa_b)
        self.client.force_login(self.tesoreria_a)
        resp = self.client.get(reverse('core:sindicato_movimiento_update', kwargs={'pk': mov_b.pk}))
        self.assertEqual(resp.status_code, 404)
