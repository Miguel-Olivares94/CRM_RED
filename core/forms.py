from .models import Cliente, Contacto, Oportunidad, Llamada, MetaVentas, Comision, Seguimiento, CampoPersonalizado
from .chile_data import REGIONES_CHOICES, SECTORES_CHOICES, TIPO_CLIENTE_CHOICES, SI_NO_CHOICES, PRODUCTOS_CLARO_CHOICES
from django import forms
from django.contrib.auth import get_user_model


def _campo_personalizado_to_form_field(campo):
    """Convierte un CampoPersonalizado en el campo de formulario Django correspondiente."""
    attrs = {'class': 'form-control'}
    required = campo.obligatorio

    if campo.tipo == CampoPersonalizado.TIPO_TEXTO:
        return forms.CharField(
            label=campo.nombre, required=required,
            widget=forms.TextInput(attrs=attrs),
        )
    if campo.tipo == CampoPersonalizado.TIPO_NUMERO:
        return forms.DecimalField(
            label=campo.nombre, required=required,
            widget=forms.NumberInput(attrs={**attrs, 'step': 'any'}),
        )
    if campo.tipo == CampoPersonalizado.TIPO_FECHA:
        return forms.DateField(
            label=campo.nombre, required=required,
            widget=forms.DateInput(attrs={**attrs, 'type': 'date'}),
        )
    if campo.tipo == CampoPersonalizado.TIPO_LISTA:
        opciones = campo.opciones or []
        choices = [('', '-- Selecciona --')] + [(o, o) for o in opciones]
        return forms.ChoiceField(
            label=campo.nombre, required=required,
            choices=choices,
            widget=forms.Select(attrs=attrs),
        )
    if campo.tipo == CampoPersonalizado.TIPO_BOOLEANO:
        return forms.BooleanField(
            label=campo.nombre, required=False,
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        )
    # fallback
    return forms.CharField(label=campo.nombre, required=required,
                           widget=forms.TextInput(attrs=attrs))

User = get_user_model()


class DateInput(forms.DateInput):
    input_type = "date"


class DateTimeInput(forms.DateTimeInput):
    input_type = "datetime-local"


