from django.conf import settings
from django.db import models
from datetime import datetime, timedelta


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Empresa(BaseModel):
    """Tenant — empresa que contrata el CRM"""

    TIPO_PLATAFORMA = 'PLATAFORMA'
    TIPO_CLIENTE = 'CLIENTE'
    TIPO_CHOICES = [
        (TIPO_PLATAFORMA, 'Plataforma (dueño del sistema)'),
        (TIPO_CLIENTE, 'Cliente (empresa contratante)'),
    ]

    nombre = models.CharField(max_length=255, verbose_name='Nombre Empresa')
    rut = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name='RUT')
    dominio = models.CharField(max_length=100, unique=True, blank=True, null=True,
                               help_text='Ej: claro.cl — se usa para asignar usuarios automáticamente',
                               verbose_name='Dominio email')
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default=TIPO_CLIENTE,
        verbose_name='Tipo de empresa',
        help_text='PLATAFORMA = dueño del sistema. Solo puede haber una.',
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')
    logo = models.ImageField(upload_to='empresas/logos/', blank=True, null=True, verbose_name='Logo')

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class CampoPersonalizado(BaseModel):
    """
    Define campos extra configurables por empresa para entidades clave.
    Los valores se almacenan en datos_extra (JSONField) de cada entidad.
    Estrategia A: Claro Chile conserva columnas reales; otras empresas usan este mecanismo.
    """
    TIPO_TEXTO    = 'TEXT'
    TIPO_NUMERO   = 'NUMBER'
    TIPO_FECHA    = 'DATE'
    TIPO_LISTA    = 'SELECT'
    TIPO_BOOLEANO = 'BOOL'

    TIPOS = [
        (TIPO_TEXTO,    'Texto'),
        (TIPO_NUMERO,   'Número'),
        (TIPO_FECHA,    'Fecha'),
        (TIPO_LISTA,    'Lista desplegable'),
        (TIPO_BOOLEANO, 'Booleano (Sí/No)'),
    ]

    ENTIDAD_CLIENTE     = 'CLIENTE'
    ENTIDAD_OPORTUNIDAD = 'OPORTUNIDAD'
    ENTIDAD_SEGUIMIENTO = 'SEGUIMIENTO'

    ENTIDADES = [
        (ENTIDAD_CLIENTE,     'Cliente'),
        (ENTIDAD_OPORTUNIDAD, 'Oportunidad'),
        (ENTIDAD_SEGUIMIENTO, 'Seguimiento'),
    ]

    empresa     = models.ForeignKey(
        'Empresa',
        on_delete=models.CASCADE,
        related_name='campos_personalizados',
        verbose_name='Empresa',
    )
    entidad     = models.CharField(
        max_length=20, choices=ENTIDADES,
        verbose_name='Entidad',
        help_text='Modelo al que pertenece este campo',
    )
    nombre      = models.CharField(
        max_length=100,
        verbose_name='Nombre visible',
        help_text='Ej: "Número de Licencias"',
    )
    clave       = models.SlugField(
        max_length=100,
        verbose_name='Clave interna',
        help_text='Identificador único en JSON. Solo letras, números y guiones bajos. Ej: num_licencias',
    )
    tipo        = models.CharField(
        max_length=10, choices=TIPOS, default=TIPO_TEXTO,
        verbose_name='Tipo de campo',
    )
    opciones    = models.JSONField(
        blank=True, null=True,
        verbose_name='Opciones',
        help_text='Solo para tipo Lista. Formato: ["Opción A", "Opción B"]',
    )
    obligatorio = models.BooleanField(
        default=False,
        verbose_name='Obligatorio',
    )
    orden       = models.PositiveIntegerField(
        default=0,
        verbose_name='Orden de aparición',
    )
    activo      = models.BooleanField(
        default=True,
        verbose_name='Activo',
    )

    class Meta:
        verbose_name = 'Campo Personalizado'
        verbose_name_plural = 'Campos Personalizados'
        ordering = ['empresa', 'entidad', 'orden', 'nombre']
        unique_together = [('empresa', 'entidad', 'clave')]

    def __str__(self):
        return f"{self.empresa.nombre} | {self.get_entidad_display()} | {self.nombre}"


