from io import BytesIO

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from openpyxl import load_workbook

from core.models import (
    AuditoriaSindicato,
    ConsolidadoMensualSindicato,
    Empresa,
    MovimientoSindicato,
    SocioSindicato,
    TipoBeneficioSindicato,
    UserProfile,
)


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


class SindicatoImportViewTests(TestCase):
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
        cls.benef_inactivo_a = TipoBeneficioSindicato.objects.create(
            empresa=cls.empresa_a,
            codigo='COP',
            nombre='Copeuch',
            estado=TipoBeneficioSindicato.ESTADO_INACTIVO,
        )

    def _csv_file(self, content, name='movimientos.csv'):
        return SimpleUploadedFile(name, content.encode('utf-8'), content_type='text/csv')

    def test_usuario_sin_permiso_recibe_403(self):
        self.client.force_login(self.dirigente_a)
        resp = self.client.get(reverse('core:sindicato_movimiento_import'))
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(AuditoriaSindicato.objects.count(), 0)

    def test_archivo_valido_crea_movimientos(self):
        self.client.force_login(self.tesoreria_a)
        content = (
            'RUT,Nombre,Monto,Observacion,Referencia externa,Site\n'
            '12.345.678-5,Socio A,10000,ok,REF-OK-1,Site A\n'
            '11.111.111-1,Socio Nuevo Tenant A,12000,alta,REF-OK-2,Site B\n'
        )
        file_obj = self._csv_file(content)

        preview = self.client.post(
            reverse('core:sindicato_movimiento_import'),
            data={
                'tipo_beneficio': self.benef_a.id,
                'periodo': '2026-06',
                'archivo': file_obj,
            },
        )
        self.assertEqual(preview.status_code, 200)
        self.assertContains(preview, 'Válidas: 2')

        confirm = self.client.post(reverse('core:sindicato_movimiento_import'), data={'action': 'confirmar'})
        self.assertEqual(confirm.status_code, 200)
        self.assertContains(confirm, 'Movimientos creados: 2')

        self.assertEqual(
            MovimientoSindicato.objects.filter(empresa=self.empresa_a, periodo='2026-06').count(),
            2,
        )
        socio_nuevo = SocioSindicato.objects.get(empresa=self.empresa_a, rut='11111111-1')
        self.assertEqual(socio_nuevo.nombre, 'Socio Nuevo Tenant A')
        self.assertEqual(SocioSindicato.objects.filter(empresa=self.empresa_b, rut='11111111-1').count(), 1)

    def test_rut_invalido_rechaza_fila(self):
        self.client.force_login(self.tesoreria_a)
        content = 'RUT,Nombre,Monto\n12.345.678-9,Socio Malo,10000\n'
        file_obj = self._csv_file(content)

        preview = self.client.post(
            reverse('core:sindicato_movimiento_import'),
            data={'tipo_beneficio': self.benef_a.id, 'periodo': '2026-06', 'archivo': file_obj},
        )
        self.assertEqual(preview.status_code, 200)
        self.assertContains(preview, 'Rechazadas: 1')
        self.assertContains(preview, 'RUT inválido o vacío.')

        confirm = self.client.post(reverse('core:sindicato_movimiento_import'), data={'action': 'confirmar'})
        self.assertEqual(confirm.status_code, 200)
        self.assertContains(confirm, 'Movimientos creados: 0')

    def test_monto_cero_rechaza_fila(self):
        self.client.force_login(self.tesoreria_a)
        content = 'RUT,Nombre,Monto\n12.345.678-5,Socio A,0\n'
        file_obj = self._csv_file(content)

        preview = self.client.post(
            reverse('core:sindicato_movimiento_import'),
            data={'tipo_beneficio': self.benef_a.id, 'periodo': '2026-06', 'archivo': file_obj},
        )
        self.assertEqual(preview.status_code, 200)
        self.assertContains(preview, 'Monto debe ser mayor a cero.')

        confirm = self.client.post(reverse('core:sindicato_movimiento_import'), data={'action': 'confirmar'})
        self.assertEqual(confirm.status_code, 200)
        self.assertContains(confirm, 'Movimientos creados: 0')

    def test_beneficio_inactivo_rechaza_importacion(self):
        self.client.force_login(self.admin_a)
        content = 'RUT,Nombre,Monto\n12.345.678-5,Socio A,10000\n'
        file_obj = self._csv_file(content)

        resp = self.client.post(
            reverse('core:sindicato_movimiento_import'),
            data={
                'tipo_beneficio': self.benef_inactivo_a.id,
                'periodo': '2026-06',
                'archivo': file_obj,
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'está inactivo')
        self.assertEqual(MovimientoSindicato.objects.filter(empresa=self.empresa_a).count(), 0)

    def test_duplicado_con_referencia_externa_rechaza(self):
        MovimientoSindicato.objects.create(
            empresa=self.empresa_a,
            socio=self.socio_a,
            tipo_beneficio=self.benef_a,
            periodo='2026-06',
            monto=10000,
            referencia_externa='REF-DUP',
        )
        self.client.force_login(self.tesoreria_a)
        content = 'RUT,Nombre,Monto,Referencia externa\n12.345.678-5,Socio A,10000,REF-DUP\n'
        file_obj = self._csv_file(content)

        preview = self.client.post(
            reverse('core:sindicato_movimiento_import'),
            data={'tipo_beneficio': self.benef_a.id, 'periodo': '2026-06', 'archivo': file_obj},
        )
        self.assertEqual(preview.status_code, 200)
        self.assertContains(preview, 'Referencia externa duplicada')
        self.assertContains(preview, 'Rechazadas: 1')

        confirm = self.client.post(reverse('core:sindicato_movimiento_import'), data={'action': 'confirmar'})
        self.assertEqual(confirm.status_code, 200)
        self.assertContains(confirm, 'Movimientos creados: 0')

    def test_tenant_isolation_importa_solo_empresa_usuario(self):
        self.client.force_login(self.tesoreria_a)
        content = 'RUT,Nombre,Monto,Referencia externa\n11.111.111-1,Socio Tenant A,9000,REF-TENANT-1\n'
        file_obj = self._csv_file(content)

        self.client.post(
            reverse('core:sindicato_movimiento_import'),
            data={'tipo_beneficio': self.benef_a.id, 'periodo': '2026-07', 'archivo': file_obj},
        )
        self.client.post(reverse('core:sindicato_movimiento_import'), data={'action': 'confirmar'})

        mov = MovimientoSindicato.objects.get(referencia_externa='REF-TENANT-1')
        self.assertEqual(mov.empresa, self.empresa_a)
        self.assertEqual(mov.socio.empresa, self.empresa_a)
        self.assertEqual(SocioSindicato.objects.filter(empresa=self.empresa_b, rut='11111111-1').count(), 1)

    def test_confirmar_importacion_crea_auditoria(self):
        self.client.force_login(self.tesoreria_a)
        content = 'RUT,Nombre,Monto,Referencia externa\n12.345.678-5,Socio A,10000,REF-AUD-1\n'
        file_obj = self._csv_file(content, name='import_auditoria.csv')

        preview = self.client.post(
            reverse('core:sindicato_movimiento_import'),
            data={'tipo_beneficio': self.benef_a.id, 'periodo': '2026-06', 'archivo': file_obj},
        )
        self.assertEqual(preview.status_code, 200)

        confirm = self.client.post(reverse('core:sindicato_movimiento_import'), data={'action': 'confirmar'})
        self.assertEqual(confirm.status_code, 200)

        audit = AuditoriaSindicato.objects.latest('created_at')
        self.assertEqual(audit.accion, 'IMPORTAR_MOVIMIENTOS')
        self.assertEqual(audit.entidad, 'MovimientoSindicato')
        self.assertEqual(audit.periodo, '2026-06')
        self.assertEqual(audit.empresa, self.empresa_a)
        self.assertEqual(audit.usuario, self.tesoreria_a)
        self.assertEqual(audit.payload.get('total_filas_leidas'), 1)
        self.assertEqual(audit.payload.get('total_importadas'), 1)
        self.assertEqual(audit.payload.get('total_rechazadas'), 0)
        self.assertEqual(audit.payload.get('nombre_archivo'), 'import_auditoria.csv')

    def test_auditoria_queda_asociada_a_empresa_correcta(self):
        self.client.force_login(self.tesoreria_a)
        content = 'RUT,Nombre,Monto,Referencia externa\n11.111.111-1,Socio Tenant A,9000,REF-AUD-2\n'
        file_obj = self._csv_file(content, name='import_tenant.csv')

        self.client.post(
            reverse('core:sindicato_movimiento_import'),
            data={'tipo_beneficio': self.benef_a.id, 'periodo': '2026-07', 'archivo': file_obj},
        )
        self.client.post(reverse('core:sindicato_movimiento_import'), data={'action': 'confirmar'})

        audit = AuditoriaSindicato.objects.latest('created_at')
        self.assertEqual(audit.empresa, self.empresa_a)
        self.assertNotEqual(audit.empresa, self.empresa_b)


class SindicatoConsolidadoViewsTests(TestCase):
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

        cls.socio_a = SocioSindicato.objects.create(
            empresa=cls.empresa_a,
            rut='12345678-5',
            nombre='Socio A',
            estado_laboral=SocioSindicato.ESTADO_LABORAL_ACTIVO,
            estado=SocioSindicato.ESTADO_ACTIVO,
        )
        cls.benef_a = TipoBeneficioSindicato.objects.create(
            empresa=cls.empresa_a,
            codigo='GAS',
            nombre='Gas',
            estado=TipoBeneficioSindicato.ESTADO_ACTIVO,
            orden_export=1,
        )

        cls.socio_b = SocioSindicato.objects.create(
            empresa=cls.empresa_b,
            rut='11111111-1',
            nombre='Socio B',
            estado_laboral=SocioSindicato.ESTADO_LABORAL_ACTIVO,
            estado=SocioSindicato.ESTADO_ACTIVO,
        )
        cls.benef_b = TipoBeneficioSindicato.objects.create(
            empresa=cls.empresa_b,
            codigo='GAS',
            nombre='Gas',
            estado=TipoBeneficioSindicato.ESTADO_ACTIVO,
            orden_export=1,
        )

    def test_dirigente_ve_historial_pero_no_genera(self):
        self.client.force_login(self.dirigente_a)
        resp_hist = self.client.get(reverse('core:sindicato_consolidado_historial'))
        self.assertEqual(resp_hist.status_code, 200)

        resp_gen = self.client.post(
            reverse('core:sindicato_consolidado_generar'),
            data={'periodo': '2026-08'},
        )
        self.assertEqual(resp_gen.status_code, 403)

    def test_generar_consolidado_desde_view_usa_servicio(self):
        MovimientoSindicato.objects.create(
            empresa=self.empresa_a,
            socio=self.socio_a,
            tipo_beneficio=self.benef_a,
            periodo='2026-08',
            monto=10000,
            estado=MovimientoSindicato.ESTADO_VALIDADO,
            referencia_externa='A-1',
        )
        self.client.force_login(self.tesoreria_a)

        resp = self.client.post(
            reverse('core:sindicato_consolidado_generar'),
            data={'periodo': '2026-08'},
        )
        self.assertEqual(resp.status_code, 302)

        cons = ConsolidadoMensualSindicato.objects.get(empresa=self.empresa_a, periodo='2026-08')
        self.assertEqual(cons.total_socios, 1)
        self.assertEqual(cons.total_monto, 10000)
        self.assertTrue(
            AuditoriaSindicato.objects.filter(
                empresa=self.empresa_a,
                accion='GENERAR_CONSOLIDADO',
                periodo='2026-08',
            ).exists()
        )

    def test_cerrar_periodo_desde_view(self):
        MovimientoSindicato.objects.create(
            empresa=self.empresa_a,
            socio=self.socio_a,
            tipo_beneficio=self.benef_a,
            periodo='2026-09',
            monto=5000,
            estado=MovimientoSindicato.ESTADO_VALIDADO,
            referencia_externa='A-2',
        )
        self.client.force_login(self.admin_a)
        self.client.post(reverse('core:sindicato_consolidado_generar'), data={'periodo': '2026-09'})

        resp_cerrar = self.client.post(
            reverse('core:sindicato_consolidado_cerrar'),
            data={'periodo': '2026-09'},
        )
        self.assertEqual(resp_cerrar.status_code, 302)

        cons = ConsolidadoMensualSindicato.objects.get(empresa=self.empresa_a, periodo='2026-09')
        self.assertEqual(cons.estado, ConsolidadoMensualSindicato.ESTADO_CERRADO)
        self.assertTrue(
            AuditoriaSindicato.objects.filter(
                empresa=self.empresa_a,
                accion='CERRAR_CONSOLIDADO',
                periodo='2026-09',
            ).exists()
        )

    def test_historial_no_mezcla_tenant(self):
        ConsolidadoMensualSindicato.objects.create(
            empresa=self.empresa_b,
            periodo='2026-08',
            estado=ConsolidadoMensualSindicato.ESTADO_ABIERTO,
            total_socios=1,
            total_monto=1000,
        )
        self.client.force_login(self.tesoreria_a)

        resp = self.client.get(reverse('core:sindicato_consolidado_historial'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(list(resp.context['consolidados']), [])

    def test_dirigente_recibe_403_en_exportacion(self):
        cons = ConsolidadoMensualSindicato.objects.create(
            empresa=self.empresa_a,
            periodo='2026-12',
            estado=ConsolidadoMensualSindicato.ESTADO_CERRADO,
            total_socios=0,
            total_monto=0,
        )
        self.client.force_login(self.dirigente_a)
        resp = self.client.get(reverse('core:sindicato_consolidado_exportar', kwargs={'pk': cons.pk}))
        self.assertEqual(resp.status_code, 403)

    def test_no_exporta_consolidado_otro_tenant(self):
        cons_b = ConsolidadoMensualSindicato.objects.create(
            empresa=self.empresa_b,
            periodo='2026-12',
            estado=ConsolidadoMensualSindicato.ESTADO_CERRADO,
            total_socios=0,
            total_monto=0,
        )
        self.client.force_login(self.tesoreria_a)
        resp = self.client.get(reverse('core:sindicato_consolidado_exportar', kwargs={'pk': cons_b.pk}))
        self.assertEqual(resp.status_code, 302)

    def test_exporta_excel_consolidado_cerrado_desde_endpoint(self):
        MovimientoSindicato.objects.create(
            empresa=self.empresa_a,
            socio=self.socio_a,
            tipo_beneficio=self.benef_a,
            periodo='2026-12',
            monto=8000,
            estado=MovimientoSindicato.ESTADO_VALIDADO,
            referencia_externa='EXP-1',
        )
        self.client.force_login(self.admin_a)
        self.client.post(reverse('core:sindicato_consolidado_generar'), data={'periodo': '2026-12'})
        self.client.post(reverse('core:sindicato_consolidado_cerrar'), data={'periodo': '2026-12'})
        cons = ConsolidadoMensualSindicato.objects.get(empresa=self.empresa_a, periodo='2026-12')

        resp = self.client.get(reverse('core:sindicato_consolidado_exportar', kwargs={'pk': cons.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            resp['Content-Type'],
        )
        self.assertTrue(
            AuditoriaSindicato.objects.filter(
                empresa=self.empresa_a,
                accion='EXPORTAR_CONSOLIDADO',
                periodo='2026-12',
            ).exists()
        )

    def test_detalle_consolidado_renderiza_sin_nameerror(self):
        MovimientoSindicato.objects.create(
            empresa=self.empresa_a,
            socio=self.socio_a,
            tipo_beneficio=self.benef_a,
            periodo='2026-10',
            monto=6000,
            estado=MovimientoSindicato.ESTADO_VALIDADO,
            referencia_externa='DET-1',
        )
        self.client.force_login(self.tesoreria_a)
        self.client.post(reverse('core:sindicato_consolidado_generar'), data={'periodo': '2026-10'})
        cons = ConsolidadoMensualSindicato.objects.get(empresa=self.empresa_a, periodo='2026-10')

        resp = self.client.get(reverse('core:sindicato_consolidado_detalle', kwargs={'pk': cons.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(list(resp.context['detalles'])[0].monto_aprobado, 6000)

    def test_exportar_consolidado_ya_exportado_sigue_disponible(self):
        MovimientoSindicato.objects.create(
            empresa=self.empresa_a,
            socio=self.socio_a,
            tipo_beneficio=self.benef_a,
            periodo='2026-11',
            monto=7000,
            estado=MovimientoSindicato.ESTADO_VALIDADO,
            referencia_externa='EXP-REPEAT-1',
        )
        self.client.force_login(self.admin_a)
        self.client.post(reverse('core:sindicato_consolidado_generar'), data={'periodo': '2026-11'})
        self.client.post(reverse('core:sindicato_consolidado_cerrar'), data={'periodo': '2026-11'})
        cons = ConsolidadoMensualSindicato.objects.get(empresa=self.empresa_a, periodo='2026-11')

        first = self.client.get(reverse('core:sindicato_consolidado_exportar', kwargs={'pk': cons.pk}))
        self.assertEqual(first.status_code, 200)
        cons.refresh_from_db()
        self.assertEqual(cons.estado, ConsolidadoMensualSindicato.ESTADO_EXPORTADO)

        second = self.client.get(reverse('core:sindicato_consolidado_exportar', kwargs={'pk': cons.pk}))
        self.assertEqual(second.status_code, 200)


class SindicatoConsolidadoE2EFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa = Empresa.objects.create(nombre='Empresa E2E', tipo='CLIENTE')
        cls.grp_tesoreria = Group.objects.create(name='Tesoreria')

        cls.tesoreria = User.objects.create_user(username='tes_e2e', email='tes_e2e@test.cl', password='x')
        cls.tesoreria.groups.add(cls.grp_tesoreria)
        UserProfile.objects.create(user=cls.tesoreria, empresa=cls.empresa, role='ADMIN')

        cls.benef = TipoBeneficioSindicato.objects.create(
            empresa=cls.empresa,
            codigo='GAS',
            nombre='Gas',
            estado=TipoBeneficioSindicato.ESTADO_ACTIVO,
            orden_export=1,
        )

    def test_flujo_e2e_importar_generar_detalle_cerrar_exportar_y_validar_excel(self):
        self.client.force_login(self.tesoreria)
        periodo = '2026-12'

        # 1) Importar movimientos
        csv_content = (
            'RUT,Nombre,Monto,Observacion,Referencia externa,Site\n'
            '12.345.678-5,Socio Uno,10000,ok,REF-E2E-1,Site Norte\n'
            '11.111.111-1,Socio Dos,15000,ok,REF-E2E-2,Site Sur\n'
        )
        preview = self.client.post(
            reverse('core:sindicato_movimiento_import'),
            data={
                'tipo_beneficio': self.benef.id,
                'periodo': periodo,
                'archivo': SimpleUploadedFile('e2e_movs.csv', csv_content.encode('utf-8'), content_type='text/csv'),
            },
        )
        self.assertEqual(preview.status_code, 200)
        self.assertContains(preview, 'Válidas: 2')

        confirm = self.client.post(reverse('core:sindicato_movimiento_import'), data={'action': 'confirmar'})
        self.assertEqual(confirm.status_code, 200)
        self.assertContains(confirm, 'Movimientos creados: 2')
        self.assertEqual(MovimientoSindicato.objects.filter(empresa=self.empresa, periodo=periodo).count(), 2)

        # 2) Generar consolidado
        generar = self.client.post(reverse('core:sindicato_consolidado_generar'), data={'periodo': periodo})
        self.assertEqual(generar.status_code, 302)
        consolidado = ConsolidadoMensualSindicato.objects.get(empresa=self.empresa, periodo=periodo)
        self.assertEqual(consolidado.estado, ConsolidadoMensualSindicato.ESTADO_ABIERTO)
        self.assertEqual(consolidado.total_socios, 2)
        self.assertEqual(int(consolidado.total_monto), 25000)

        # 3) Ver detalle
        detalle = self.client.get(reverse('core:sindicato_consolidado_detalle', kwargs={'pk': consolidado.pk}))
        self.assertEqual(detalle.status_code, 200)
        self.assertEqual(len(list(detalle.context['detalles'])), 2)

        # 4) Cerrar período
        cerrar = self.client.post(reverse('core:sindicato_consolidado_cerrar'), data={'periodo': periodo})
        self.assertEqual(cerrar.status_code, 302)
        consolidado.refresh_from_db()
        self.assertEqual(consolidado.estado, ConsolidadoMensualSindicato.ESTADO_CERRADO)

        # 5) Exportar Excel
        export = self.client.get(reverse('core:sindicato_consolidado_exportar', kwargs={'pk': consolidado.pk}))
        self.assertEqual(export.status_code, 200)
        self.assertIn(
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            export['Content-Type'],
        )

        # 6) Validar contenido del archivo generado
        wb = load_workbook(filename=BytesIO(export.content))
        ws = wb['Consolidado']
        headers = [c.value for c in ws[1]]
        self.assertEqual(headers[:4], ['RUT', 'Nombre', 'Site', 'Estado laboral'])
        self.assertIn('Gas', headers)
        self.assertEqual(headers[-1], 'Total General')

        rows = list(ws.iter_rows(min_row=2, values_only=True))
        total_row = None
        for row in rows:
            if row[0] == 'TOTAL':
                total_row = row
                break
        self.assertIsNotNone(total_row)

        gas_idx = headers.index('Gas')
        total_idx = len(headers) - 1
        sum_gas = sum(int(r[gas_idx] or 0) for r in rows if r[0] != 'TOTAL')
        sum_total = sum(int(r[total_idx] or 0) for r in rows if r[0] != 'TOTAL')
        self.assertEqual(int(total_row[gas_idx] or 0), sum_gas)
        self.assertEqual(int(total_row[total_idx] or 0), sum_total)
