from django.conf import settings
from django.db import models
from datetime import datetime, timedelta


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


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
        unique_together = ['usuario', 'periodo']
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
        unique_together = ['usuario', 'periodo']
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