class Cliente(BaseModel):
    """Empresa cliente - tabla maestra"""
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('DORMIDO', 'Dormido'),
        ('PROSPECT', 'Prospect'),
    ]
    
    SEGMENTO_CHOICES = [
        ('GRANDE', 'Grande'),
        ('CORP', 'Corporativo'),
        ('MED', 'Mediano'),
        ('PYM', 'PyME'),
        ('OTRO', 'Otro'),
    ]
    
    ORIGEN_CHOICES = [
        ('IMPORTADO', 'Importado (cartera)'),
        ('MANUAL', 'Prospectado por vendedor'),
    ]

    # Campos básicos
    # rut es único GLOBAL (no por empresa) por decisión deliberada: cambiarlo a
    # unique_together(empresa, rut) requiere rediseñar ClienteResource, las vistas
    # de importación de cartera y los scripts legacy con ON CONFLICT (rut). Diferido
    # hasta que exista una empresa real con clientes propios o se rediseñen los
    # importadores (deuda técnica conocida).
    rut = models.CharField(max_length=20, unique=True, verbose_name='RUT')
    dv = models.CharField(max_length=1, blank=True, null=True, verbose_name='DV')
    nombre_empresa = models.CharField(max_length=255, verbose_name='Nombre Empresa')
    sector = models.CharField(max_length=100, blank=True, null=True, verbose_name='Sector')
    tipo_cliente = models.CharField(max_length=50, blank=True, null=True, verbose_name='Tipo Cliente')
    usuario_asignado = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='clientes',
        verbose_name='Ejecutivo Asignado'
    )
    fecha_registro = models.DateField(blank=True, null=True, verbose_name='Fecha Registro')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PROSPECT', verbose_name='Estado')
    comuna = models.CharField(max_length=100, blank=True, null=True, verbose_name='Comuna')
    provincia = models.CharField(max_length=100, blank=True, null=True, verbose_name='Provincia')
    region = models.CharField(max_length=100, blank=True, null=True, verbose_name='Región')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    origen = models.CharField(
        max_length=20, choices=ORIGEN_CHOICES, default='IMPORTADO', verbose_name='Origen'
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='clientes_creados',
        verbose_name='Creado Por'
    )
    empresa = models.ForeignKey(
        'Empresa',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='clientes',
        verbose_name='Empresa (tenant)'
    )

    # Campos de segmentación Claro
    segmento = models.CharField(max_length=50, blank=True, null=True, choices=SEGMENTO_CHOICES, verbose_name='Segmento')
    subrango = models.CharField(max_length=50, blank=True, null=True, verbose_name='Subrango')
    supervisor = models.CharField(max_length=100, blank=True, null=True, verbose_name='Supervisor')
    subgerencia = models.CharField(max_length=100, blank=True, null=True, verbose_name='Subgerencia')
    
    # Campos de servicios Claro
    renta_uf_total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name='Renta UF Total')
    q_total_lineas = models.IntegerField(blank=True, null=True, default=0, verbose_name='Total Planes Multimedia')
    bam = models.IntegerField(blank=True, null=True, default=0, verbose_name='BAM')
    m2m = models.IntegerField(blank=True, null=True, default=0, verbose_name='M2M')
    voz = models.IntegerField(blank=True, null=True, default=0, verbose_name='GPS')
    fijo = models.CharField(max_length=10, blank=True, null=True, verbose_name='¿Fijo?')
    movil = models.CharField(max_length=10, blank=True, null=True, verbose_name='¿Móvil?')
    fijo_movil = models.CharField(max_length=50, blank=True, null=True, verbose_name='Fijo+Móvil')
    edv = models.CharField(max_length=150, blank=True, null=True, verbose_name='Ejecutivo de Ventas (EDV)')

    # Campos personalizados por empresa (Fase 1: estructura, sin uso en Claro Chile)
    datos_extra = models.JSONField(
        blank=True, null=True, default=dict,
        verbose_name='Datos adicionales',
        help_text='Almacena valores de campos personalizados definidos por la empresa (CampoPersonalizado)',
    )

    class Meta:
        ordering = ['nombre_empresa']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['usuario_asignado']),
        ]
    
    def __str__(self):
        return f"{self.rut} - {self.nombre_empresa}"
    
    @property
    def oportunidades_activas(self):
        return self.oportunidades.filter(estado='ABIERTA').count()
    
    @property
    def valor_cartera(self):
        from django.db.models import Sum
        return self.oportunidades.filter(estado='ABIERTA').aggregate(
            total=Sum('monto')
        )['total'] or 0