# ==================== CLIENTE ====================
class ClienteForm(forms.ModelForm):
    def __init__(self, *args, user=None, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Guardar empresa para usarla en clean() y en el template
        self._empresa = empresa

        # Mostrar email en el select de ejecutivo asignado
        self.fields['usuario_asignado'].label_from_instance = lambda obj: obj.email or obj.username

        # ── Selects inteligentes ──────────────────────────────────────────────
        self.fields['region'] = forms.ChoiceField(
            choices=REGIONES_CHOICES, required=False, label='Región',
            widget=forms.Select(attrs={"class": "form-control", "id": "id_region"})
        )
        self.fields['comuna'] = forms.CharField(
            required=False, label='Comuna',
            widget=forms.Select(attrs={
                "class": "form-control", "id": "id_comuna",
                "data-current": self.instance.comuna if self.instance.pk else '',
                "data-no-select2": "true",
            })
        )
        self.fields['sector'] = forms.ChoiceField(
            choices=SECTORES_CHOICES, required=False, label='Sector',
            widget=forms.Select(attrs={"class": "form-control"})
        )
        self.fields['tipo_cliente'] = forms.ChoiceField(
            choices=TIPO_CLIENTE_CHOICES, required=False, label='Tipo Cliente',
            widget=forms.Select(attrs={"class": "form-control"})
        )
        self.fields['fijo'] = forms.ChoiceField(
            choices=SI_NO_CHOICES, required=False, label='¿Tiene Fijo?',
            widget=forms.Select(attrs={"class": "form-control"})
        )
        self.fields['movil'] = forms.ChoiceField(
            choices=SI_NO_CHOICES, required=False, label='¿Tiene Móvil?',
            widget=forms.Select(attrs={"class": "form-control"})
        )

        # Preseleccionar valores actuales si es edición
        if self.instance.pk:
            self.initial.setdefault('region', self.instance.region)
            self.initial.setdefault('sector', self.instance.sector)
            self.initial.setdefault('tipo_cliente', self.instance.tipo_cliente)
            self.initial.setdefault('fijo', self.instance.fijo)
            self.initial.setdefault('movil', self.instance.movil)

        # ── Supervisor: select dinámico con Managers del sistema ─────────────
        def nombre_usuario(u):
            return u.get_full_name().strip() or u.username

        supervisores = User.objects.filter(
            groups__name__in=['Manager', 'Admin']
        ).order_by('last_name', 'first_name')
        self.fields['supervisor'] = forms.ChoiceField(
            choices=[('', '-- Selecciona supervisor --')] + [
                (nombre_usuario(u), nombre_usuario(u)) for u in supervisores
            ],
            required=False, label='Supervisor',
            widget=forms.Select(attrs={"class": "form-control"})
        )
        if self.instance.pk:
            self.initial.setdefault('supervisor', self.instance.supervisor)

        # ── EDV: select dinámico con Ejecutivos del sistema ───────────────────
        ejecutivos = User.objects.filter(
            groups__name='Ejecutivo'
        ).order_by('last_name', 'first_name')
        self.fields['edv'] = forms.ChoiceField(
            choices=[('', '-- Selecciona ejecutivo --')] + [
                (nombre_usuario(u), nombre_usuario(u)) for u in ejecutivos
            ],
            required=False, label='Ejecutivo de Ventas',
            widget=forms.Select(attrs={"class": "form-control"})
        )
        if self.instance.pk:
            self.initial.setdefault('edv', self.instance.edv)

        # ── Filtro por rol de usuario ─────────────────────────────────────────
        if user:
            try:
                profile = user.profile
                es_manager = profile.es_manager
                es_ejecutivo = profile.es_ejecutivo
            except Exception:
                es_manager = user.groups.filter(name='Manager').exists()
                es_ejecutivo = user.groups.filter(name='Ejecutivo').exists()

            if es_manager:
                subordinados_ids = list(user.subordinados.values_list('user_id', flat=True))
                subordinados_ids.append(user.id)
                self.fields['usuario_asignado'].queryset = User.objects.filter(id__in=subordinados_ids)
                # Manager → supervisor = sí mismo (bloqueado)
                n = nombre_usuario(user)
                self.fields['supervisor'] = forms.ChoiceField(
                    choices=[(n, n)],
                    required=False, label='Supervisor',
                    widget=forms.Select(attrs={"class": "form-control"})
                )
                self.initial['supervisor'] = n

            elif es_ejecutivo:
                self.fields['usuario_asignado'].queryset = User.objects.filter(id=user.id)
                self.initial['usuario_asignado'] = user.id
                # Ejecutivo → supervisor = su manager (bloqueado)
                try:
                    mgr = user.profile.supervisor
                    n_sup = nombre_usuario(mgr) if mgr else ''
                except Exception:
                    n_sup = ''
                self.fields['supervisor'] = forms.ChoiceField(
                    choices=[(n_sup, n_sup)] if n_sup else [('', '-- Sin supervisor asignado --')],
                    required=False, label='Supervisor',
                    widget=forms.Select(attrs={"class": "form-control"})
                )
                self.initial['supervisor'] = n_sup
                # Ejecutivo → EDV = sí mismo (bloqueado)
                n_edv = nombre_usuario(user)
                self.fields['edv'] = forms.ChoiceField(
                    choices=[(n_edv, n_edv)],
                    required=False, label='Ejecutivo de Ventas',
                    widget=forms.Select(attrs={"class": "form-control"})
                )
                self.initial['edv'] = n_edv

        # ── Campos personalizados por empresa ─────────────────────────────────
        # Se inyectan al final del formulario con prefijo 'extra__<clave>'
        # Solo si la empresa fue pasada explícitamente desde la vista.
        if self._empresa:
            campos = CampoPersonalizado.objects.filter(
                empresa=self._empresa,
                entidad=CampoPersonalizado.ENTIDAD_CLIENTE,
                activo=True,
            ).order_by('orden', 'nombre')
            for campo in campos:
                field_name = f'extra__{campo.clave}'
                form_field = _campo_personalizado_to_form_field(campo)
                # En edición, recuperar el valor guardado de datos_extra
                if self.instance.pk and self.instance.datos_extra:
                    valor = self.instance.datos_extra.get(campo.clave)
                    if valor is not None:
                        form_field.initial = valor
                self.fields[field_name] = form_field

    def campos_extra_iter(self):
        """Iterador para el template: devuelve (campo_form, nombre_visible) de los campos extra."""
        for name, field in self.fields.items():
            if name.startswith('extra__'):
                yield self[name]

    class Meta:
        model = Cliente
        fields = [
            "rut", "nombre_empresa", "sector", "tipo_cliente", 
            "usuario_asignado", "estado", "region",
            "provincia", "observaciones",
            "dv", "segmento", "subrango", "supervisor", "subgerencia",
            "q_total_lineas", "bam", "m2m", "voz", "fijo", "movil", "fijo_movil", "edv"
        ]
        widgets = {
            "rut": forms.TextInput(attrs={
                "class": "form-control", "placeholder": "Ej: 12.345.678-9",
                "autocomplete": "off",
            }),
            "dv": forms.TextInput(attrs={"class": "form-control", "placeholder": "Auto", "readonly": "readonly", "style": "background:#f0f0f0"}),
            "nombre_empresa": forms.TextInput(attrs={"class": "form-control", "placeholder": "Razón social completa"}),
            "usuario_asignado": forms.Select(attrs={"class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-control"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Información adicional relevante"}),
            "segmento": forms.Select(attrs={"class": "form-control"}),
            "subrango": forms.TextInput(attrs={"class": "form-control", "placeholder": "Subrango"}),
            "subgerencia": forms.TextInput(attrs={"class": "form-control", "placeholder": "Subgerencia"}),
            "q_total_lineas": forms.NumberInput(attrs={"class": "form-control", "placeholder": "0"}),
            "bam": forms.NumberInput(attrs={"class": "form-control", "placeholder": "0"}),
            "m2m": forms.NumberInput(attrs={"class": "form-control", "placeholder": "0"}),
            "voz": forms.NumberInput(attrs={"class": "form-control", "placeholder": "0"}),
            "fijo_movil": forms.TextInput(attrs={"class": "form-control", "placeholder": "Descripción fijo+móvil"}),
            "provincia": forms.TextInput(attrs={"class": "form-control", "placeholder": "Se completa automáticamente"}),
        }



# ==================== CONTACTO ====================
class ContactoForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtra clientes según el rol del usuario
        if user:
            try:
                profile = user.profile
                if profile.es_manager:
                    # Manager ve sus subordinados' clientes + sus propios clientes
                    subordinados_ids = list(user.subordinados.values_list('user_id', flat=True))
                    subordinados_ids.append(user.id)
                    self.fields['cliente'].queryset = Cliente.objects.filter(usuario_asignado_id__in=subordinados_ids)
                elif profile.es_ejecutivo:
                    # Ejecutivo solo ve sus clientes asignados
                    self.fields['cliente'].queryset = Cliente.objects.filter(usuario_asignado=user)
                # Admin ve todos (queryset por defecto)
            except:
                # Fallback para usuarios sin profile
                if user.groups.filter(name='Ejecutivo').exists():
                    self.fields['cliente'].queryset = Cliente.objects.filter(usuario_asignado=user)
    
    class Meta:
        model = Contacto
        fields = [
            "cliente", "nombre", "cargo", "rol", "email", 
            "telefono_movil", "telefono_fijo", "activo"
        ]
        widgets = {
            "cliente": forms.Select(attrs={"class": "form-control"}),
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre"}),
            "cargo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Cargo"}),
            "rol": forms.Select(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
            "telefono_movil": forms.TextInput(attrs={"class": "form-control", "placeholder": "9 XXXX XXXX", "maxlength": "11", "inputmode": "numeric"}),
            "telefono_fijo": forms.TextInput(attrs={"class": "form-control", "placeholder": "2 XXXX XXXX", "maxlength": "11", "inputmode": "numeric"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


# ==================== OPORTUNIDAD ====================
class OportunidadForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if user:
            # Si es manager, ve sus subordinados + a sí mismo
            try:
                profile = user.profile
                if profile.es_manager:
                    subordinados_ids = list(user.subordinados.values_list('user_id', flat=True))
                    subordinados_ids.append(user.id)
                    self.fields['cliente'].queryset = Cliente.objects.filter(usuario_asignado_id__in=subordinados_ids)
                    self.fields['usuario'].queryset = User.objects.filter(id__in=subordinados_ids)
                elif profile.es_ejecutivo:
                    # Ejecutivo solo ve sus clientes y se asigna a sí mismo
                    self.fields['cliente'].queryset = Cliente.objects.filter(usuario_asignado=user)
                    self.fields['usuario'].queryset = User.objects.filter(id=user.id)
                    self.initial['usuario'] = user.id
                # Admin ve todos (queryset por defecto)
            except:
                # Fallback para usuarios sin profile
                if user.groups.filter(name='Ejecutivo').exists():
                    self.fields['cliente'].queryset = Cliente.objects.filter(usuario_asignado=user)
                    self.fields['usuario'].queryset = User.objects.filter(id=user.id)
                    self.initial['usuario'] = user.id
        
    class Meta:
        model = Oportunidad
        fields = [
            "cliente", "usuario", "monto", "etapa", "probabilidad",
            "productos", "lineas", "fecha_cierre_estimada", "proximo_contacto",
            "observaciones", "comision_estimada", "estado"
        ]
        widgets = {
            "cliente": forms.Select(attrs={"class": "form-control"}),
            "usuario": forms.Select(attrs={"class": "form-control"}),
            "monto": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Monto"}),
            "etapa": forms.Select(attrs={"class": "form-control"}),
            "probabilidad": forms.NumberInput(attrs={"class": "form-control", "min": "0", "max": "100", "placeholder": "%"}),
            "productos": forms.Select(
                choices=[('', '-- Selecciona producto --')] + list(PRODUCTOS_CLARO_CHOICES),
                attrs={"class": "form-control"}
            ),
            "lineas": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Nº de líneas"}),
            "fecha_cierre_estimada": DateInput(),
            "proximo_contacto": DateInput(),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Observaciones"}),
            "comision_estimada": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Comisión estimada"}),
            "estado": forms.Select(attrs={"class": "form-control"}),
        }


# ==================== LLAMADA ====================
class LlamadaForm(forms.ModelForm):
    def __init__(self, *args, user=None, contacto_id=None, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.contacto_id:
            # Edición: fija el queryset al contacto actual
            self.fields['contacto'].queryset = Contacto.objects.filter(
                pk=self.instance.contacto_id
            ).select_related('cliente')
        elif contacto_id:
            # Creación desde ?contacto=ID: pre-seleccionar ese contacto
            try:
                self.fields['contacto'].queryset = Contacto.objects.filter(
                    pk=int(contacto_id)
                ).select_related('cliente')
                self.initial['contacto'] = int(contacto_id)
            except (ValueError, TypeError):
                self.fields['contacto'].queryset = Contacto.objects.none()
        elif user:
            # Creación sin contacto URL: cargar contactos según rol del usuario
            try:
                profile = user.profile
                if profile.es_manager:
                    subordinados_ids = list(user.subordinados.values_list('user_id', flat=True))
                    subordinados_ids.append(user.id)
                    qs = Contacto.objects.filter(
                        cliente__usuario_asignado_id__in=subordinados_ids
                    )
                else:
                    qs = Contacto.objects.filter(cliente__usuario_asignado=user)
            except Exception:
                qs = Contacto.objects.filter(cliente__usuario_asignado=user)
            self.fields['contacto'].queryset = qs.select_related('cliente').order_by(
                'cliente__nombre_empresa', 'nombre'
            )
        else:
            self.fields['contacto'].queryset = Contacto.objects.none()
        
    class Meta:
        model = Llamada
        fields = [
            "contacto", "fecha_hora", "duracion_minutos",
            "tipo", "resultado", "nota_ejecutiva", "proximo_contacto_propuesto",
            "productos_discutidos", "accion_pendiente"
        ]
        widgets = {
            "contacto": forms.Select(attrs={"class": "form-control"}),
            "fecha_hora": DateTimeInput(),
            "duracion_minutos": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Minutos"}),
            "tipo": forms.Select(attrs={"class": "form-control"}),
            "resultado": forms.Select(attrs={"class": "form-control"}),
            "nota_ejecutiva": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Notas"}),
            "proximo_contacto_propuesto": DateInput(),
            "productos_discutidos": forms.Select(
                choices=[('', '-- Selecciona producto --')] + list(PRODUCTOS_CLARO_CHOICES),
                attrs={"class": "form-control"}
            ),
            "accion_pendiente": forms.TextInput(attrs={"class": "form-control", "placeholder": "Acción pendiente"}),
        }


# ==================== META VENTAS ====================
class MetaVentasForm(forms.ModelForm):
    class Meta:
        model = MetaVentas
        fields = [
            "usuario", "periodo", "meta_lineas_portabilidad", "meta_lineas_nueva",
            "meta_lineas_m2m", "meta_monto_total", "comision_base",
            "comision_por_linea", "factor_aceleracion", "bonificacion_meta"
        ]
        widgets = {
            "usuario": forms.Select(attrs={"class": "form-control"}),
            "periodo": forms.TextInput(attrs={"class": "form-control", "placeholder": "2026-04"}),
            "meta_lineas_portabilidad": forms.NumberInput(attrs={"class": "form-control"}),
            "meta_lineas_nueva": forms.NumberInput(attrs={"class": "form-control"}),
            "meta_lineas_m2m": forms.NumberInput(attrs={"class": "form-control"}),
            "meta_monto_total": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "comision_base": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "comision_por_linea": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "factor_aceleracion": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "value": "1.0"}),
            "bonificacion_meta": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }


# ==================== COMISIÓN ====================
class ComisionForm(forms.ModelForm):
    class Meta:
        model = Comision
        fields = [
            "usuario", "meta", "periodo", "lineas_portabilidad_vendidas",
            "lineas_nueva_vendidas", "lineas_m2m_vendidas", "monto_total_vendido",
            "comision_calculada", "bonificacion_aplicada", "total_a_pagar",
            "estado", "fecha_pago"
        ]
        widgets = {
            "usuario": forms.Select(attrs={"class": "form-control"}),
            "meta": forms.Select(attrs={"class": "form-control"}),
            "periodo": forms.TextInput(attrs={"class": "form-control", "placeholder": "2026-04"}),
            "lineas_portabilidad_vendidas": forms.NumberInput(attrs={"class": "form-control"}),
            "lineas_nueva_vendidas": forms.NumberInput(attrs={"class": "form-control"}),
            "lineas_m2m_vendidas": forms.NumberInput(attrs={"class": "form-control"}),
            "monto_total_vendido": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "comision_calculada": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "bonificacion_aplicada": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "total_a_pagar": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "estado": forms.Select(attrs={"class": "form-control"}),
            "fecha_pago": DateInput(),
        }


# ==================== SEGUIMIENTO ====================
class SeguimientoForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user:
            try:
                profile = user.profile
                if profile.es_manager:
                    subordinados_ids = list(user.subordinados.values_list('user_id', flat=True))
                    subordinados_ids.append(user.id)
                    self.fields['asignado_a'].queryset = User.objects.filter(id__in=subordinados_ids)
                    self.fields['oportunidad'].queryset = Oportunidad.objects.filter(
                        cliente__usuario_asignado_id__in=subordinados_ids
                    ).select_related('cliente')
                elif profile.es_ejecutivo:
                    # Ejecutivo solo puede asignarse a sí mismo
                    self.fields['asignado_a'].queryset = User.objects.filter(id=user.id)
                    self.initial['asignado_a'] = user.id
                    self.fields['oportunidad'].queryset = Oportunidad.objects.filter(
                        cliente__usuario_asignado=user
                    ).select_related('cliente')
            except Exception:
                if user.groups.filter(name__in=['Ejecutivo', 'Vendedor']).exists():
                    self.fields['asignado_a'].queryset = User.objects.filter(id=user.id)
                    self.initial['asignado_a'] = user.id
                    self.fields['oportunidad'].queryset = Oportunidad.objects.filter(
                        cliente__usuario_asignado=user
                    ).select_related('cliente')

    class Meta:
        model = Seguimiento
        fields = [
            "oportunidad", "tipo", "descripcion", "fecha_vencimiento",
            "prioridad", "estado", "asignado_a"
        ]
        widgets = {
            "oportunidad": forms.Select(attrs={"class": "form-control"}),
            "tipo": forms.Select(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Descripción"}),
            "fecha_vencimiento": DateInput(),
            "prioridad": forms.Select(attrs={"class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-control"}),
            "asignado_a": forms.Select(attrs={"class": "form-control"}),
        }


# ==================== AUTENTICACIÓN ====================
class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Correo electrónico"})
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Contraseña"})
    )

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email and password:
            self.user_cache = None
            try:
                user = User.objects.get(email=email)
                if not user.check_password(password):
                    raise forms.ValidationError("Correo o contraseña incorrectos.")
                self.user_cache = user
            except User.DoesNotExist:
                raise forms.ValidationError("Correo o contraseña incorrectos.")
        return self.cleaned_data

    def get_user(self):
        return self.user_cache


# ==================== CREAR EJECUTIVO ====================
class CreateEjecutivoForm(forms.Form):
    """Formulario para managers crear nuevos ejecutivos"""
    
    username = forms.CharField(
        max_length=150,
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "ej: juan.perez"
        })
    )
    
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "ej: juan.perez@claro.cl"
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        label="Nombre",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Nombre"
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        label="Apellido",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Apellido"
        })
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya existe.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email
