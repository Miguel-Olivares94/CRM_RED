# Guía de Piloto — SindiApp

**Versión:** 1.0  
**Fecha:** Junio 2026  
**Plataforma:** Railway (PostgreSQL + gunicorn + WhiteNoise)  
**Branch:** `feature/modulo-sindicatos-mvp`

---

## 1. Pre-requisitos del piloto

Antes de entregar acceso al cliente, verificar que:

| Ítem | Responsable | Estado |
|---|---|---|
| Variables de entorno Railway configuradas | DevOps | Verificar |
| Deploy exitoso en Railway | DevOps | Verificar |
| Superusuario creado en Railway | DevOps | Verificar |
| Empresa del sindicato creada en Admin Django | Administrador | Verificar |
| Usuarios creados y asignados a empresa + grupo | Administrador | Verificar |
| Beneficios iniciales creados (Gas, Telefonía, etc.) | Administrador cliente | Verificar |
| Plantillas Excel del cliente disponibles para prueba | Cliente | Verificar |

---

## 2. Variables de entorno Railway requeridas

Configurar en el panel Railway → Variables:

```
SECRET_KEY=<clave-secreta-larga-y-aleatoria>
DATABASE_URL=<url-postgresql-railway>          # Se genera automáticamente
DEBUG=False                                    # CRÍTICO: False en producción
ALLOWED_HOSTS=tu-app.up.railway.app
RAILWAY_PUBLIC_DOMAIN=tu-app.up.railway.app

# Módulo Documentos/OCR:
# True  = visible en sidebar (OCR devuelve datos demo si pytesseract no instalado)
# False = módulo oculto (recomendado si no se incluye OCR en el piloto)
SINDIAPP_DOCUMENTOS_HABILITADO=False
```

**IMPORTANTE:** Con `DEBUG=False`, los archivos media se sirven mediante la vista
autenticada configurada en `config/urls.py`. Solo usuarios con sesión activa pueden
acceder a documentos subidos.

---

## 3. Primer deploy en Railway

El `railway.toml` ejecuta automáticamente al iniciar:

```bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py setup_empresa_inicial
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

**Acción adicional post-deploy (manual, una vez):**

```bash
# En Railway → Shell (o via railway run):
python manage.py configurar_sindiapp
```

Esto crea los grupos `Administracion`, `Tesoreria` y `Dirigente` y muestra el
procedimiento de alta de usuarios.

---

## 4. Alta de usuarios del sindicato

### Paso A — Ingresar al Admin Django

URL: `https://tu-app.up.railway.app/admin/`  
Credenciales: superusuario creado en Railway Shell:

```bash
python manage.py createsuperuser --email=admin@tudominio.cl
```

---

### Paso B — Crear empresa del sindicato (si no existe)

Admin → **Empresas** → Agregar empresa:

| Campo | Valor |
|---|---|
| Nombre | `Sindicato [Nombre]` |
| RUT | RUT del sindicato |
| Tipo | `Cliente` |
| Activo | ✓ |

---

### Paso C — Crear usuario

Admin → **Usuarios** → Agregar usuario:

| Campo | Valor |
|---|---|
| Username | correo del usuario (ej: `tesorera@sindicato.cl`) |
| Email | mismo correo |
| Password | contraseña segura temporaria |

Guardar. Luego en la edición del usuario:

| Campo | Valor |
|---|---|
| First name | nombre del usuario |
| Last name | apellido |
| Staff status | ☐ (NO marcar para usuarios del sindicato) |

---

### Paso D — Asignar empresa al usuario

Admin → **User profiles** → Agregar user profile:

| Campo | Valor |
|---|---|
| User | (seleccionar el usuario recién creado) |
| Empresa | (empresa del sindicato creada en Paso B) |
| Role | (dejar vacío — el rol lo da el Grupo) |

---

### Paso E — Asignar rol (Grupo)

Admin → **Usuarios** → (el usuario) → sección **Permisos** → campo **Grupos**:

| Grupo | Qué puede hacer |
|---|---|
| `Administracion` | Acceso completo: socios, beneficios, movimientos, consolidados, exportación, documentos, auditoría |
| `Tesoreria` | Importar, consolidar, exportar, gestionar documentos. Solo lectura de socios/beneficios |
| `Dirigente` | Solo lectura: socios, movimientos, consolidados, alertas |

Seleccionar el grupo apropiado → Guardar.

---

### Paso F — Verificar acceso

El usuario ingresa en: `https://tu-app.up.railway.app/sindiapp/login/`  
con su email y contraseña asignada.

Debe ver el dashboard de SindiApp con el menú correspondiente a su rol.

---

## 5. Configuración inicial del sindicato (hecha por el Administrador cliente)

### 5.1 Crear beneficios

SindiApp → **Beneficios** → Nuevo beneficio:

Para un sindicato típico con Gas, Telefonía y Copeuch:

| Código | Nombre | Orden Export |
|---|---|---|
| `GAS` | Gas | 1 |
| `TEL` | Telefonía | 2 |
| `COP` | Copeuch | 3 |

El **orden de exportación** determina el orden de columnas en el Excel consolidado.

### 5.2 Socios

Los socios se **crean automáticamente** la primera vez que se importa un archivo Excel con sus datos. También pueden agregarse manualmente desde SindiApp → Socios → Nuevo.

---

## 6. Flujo completo de trabajo mensual

```
1. IMPORTAR movimientos del mes
   SindiApp → Movimientos → Importar Excel
   • Subir archivo Gas, Telefonía o Copeuch
   • Revisar previsualización (errores aparecen en rojo)
   • Confirmar importación

2. REVISAR alertas
   SindiApp → Alertas
   • Verificar socios con licencia médica o baja activa
   • Resolver o ignorar las alertas del período

3. GENERAR consolidado mensual
   SindiApp → Consolidados → Generar consolidado
   • Seleccionar período (YYYY-MM)
   • El sistema totaliza por socio y beneficio

4. REVISAR consolidado
   SindiApp → Consolidados → (el período) → Ver detalle
   • Verificar montos y socios

5. CERRAR período
   SindiApp → Consolidados → (el período) → Cerrar período
   • Acción irreversible — confirmar antes de ejecutar
   • Bloquea nuevas importaciones para ese período

6. EXPORTAR Excel
   SindiApp → Consolidados → (el período) → Exportar Excel
   • Genera archivo con columnas: RUT, Nombre + una columna por beneficio
   • Listo para enviar a la empresa o al banco

7. AUDITORÍA
   SindiApp → Auditoría
   • Registro de todas las acciones del período
```

---

## 7. Flujo de validación con plantillas reales del cliente

### Gas
**Formato esperado del archivo:**

| Columna requerida | Alias aceptado |
|---|---|
| rut | rut |
| nombre | nombre, nombre_apellido |
| monto | monto, vale_de_gas |

**Columnas opcionales:** site, vale_de_gas

**Notas:**
- El sistema detecta automáticamente el tipo GAS al importar
- Los montos deben ser números (sin puntos de miles en el valor de celda)
- RUT chileno con o sin puntos y guión (se normaliza automáticamente)

---

### Telefonía
**Formato esperado del archivo:**

| Columna requerida | Alias aceptado |
|---|---|
| rut | rut |
| nombre | nombre, razon_social |
| monto | cargo_fijo |

**Columnas opcionales:** cuenta, pcs, fecha_entrega

---

### Copeuch
**Formato esperado del archivo:**

| Columna requerida | Alias aceptado |
|---|---|
| rut | rut |
| nombre | nombre |
| monto | tot_dctos, total_descuentos, total_dctos, tot_dcto, total_dcto |

**Notas importantes para Copeuch:**
- El archivo puede tener hasta 24 filas informativas antes de los headers reales
- El sistema las detecta automáticamente (escanea hasta fila 25)
- Los headers pueden tener acentos, puntos y espacios — se normalizan automáticamente
- Los montos pueden usar punto como separador de miles (ej: `1.234.567`) — se limpian

---

## 8. Procedimiento ante problemas comunes