class Contacto(BaseModel):
    """Personas de contacto en clientes"""
    ROL_CHOICES = [
        ('DECISOR', 'Decidor'),
        ('INFLUENCIADOR', 'Influenciador'),
        ('USUARIO', 'Usuario'),
        ('OTRO', 'Otro'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='contactos', verbose_name='Cliente')
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    cargo = models.CharField(max_length=150, blank=True, null=True, verbose_name='Cargo')
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='OTRO', verbose_name='Rol')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    telefono_movil = models.CharField(max_length=20, blank=True, null=True, verbose_name='Teléfono Móvil')
    telefono_fijo = models.CharField(max_length=20, blank=True, null=True, verbose_name='Teléfono Fijo')
    orden = models.PositiveIntegerField(default=1, verbose_name='Orden')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    
    class Meta:
        ordering = ['cliente', 'orden', 'nombre']
        verbose_name = 'Contacto'
        verbose_name_plural = 'Contactos'
    
    def __str__(self):
        return f"{self.nombre} ({self.cliente.nombre_empresa})"


class Oportunidad(BaseModel):
    """Ventas potenciales - Pipeline"""
    ETAPA_CHOICES = [
        ('LEAD', 'Lead'),
        ('CONTACTO', 'Contacto Inicial'),
        ('CALIFICADO', 'Calificado'),
        ('PROPUESTA', 'Propuesta Presentada'),
        ('NEGOCIACION', 'Negociación'),
        ('CIERRE', 'Cierre Próximo'),
        ('GANADA', 'Venta Ganada'),
        ('PERDIDA', 'Venta Perdida'),
        ('DORMIDA', 'Dormida'),
    ]
    
    ESTADO_CHOICES = [
        ('ABIERTA', 'Abierta'),
        ('GANADA', 'Ganada'),
        ('PERDIDA', 'Perdida'),
    ]
    
    MONEDA_CHOICES = [
        ('CLP', 'CLP'),
        ('USD', 'USD'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='oportunidades', verbose_name='Cliente')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='oportunidades',
        verbose_name='Ejecutivo'
    )
    
    monto = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Monto')
    moneda = models.CharField(max_length=3, choices=MONEDA_CHOICES, default='CLP', verbose_name='Moneda')
    
    etapa = models.CharField(max_length=20, choices=ETAPA_CHOICES, default='LEAD', verbose_name='Etapa')
    probabilidad = models.PositiveIntegerField(default=0, verbose_name='Probabilidad (%)')
    productos = models.CharField(max_length=255, blank=True, null=True, verbose_name='Productos')
    lineas = models.PositiveIntegerField(default=0, verbose_name='Líneas')
    
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha Creación')
    fecha_cierre_estimada = models.DateField(blank=True, null=True, verbose_name='Fecha Cierre Estimada')
    fecha_cierre_real = models.DateField(blank=True, null=True, verbose_name='Fecha Cierre Real')
    fecha_ultimo_contacto = models.DateTimeField(blank=True, null=True, verbose_name='Último Contacto')
    proximo_contacto = models.DateField(blank=True, null=True, verbose_name='Próximo Contacto')
    
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    comision_estimada = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name='Comisión Estimada')
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='ABIERTA', verbose_name='Estado')
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='oportunidades_creadas',
        verbose_name='Creado Por'
    )

    # Campos personalizados por empresa
    datos_extra = models.JSONField(
        blank=True, null=True, default=dict,
        verbose_name='Datos adicionales',
        help_text='Almacena valores de campos personalizados definidos por la empresa (CampoPersonalizado)',
    )

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Oportunidad'
        verbose_name_plural = 'Oportunidades'
        indexes = [
            models.Index(fields=['etapa']),
            models.Index(fields=['usuario']),
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_cierre_estimada']),
        ]
    
    def __str__(self):
        return f"{self.cliente.nombre_empresa} — {self.get_etapa_display()}"
    
    @property
    def dias_sin_contacto(self):
        if self.fecha_ultimo_contacto:
            return (datetime.now().replace(tzinfo=None) - self.fecha_ultimo_contacto.replace(tzinfo=None)).days
        return None
    
    @property
    def estado_alerta(self):
        """Retorna el estado de alerta según días sin contacto"""
        dias = self.dias_sin_contacto
        if dias is None:
            return 'SIN_CONTACTO'
        if dias < 7:
            return 'AL_DIA'
        elif dias < 14:
            return 'ATENCION'
        elif dias < 30:
            return 'EN_RIESGO'
        elif dias < 45:
            return 'RIESGO_ALTO'
        else:
            return 'DORMIDA'


class Llamada(BaseModel):
    """Registro de contactos - Llamadas, emails, reuniones"""
    TIPO_CHOICES = [
        ('LLAMADA', 'Llamada'),
        ('EMAIL', 'Email'),
        ('REUNION', 'Reunión'),
        ('VIDEO', 'Videollamada'),
    ]
    
    RESULTADO_CHOICES = [
        ('EXITOSA', 'Exitosa'),
        ('FALLIDA', 'Fallida'),
        ('SIN_RESPUESTA', 'Sin Respuesta'),
        ('PENDIENTE', 'Pendiente'),
    ]
    
    oportunidad = models.ForeignKey(Oportunidad, on_delete=models.SET_NULL, null=True, blank=True, related_name='llamadas', verbose_name='Oportunidad')
    contacto = models.ForeignKey(Contacto, on_delete=models.SET_NULL, null=True, blank=True, related_name='llamadas', verbose_name='Contacto')
    
    fecha_hora = models.DateTimeField(verbose_name='Fecha y Hora')
    duracion_minutos = models.PositiveIntegerField(blank=True, null=True, verbose_name='Duración (min)')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='LLAMADA', verbose_name='Tipo')
    resultado = models.CharField(max_length=20, choices=RESULTADO_CHOICES, default='PENDIENTE', verbose_name='Resultado')
    
    nota_ejecutiva = models.TextField(blank=True, null=True, verbose_name='Notas')
    proximo_contacto_propuesto = models.DateField(blank=True, null=True, verbose_name='Próximo Contacto Propuesto')
    productos_discutidos = models.CharField(max_length=255, blank=True, null=True, verbose_name='Productos Discutidos')
    accion_pendiente = models.CharField(max_length=255, blank=True, null=True, verbose_name='Acción Pendiente')
    
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Creado Por')
    
    class Meta:
        ordering = ['-fecha_hora']
        verbose_name = 'Gestión'
        verbose_name_plural = 'Gestiones'
    
    def __str__(self):
        if self.oportunidad:
            return f"{self.oportunidad.cliente.nombre_empresa} - {self.fecha_hora}"
        elif self.contacto and self.contacto.cliente:
            return f"{self.contacto.cliente.nombre_empresa} - {self.fecha_hora}"
        return f"Gestión - {self.fecha_hora}"


class MetaVentas(BaseModel):
    """Metas mensuales de vendedores"""
    empresa = models.ForeignKey(
        'Empresa', on_delete=models.CASCADE, null=True, blank=True,
        related_name='metas_ventas', verbose_name='Empresa (tenant)'
    )
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='metas_ventas', verbose_name='Usuario')
    periodo = models.CharField(max_length=20, verbose_name='Período')  # 2026-04, 2026-05, etc.
    
    meta_lineas_portabilidad = models.PositiveIntegerField(default=0, verbose_name='Meta Líneas Portabilidad')
    meta_lineas_nueva = models.PositiveIntegerField(default=0, verbose_name='Meta Líneas Nueva')
    meta_lineas_m2m = models.PositiveIntegerField(default=0, verbose_name='Meta Líneas M2M')
    meta_monto_total = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Meta Monto Total')
    
    comision_base = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Comisión Base')
    comision_por_linea = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Comisión por Línea')
    factor_aceleracion = models.DecimalField(max_digits=3, decimal_places=2, default=1.0, verbose_name='Factor Aceleración')
    bonificacion_meta = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Bonificación Meta')
    
    class Meta:
        unique_together = [('empresa', 'usuario', 'periodo')]
        verbose_name = 'Meta de Ventas'
        verbose_name_plural = 'Metas de Ventas'
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.periodo}"