### "No puedo hacer login en SindiApp"
1. Verificar que el usuario tenga Email correcto (el login es por email)
2. Verificar que tenga UserProfile con empresa asignada
3. Verificar que tenga al menos un grupo (Administracion/Tesoreria/Dirigente)
4. Si todo está correcto, resetear contraseña desde Admin → Usuarios

### "El Excel no se importa correctamente"
1. Verificar que las columnas requeridas existan en el archivo
2. Revisar el mensaje de error en la previsualización (columna "Error" en rojo)
3. Los RUT inválidos se muestran con error — verificar el dígito verificador
4. Si el tipo no se detecta, el sistema usa modo Genérico (requiere columnas: rut, nombre, monto)

### "El archivo exportado está vacío"
1. Verificar que existan movimientos para el período
2. Verificar que el período esté CERRADO (no ABIERTO)
3. Verificar que los socios tengan beneficios asociados

### "No veo el módulo de Documentos"
La variable `SINDIAPP_DOCUMENTOS_HABILITADO=False` en Railway oculta el módulo.  
Para habilitarlo: cambiar a `True` y redeploy.

### "El sitio cayó en Railway"
1. Ir a Railway → proyecto → logs → revisar errores
2. Si es un error de migraciones: `python manage.py migrate --noinput` en Railway Shell
3. Si es un error de memoria: escalar el plan de Railway
4. Railway tiene política `ON_FAILURE` con 3 reintentos automáticos configurados

---

## 9. Respaldo de datos

**Base de datos:** Railway PostgreSQL hace snapshots automáticos según el plan contratado.

**Respaldo manual (recomendado antes de cada cierre de período):**

```bash
# Desde Railway Shell o localmente con la DATABASE_URL:
python manage.py dumpdata core.SocioSindicato core.TipoBeneficioSindicato \
    core.MovimientoSindicato core.ConsolidadoMensualSindicato \
    core.ConsolidadoDetalleSindicato \
    --output=backup_sindicato_$(date +%Y%m%d).json

# Guardar el archivo en almacenamiento externo (Drive, S3, etc.)
```

**Archivos media (documentos subidos):**  
Los archivos en `MEDIA_ROOT` no están respaldados automáticamente.  
Para el piloto: hacer backup manual de la carpeta `media/` periódicamente.  
A largo plazo: migrar a almacenamiento externo (Cloudinary, S3, Railway Volumes).

---

## 10. SLA básico para cliente piloto

| Aspecto | Compromiso piloto |
|---|---|
| **Disponibilidad** | Best-effort (plataforma Railway) |
| **Tiempo de respuesta ante incidentes críticos** | 4 horas hábiles |
| **Tiempo de respuesta ante incidentes menores** | 48 horas hábiles |
| **Ventana de mantenimiento** | Viernes 22:00 – Sábado 06:00 |
| **Retención de datos** | Mínimo 12 meses en Railway PostgreSQL |
| **Respaldo** | Manual pre-cierre de período + automático Railway |
| **Soporte** | Correo a [soporte@dominio.cl] durante horario hábil |

**Incidente crítico:** sistema no disponible, pérdida de datos, imposibilidad de importar o exportar.  
**Incidente menor:** error en UI, lentitud, funcionalidad no crítica.

---

## 11. Checklist pre-entrega al cliente

```
□ Deploy Railway exitoso (manage.py check sin errores)
□ DEBUG=False en Railway
□ Superusuario creado
□ python manage.py configurar_sindiapp ejecutado (3 grupos creados)
□ Empresa del sindicato creada
□ Usuario Administracion creado y puede hacer login
□ Usuario Tesoreria creado y puede hacer login
□ Usuario Dirigente creado (opcional, según estructura)
□ Beneficios iniciales creados (Gas, Telefonía, Copeuch)
□ Importación de prueba con plantilla Gas realizada exitosamente
□ Importación de prueba con plantilla Telefonía realizada exitosamente
□ Importación de prueba con plantilla Copeuch realizada exitosamente
□ Consolidado generado y exportado para el período de prueba
□ Auditoría muestra acciones del período de prueba
□ Manual de usuario entregado al cliente
□ Contacto de soporte comunicado al cliente
```