class Comision(BaseModel):
    """Comisiones calculadas"""
    ESTADO_CHOICES = [
        ('CALCULADA', 'Calculada'),
        ('APROBADA', 'Aprobada'),
        ('PAGADA', 'Pagada'),
    ]

    empresa = models.ForeignKey(
        'Empresa', on_delete=models.CASCADE, null=True, blank=True,
        related_name='comisiones', verbose_name='Empresa (tenant)'
    )
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comisiones', verbose_name='Usuario')
    meta = models.ForeignKey(MetaVentas, on_delete=models.SET_NULL, null=True, related_name='comisiones', verbose_name='Meta')
    periodo = models.CharField(max_length=20, verbose_name='Período')
    
    lineas_portabilidad_vendidas = models.PositiveIntegerField(default=0, verbose_name='Líneas Portabilidad Vendidas')
    lineas_nueva_vendidas = models.PositiveIntegerField(default=0, verbose_name='Líneas Nueva Vendidas')
    lineas_m2m_vendidas = models.PositiveIntegerField(default=0, verbose_name='Líneas M2M Vendidas')
    monto_total_vendido = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Monto Total Vendido')
    
    comision_calculada = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Comisión Calculada')
    bonificacion_aplicada = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Bonificación Aplicada')
    total_a_pagar = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Total a Pagar')
    
    fecha_calculo = models.DateTimeField(blank=True, null=True, verbose_name='Fecha Cálculo')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='CALCULADA', verbose_name='Estado')
    fecha_pago = models.DateField(blank=True, null=True, verbose_name='Fecha Pago')
    
    class Meta:
        unique_together = [('empresa', 'usuario', 'periodo')]
        verbose_name = 'Comisión'
        verbose_name_plural = 'Comisiones'
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.periodo} - ${self.total_a_pagar}"


class Seguimiento(BaseModel):
    """Alertas, recordatorios, tareas"""
    TIPO_CHOICES = [
        ('ALERTA', 'Alerta'),
        ('RECORDATORIO', 'Recordatorio'),
        ('TAREA', 'Tarea'),
        ('NOTA', 'Nota'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
        ('CRITICA', 'Crítica'),
    ]
    
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROGRESO', 'En Progreso'),
        ('COMPLETADA', 'Completada'),
    ]
    
    oportunidad = models.ForeignKey(Oportunidad, on_delete=models.CASCADE, related_name='seguimientos', verbose_name='Oportunidad')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='RECORDATORIO', verbose_name='Tipo')
    descripcion = models.TextField(verbose_name='Descripción')
    
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha Creación')
    fecha_vencimiento = models.DateField(blank=True, null=True, verbose_name='Fecha Vencimiento')
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='MEDIA', verbose_name='Prioridad')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE', verbose_name='Estado')
    
    asignado_a = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='seguimientos', verbose_name='Asignado A')
    completado_en = models.DateTimeField(blank=True, null=True, verbose_name='Completado En')
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='seguimientos_creados',
        verbose_name='Creado Por'
    )

    # Campos personalizados por empresa
    datos_extra = models.JSONField(
        blank=True, null=True, default=dict,
        verbose_name='Datos adicionales',
        help_text='Almacena valores de campos personalizados definidos por la empresa (CampoPersonalizado)',
    )

    class Meta:
        ordering = ['-fecha_vencimiento', '-prioridad']
        verbose_name = 'Seguimiento'
        verbose_name_plural = 'Seguimientos'
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_vencimiento']),
        ]
    
    def __str__(self):
        return f"{self.oportunidad.cliente.nombre_empresa} - {self.tipo}"


class UserProfile(BaseModel):
    """Perfil extendido de usuario para jerarquía de supervisores"""
    ROLE_CHOICES = [
        ('ADMIN', 'Administrador General'),
        ('MANAGER', 'Gerente de Ventas'),
        ('EJECUTIVO', 'Ejecutivo'),
        ('OTRO', 'Otro'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Usuario'
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='EJECUTIVO',
        verbose_name='Rol'
    )
    
    empresa = models.ForeignKey(
        'Empresa',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='usuarios',
        verbose_name='Empresa (tenant)'
    )

    # Supervisor: si es MANAGER, aquí irá el ADMIN supervisor. Si es EJECUTIVO, aquí irá el MANAGER supervisor
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinados',
        verbose_name='Supervisor'
    )
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuarios'
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_role_display()})"
    
    @property
    def es_admin(self):
        return self.role == 'ADMIN'
    
    @property
    def es_manager(self):
        return self.role == 'MANAGER'
    
    @property
    def es_ejecutivo(self):
        return self.role == 'EJECUTIVO'


class SocioSindicato(BaseModel):
    """Socios del módulo sindical (aislado del CRM comercial)."""

    ESTADO_LABORAL_ACTIVO = 'ACTIVO'
    ESTADO_LABORAL_LICENCIA = 'LICENCIA_MEDICA'
    ESTADO_LABORAL_DESVINCULADO = 'DESVINCULADO'
    ESTADO_LABORAL_SUSPENDIDO = 'SUSPENDIDO'
    ESTADO_LABORAL_CHOICES = [
        (ESTADO_LABORAL_ACTIVO, 'Activo'),
        (ESTADO_LABORAL_LICENCIA, 'Licencia médica'),
        (ESTADO_LABORAL_DESVINCULADO, 'Desvinculado'),
        (ESTADO_LABORAL_SUSPENDIDO, 'Suspendido'),
    ]

    ESTADO_ACTIVO = 'ACTIVO'
    ESTADO_INACTIVO = 'INACTIVO'
    ESTADO_CHOICES = [
        (ESTADO_ACTIVO, 'Activo'),
        (ESTADO_INACTIVO, 'Inactivo'),
    ]

    empresa = models.ForeignKey(
        'Empresa',
        on_delete=models.CASCADE,
        related_name='socios_sindicato',
        verbose_name='Empresa (tenant)',
    )
    rut = models.CharField(max_length=20, verbose_name='RUT')
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    site = models.CharField(max_length=100, blank=True, null=True, verbose_name='Site')
    estado_laboral = models.CharField(
        max_length=20,
        choices=ESTADO_LABORAL_CHOICES,
        default=ESTADO_LABORAL_ACTIVO,
        verbose_name='Estado laboral',
    )
    fecha_ingreso = models.DateField(blank=True, null=True, verbose_name='Fecha ingreso')
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_ACTIVO,
        verbose_name='Estado',
    )

    class Meta:
        verbose_name = 'Socio Sindicato'
        verbose_name_plural = 'Socios Sindicato'
        ordering = ['nombre']
        constraints = [
            models.UniqueConstraint(fields=['empresa', 'rut'], name='uniq_socio_sindicato_empresa_rut'),
        ]
        indexes = [
            models.Index(fields=['empresa', 'rut']),
            models.Index(fields=['empresa', 'estado']),
            models.Index(fields=['empresa', 'estado_laboral']),
        ]

    def __str__(self):
        return f"{self.rut} - {self.nombre}"


class TipoBeneficioSindicato(BaseModel):
    """Catálogo de beneficios del módulo sindical."""

    ESTADO_ACTIVO = 'ACTIVO'
    ESTADO_INACTIVO = 'INACTIVO'
    ESTADO_CHOICES = [
        (ESTADO_ACTIVO, 'Activo'),
        (ESTADO_INACTIVO, 'Inactivo'),
    ]

    empresa = models.ForeignKey(
        'Empresa',
        on_delete=models.CASCADE,
        related_name='tipos_beneficio_sindicato',
        verbose_name='Empresa (tenant)',
    )
    codigo = models.CharField(max_length=40, verbose_name='Código')
    nombre = models.CharField(max_length=120, verbose_name='Nombre')
    orden_export = models.PositiveSmallIntegerField(default=100, verbose_name='Orden exportación')
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_ACTIVO,
        verbose_name='Estado',
    )

    class Meta:
        verbose_name = 'Tipo Beneficio Sindicato'
        verbose_name_plural = 'Tipos Beneficio Sindicato'
        ordering = ['orden_export', 'nombre']
        constraints = [
            models.UniqueConstraint(fields=['empresa', 'codigo'], name='uniq_tipo_benef_sind_empresa_codigo'),
            models.UniqueConstraint(fields=['empresa', 'nombre'], name='uniq_tipo_benef_sind_empresa_nombre'),
        ]
        indexes = [
            models.Index(fields=['empresa', 'estado']),
            models.Index(fields=['empresa', 'orden_export']),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.empresa})"


class MovimientoSindicato(BaseModel):
    """Movimientos mensuales de descuentos sindicales por socio y beneficio."""

    ESTADO_PENDIENTE = 'PENDIENTE'
    ESTADO_VALIDADO = 'VALIDADO'
    ESTADO_OBSERVADO = 'OBSERVADO'
    ESTADO_RECHAZADO = 'RECHAZADO'
    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_VALIDADO, 'Validado'),
        (ESTADO_OBSERVADO, 'Observado'),
        (ESTADO_RECHAZADO, 'Rechazado'),
    ]

    FUENTE_GAS = 'GAS'
    FUENTE_TELEFONIA = 'TELEFONIA'
    FUENTE_COPEUCH = 'COPEUCH'
    FUENTE_CHOICES = [
        (FUENTE_GAS, 'Gas'),
        (FUENTE_TELEFONIA, 'Telefonia'),
        (FUENTE_COPEUCH, 'Copeuch'),
    ]

    empresa = models.ForeignKey(
        'Empresa',
        on_delete=models.CASCADE,
        related_name='movimientos_sindicato',
        verbose_name='Empresa (tenant)',
    )
    socio = models.ForeignKey(
        'SocioSindicato',
        on_delete=models.PROTECT,
        related_name='movimientos',
        verbose_name='Socio',
    )
    tipo_beneficio = models.ForeignKey(
        'TipoBeneficioSindicato',
        on_delete=models.PROTECT,
        related_name='movimientos',
        verbose_name='Tipo beneficio',
    )
    periodo = models.CharField(max_length=7, verbose_name='Periodo (YYYY-MM)')
    monto = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Monto')
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_PENDIENTE,
        verbose_name='Estado',
    )
    observacion = models.CharField(max_length=300, blank=True, null=True, verbose_name='Observación')
    referencia_externa = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Referencia externa',
    )
    fuente = models.CharField(
        max_length=20,
        choices=FUENTE_CHOICES,
        default=FUENTE_GAS,
        verbose_name='Fuente',
    )
    metadata_fuente = models.JSONField(
        blank=True,
        default=dict,
        verbose_name='Metadata fuente',
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimientos_sindicato_creados',
        verbose_name='Creado por',
    )

    class Meta:
        verbose_name = 'Movimiento Sindicato'
        verbose_name_plural = 'Movimientos Sindicato'
        ordering = ['-periodo', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['empresa', 'socio', 'tipo_beneficio', 'periodo', 'referencia_externa'],
                name='uniq_mov_sind_empresa_socio_benef_periodo_ref',
            ),
            models.CheckConstraint(check=models.Q(monto__gt=0), name='chk_mov_sind_monto_positivo'),
        ]
        indexes = [
            models.Index(fields=['empresa', 'periodo']),
            models.Index(fields=['empresa', 'estado']),
            models.Index(fields=['empresa', 'socio', 'periodo']),
        ]

    def __str__(self):
        return f"{self.periodo} | {self.socio} | {self.tipo_beneficio.nombre}"


class AuditoriaSindicato(BaseModel):
    """Bitácora de eventos del módulo sindical."""

    empresa = models.ForeignKey(
        'Empresa',
        on_delete=models.CASCADE,
        related_name='auditorias_sindicato',
        verbose_name='Empresa (tenant)',
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auditorias_sindicato',
        verbose_name='Usuario',
    )
    accion = models.CharField(max_length=40, verbose_name='Acción')
    entidad = models.CharField(max_length=60, verbose_name='Entidad')
    entidad_id = models.CharField(max_length=40, verbose_name='ID entidad')
    periodo = models.CharField(max_length=7, blank=True, null=True, verbose_name='Periodo')
    resumen = models.CharField(max_length=255, verbose_name='Resumen')
    payload = models.JSONField(default=dict, blank=True, verbose_name='Payload')
    ip_origen = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP origen')

    class Meta:
        verbose_name = 'Auditoría Sindicato'
        verbose_name_plural = 'Auditorías Sindicato'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['empresa', 'created_at']),
            models.Index(fields=['empresa', 'entidad', 'entidad_id']),
            models.Index(fields=['empresa', 'periodo']),
        ]

    def __str__(self):
        return f"{self.accion} | {self.entidad} | {self.created_at:%Y-%m-%d %H:%M}"


class ConsolidadoMensualSindicato(BaseModel):
    """Preparación conceptual para sprint siguiente: cabecera de consolidado mensual."""

    ESTADO_ABIERTO = 'ABIERTO'
    ESTADO_CERRADO = 'CERRADO'
    ESTADO_EXPORTADO = 'EXPORTADO'
    ESTADO_CHOICES = [
        (ESTADO_ABIERTO, 'Abierto'),
        (ESTADO_CERRADO, 'Cerrado'),
        (ESTADO_EXPORTADO, 'Exportado'),
    ]

    empresa = models.ForeignKey(
        'Empresa',
        on_delete=models.CASCADE,
        related_name='consolidados_sindicato',
        verbose_name='Empresa (tenant)',
    )
    periodo = models.CharField(max_length=7, verbose_name='Periodo (YYYY-MM)')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_ABIERTO, verbose_name='Estado')
    fecha_generacion = models.DateTimeField(blank=True, null=True, verbose_name='Fecha generación')
    total_socios = models.PositiveIntegerField(default=0, verbose_name='Total socios')
    total_monto = models.DecimalField(max_digits=14, decimal_places=0, default=0, verbose_name='Total monto')

    class Meta:
        verbose_name = 'Consolidado Mensual Sindicato'
        verbose_name_plural = 'Consolidados Mensuales Sindicato'
        constraints = [
            models.UniqueConstraint(fields=['empresa', 'periodo'], name='uniq_cons_mensual_sind_empresa_periodo'),
            models.CheckConstraint(check=models.Q(total_monto__gte=0), name='chk_cons_sind_total_monto_nonneg'),
        ]
        indexes = [
            models.Index(fields=['empresa', 'estado']),
            models.Index(fields=['empresa', 'periodo']),
        ]

    def __str__(self):
        return f"{self.empresa} | {self.periodo}"


class ConsolidadoDetalleSindicato(BaseModel):
    """Preparación conceptual para sprint siguiente: detalle socio x beneficio."""

    empresa = models.ForeignKey(
        'Empresa',
        on_delete=models.CASCADE,
        related_name='consolidado_detalles_sindicato',
        verbose_name='Empresa (tenant)',
    )
    consolidado = models.ForeignKey(
        'ConsolidadoMensualSindicato',
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Consolidado',
    )
    socio = models.ForeignKey('SocioSindicato', on_delete=models.PROTECT, related_name='consolidado_detalles')
    tipo_beneficio = models.ForeignKey(
        'TipoBeneficioSindicato', on_delete=models.PROTECT, related_name='consolidado_detalles'
    )
    monto_aprobado = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name='Monto aprobado')
    motivo_ajuste = models.CharField(max_length=300, blank=True, null=True, verbose_name='Motivo ajuste')

    class Meta:
        verbose_name = 'Consolidado Detalle Sindicato'
        verbose_name_plural = 'Consolidado Detalles Sindicato'
        constraints = [
            models.UniqueConstraint(
                fields=['consolidado', 'socio', 'tipo_beneficio'],
                name='uniq_cons_det_sind_consolidado_socio_benef',
            ),
            models.CheckConstraint(check=models.Q(monto_aprobado__gte=0), name='chk_cons_det_sind_monto_nonneg'),
        ]
        indexes = [
            models.Index(fields=['consolidado', 'socio']),
            models.Index(fields=['consolidado', 'tipo_beneficio']),
        ]

    def __str__(self):
        return f"{self.consolidado.periodo} | {self.socio} | {self.tipo_beneficio.nombre}"
