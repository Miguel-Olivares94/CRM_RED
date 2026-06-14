# MVP Sindicato - Paquete de ejecucion

Fecha: 2026-06-12
Objetivo: construir una primera version funcional para un cliente fundador, enfocada en automatizar descuentos sindicales mensuales y generar consolidado automatico.

## 1) Historias de usuario del MVP

### 1.1 Modulo Socios

Historia US-SOC-01 (P0)
- Rol: Administracion
- Descripcion: Como usuario de administracion quiero crear y editar socios para mantener el padron actualizado.
- Criterios de aceptacion:
  1. Se puede crear socio con RUT, nombre, site, estado laboral, fecha ingreso y estado.
  2. No se permite crear dos socios activos con el mismo RUT dentro del mismo sindicato.
  3. Se puede editar estado laboral y estado del socio.
  4. Se registra auditoria en crear y editar.
- Dependencias: US-SEG-01 (roles basicos), modelo Sindicato.

Historia US-SOC-02 (P0)
- Rol: Administracion, Tesoreria
- Descripcion: Como usuario operativo quiero listar y buscar socios por RUT/nombre/estado para gestionar rapidamente.
- Criterios de aceptacion:
  1. Busqueda por RUT exacto y por nombre parcial.
  2. Filtro por estado laboral y estado.
  3. Solo visualiza socios de su sindicato.
- Dependencias: US-SOC-01.

### 1.2 Modulo Tipos de beneficio

Historia US-BEN-01 (P0)
- Rol: Administracion
- Descripcion: Como administracion quiero mantener el catalogo de tipos de beneficio para clasificar descuentos.
- Criterios de aceptacion:
  1. Se pueden crear tipos de beneficio con codigo unico y nombre.
  2. Se puede activar/desactivar un tipo.
  3. No se puede eliminar fisicamente si tiene movimientos asociados.
  4. Se auditan cambios.
- Dependencias: US-SEG-01.

Historia US-BEN-02 (P1)
- Rol: Administracion
- Descripcion: Como administracion quiero definir orden de visualizacion para exportar consolidado en formato esperado.
- Criterios de aceptacion:
  1. Cada tipo de beneficio tiene campo orden_export.
  2. El orden se refleja en la exportacion.
- Dependencias: US-BEN-01, US-EXP-01.

### 1.3 Modulo Movimientos

Historia US-MOV-01 (P0)
- Rol: Tesoreria, Administracion
- Descripcion: Como tesoreria quiero registrar movimientos por socio y beneficio para alimentar el consolidado.
- Criterios de aceptacion:
  1. Campos minimos: socio, tipo beneficio, periodo, monto, estado, observacion.
  2. No permite monto <= 0.
  3. No permite registrar movimiento si beneficio esta inactivo.
  4. No permite registrar en periodo cerrado.
  5. Registra auditoria.
- Dependencias: US-SOC-01, US-BEN-01, US-CON-01.

Historia US-MOV-02 (P0)
- Rol: Tesoreria
- Descripcion: Como tesoreria quiero detectar duplicados para evitar dobles descuentos.
- Criterios de aceptacion:
  1. Se detecta duplicado por (sindicato, socio, tipo beneficio, periodo, referencia opcional).
  2. El sistema bloquea guardado y muestra mensaje.
- Dependencias: US-MOV-01.

Historia US-MOV-03 (P1)
- Rol: Tesoreria
- Descripcion: Como tesoreria quiero importar movimientos en lote desde plantilla puente.
- Criterios de aceptacion:
  1. Carga archivo xlsx/csv con validaciones de estructura.
  2. Reporta filas aceptadas/rechazadas.
  3. No crea registros de otros sindicatos.
- Dependencias: US-MOV-01, US-VAL-01.

### 1.4 Modulo Validaciones

Historia US-VAL-01 (P0)
- Rol: Tesoreria
- Descripcion: Como tesoreria quiero ejecutar validaciones basicas para asegurar descuentos validos antes del consolidado.
- Criterios de aceptacion:
  1. Regla socio activo: solo socios estado=Activo.
  2. Regla licencia medica: movimiento queda observado segun politica.
  3. Regla desvinculado: se rechaza descuento.
  4. Regla RUT valido: no permite operar con RUT invalido.
  5. Regla beneficio inactivo y periodo cerrado.
  6. Resultado visible en bandeja de observaciones.
- Dependencias: US-SOC-01, US-MOV-01.

Historia US-VAL-02 (P1)
- Rol: Tesoreria, Dirigente
- Descripcion: Como tesoreria quiero aprobar/rechazar observaciones manuales para cerrar periodo.
- Criterios de aceptacion:
  1. Cada observacion tiene estado pendiente/aprobada/rechazada.
  2. Se guarda motivo y usuario que decide.
  3. Se auditan decisiones.
- Dependencias: US-VAL-01, US-CON-01.

### 1.5 Modulo Consolidado mensual

Historia US-CON-01 (P0)
- Rol: Tesoreria
- Descripcion: Como tesoreria quiero abrir y cerrar periodos para controlar cuando se permiten registros.
- Criterios de aceptacion:
  1. Estado periodo: abierto/cerrado/exportado.
  2. Solo un consolidado por sindicato y periodo.
  3. En periodo cerrado no se aceptan movimientos nuevos.
- Dependencias: modelo ConsolidadoMensual.

Historia US-CON-02 (P0)
- Rol: Tesoreria
- Descripcion: Como tesoreria quiero generar consolidado automatico para obtener total por socio y por beneficio.
- Criterios de aceptacion:
  1. Al generar, crea detalle por socio x beneficio.
  2. Calcula total por socio.
  3. Excluye/restringe segun validaciones.
  4. Permite regenerar mientras estado sea abierto.
- Dependencias: US-MOV-01, US-VAL-01, US-CON-01.

### 1.6 Modulo Exportacion Excel

Historia US-EXP-01 (P0)
- Rol: Tesoreria
- Descripcion: Como tesoreria quiero exportar consolidado a Excel con formato acordado para enviarlo a la empresa.
- Criterios de aceptacion:
  1. Columnas y orden fijo segun especificacion.
  2. Incluye fila total general de columna.
  3. Nombre de archivo incluye sindicato y periodo.
  4. Guarda trazabilidad de exportacion.
- Dependencias: US-CON-02, US-BEN-02.

### 1.7 Modulo Dashboard basico

Historia US-DAS-01 (P0)
- Rol: Dirigente, Tesoreria, Administracion
- Descripcion: Como usuario quiero ver un tablero basico con estado del periodo y montos clave.
- Criterios de aceptacion:
  1. Muestra total socios, total movimientos, total descontado del periodo.
  2. Muestra conteo de observaciones pendientes.
  3. Muestra ultimas exportaciones.
  4. Respeta permisos por rol y tenant.
- Dependencias: US-CON-02, US-EXP-01.

### 1.8 Modulo Auditoria

Historia US-AUD-01 (P0)
- Rol: Admin sindicato, Superadmin
- Descripcion: Como administrador quiero bitacora basica para trazabilidad operativa y soporte.
- Criterios de aceptacion:
  1. Registra eventos de CRUD criticos y generacion/exportacion consolidado.
  2. Campos: usuario, accion, entidad, id entidad, fecha, resumen.
  3. Filtro por fecha y entidad.
  4. No editable por usuarios funcionales.
- Dependencias: US-SEG-01.

### 1.9 Modulo Usuarios y roles

Historia US-SEG-01 (P0)
- Rol: Admin sindicato
- Descripcion: Como administrador quiero gestionar usuarios con roles para controlar acceso.
- Criterios de aceptacion:
  1. Roles minimos: Dirigente, Tesoreria, Administracion.
  2. Cada usuario pertenece a un sindicato.
  3. Restriccion por tenant en todas las vistas/API.
  4. Accion no autorizada retorna acceso denegado.
- Dependencias: modelo Sindicato, integracion auth.

Historia US-SEG-02 (P1)
- Rol: Superadmin SaaS
- Descripcion: Como superadmin quiero crear sindicatos y usuarios admin iniciales.
- Criterios de aceptacion:
  1. Alta de sindicato con codigo unico.
  2. Alta de usuario admin inicial por sindicato.
- Dependencias: US-SEG-01.

## 2) Diseno tecnico de tablas Django

Nota: Propuesta para Django + PostgreSQL.
Soft delete recomendado para maestros y entidades de negocio. No para tablas de detalle calculado historico (consolidado detalle) ni auditoria.

### 2.1 Modelo Sindicato (Tenant)
- Tabla: Sindicato
- Campos:
  1. id (BigAutoField, PK)
  2. codigo (CharField(30), unique=True, obligatorio)
  3. nombre (CharField(150), obligatorio)
  4. rut (CharField(12), obligatorio)
  5. dominio (CharField(255), null=True, blank=True)
  6. activo (BooleanField, default=True)
  7. created_at (DateTimeField, auto_now_add=True)
  8. updated_at (DateTimeField, auto_now=True)
  9. deleted_at (DateTimeField, null=True, blank=True) [soft delete]
- Indices:
  1. Index(codigo)
  2. Index(activo)
- Constraints:
  1. UniqueConstraint(codigo)
  2. Check rut formato basico (via validator)

### 2.2 Modelo Socio
- Tabla: Socio
- Campos:
  1. id (BigAutoField, PK)
  2. sindicato (ForeignKey Sindicato, on_delete=PROTECT, obligatorio)
  3. rut (CharField(12), obligatorio)
  4. nombre (CharField(150), obligatorio)
  5. site (CharField(100), obligatorio)
  6. estado_laboral (CharField choices: ACTIVO, LICENCIA_MEDICA, DESVINCULADO, SUSPENDIDO; obligatorio)
  7. fecha_ingreso (DateField, obligatorio)
  8. estado (CharField choices: ACTIVO, INACTIVO; default=ACTIVO)
  9. created_at (DateTimeField, auto_now_add=True)
  10. updated_at (DateTimeField, auto_now=True)
  11. deleted_at (DateTimeField, null=True, blank=True) [soft delete]
- Relaciones:
  1. N:1 con Sindicato
- Indices:
  1. Index(sindicato, rut)
  2. Index(sindicato, estado)
  3. Index(sindicato, estado_laboral)
  4. Index(nombre)
- Constraints:
  1. UniqueConstraint(fields=[sindicato, rut], condition=deleted_at IS NULL)
  2. Validator de RUT obligatorio

### 2.3 Modelo TipoBeneficio
- Tabla: TipoBeneficio
- Campos:
  1. id (BigAutoField, PK)
  2. sindicato (ForeignKey Sindicato, on_delete=PROTECT, obligatorio)
  3. codigo (SlugField/CharField(40), obligatorio)
  4. nombre (CharField(120), obligatorio)
  5. activo (BooleanField, default=True)
  6. orden_export (PositiveSmallIntegerField, default=100)
  7. created_at (DateTimeField, auto_now_add=True)
  8. updated_at (DateTimeField, auto_now=True)
  9. deleted_at (DateTimeField, null=True, blank=True) [soft delete]
- Relaciones:
  1. N:1 con Sindicato
- Indices:
  1. Index(sindicato, activo)
  2. Index(sindicato, orden_export)
- Constraints:
  1. UniqueConstraint(fields=[sindicato, codigo], condition=deleted_at IS NULL)
  2. UniqueConstraint(fields=[sindicato, nombre], condition=deleted_at IS NULL)

### 2.4 Modelo ConsolidadoMensual
- Tabla: ConsolidadoMensual
- Campos:
  1. id (BigAutoField, PK)
  2. sindicato (ForeignKey Sindicato, on_delete=PROTECT, obligatorio)
  3. periodo (CharField(7), formato YYYY-MM, obligatorio)
  4. estado (CharField choices: ABIERTO, CERRADO, EXPORTADO; default=ABIERTO)
  5. fecha_generacion (DateTimeField, null=True, blank=True)
  6. total_socios (PositiveIntegerField, default=0)
  7. total_monto (DecimalField(14,2), default=0)
  8. creado_por (ForeignKey User, on_delete=SET_NULL, null=True)
  9. created_at (DateTimeField, auto_now_add=True)
  10. updated_at (DateTimeField, auto_now=True)
- Indices:
  1. Index(sindicato, periodo)
  2. Index(sindicato, estado)
- Constraints:
  1. UniqueConstraint(fields=[sindicato, periodo])
  2. Check total_monto >= 0

### 2.5 Modelo Movimiento
- Tabla: Movimiento
- Campos:
  1. id (BigAutoField, PK)
  2. sindicato (ForeignKey Sindicato, on_delete=PROTECT, obligatorio)
  3. socio (ForeignKey Socio, on_delete=PROTECT, obligatorio)
  4. tipo_beneficio (ForeignKey TipoBeneficio, on_delete=PROTECT, obligatorio)
  5. consolidado (ForeignKey ConsolidadoMensual, on_delete=PROTECT, obligatorio)
  6. periodo (CharField(7), obligatorio, redundante para consultas rapidas)
  7. monto (DecimalField(12,2), obligatorio)
  8. estado (CharField choices: PENDIENTE, VALIDADO, RECHAZADO, OBSERVADO; default=PENDIENTE)
  9. observacion (CharField(300), null=True, blank=True)
  10. referencia_externa (CharField(80), null=True, blank=True)
  11. created_at (DateTimeField, auto_now_add=True)
  12. updated_at (DateTimeField, auto_now=True)
  13. deleted_at (DateTimeField, null=True, blank=True) [soft delete]
- Relaciones:
  1. N:1 con Sindicato
  2. N:1 con Socio
  3. N:1 con TipoBeneficio
  4. N:1 con ConsolidadoMensual
- Indices:
  1. Index(sindicato, periodo)
  2. Index(sindicato, socio, periodo)
  3. Index(sindicato, tipo_beneficio, periodo)
  4. Index(estado)
- Constraints:
  1. Check monto > 0
  2. UniqueConstraint(fields=[sindicato, socio, tipo_beneficio, periodo, referencia_externa], condition=deleted_at IS NULL)
  3. Constraint de integridad aplicativo: movimiento.sindicato == socio.sindicato == tipo_beneficio.sindicato

### 2.6 Modelo ConsolidadoDetalle
- Tabla: ConsolidadoDetalle
- Campos:
  1. id (BigAutoField, PK)
  2. sindicato (ForeignKey Sindicato, on_delete=PROTECT, obligatorio)
  3. consolidado (ForeignKey ConsolidadoMensual, on_delete=CASCADE, obligatorio)
  4. socio (ForeignKey Socio, on_delete=PROTECT, obligatorio)
  5. tipo_beneficio (ForeignKey TipoBeneficio, on_delete=PROTECT, obligatorio)
  6. monto_aprobado (DecimalField(12,2), obligatorio)
  7. motivo_ajuste (CharField(300), null=True, blank=True)
  8. created_at (DateTimeField, auto_now_add=True)
- Indices:
  1. Index(consolidado, socio)
  2. Index(consolidado, tipo_beneficio)
- Constraints:
  1. UniqueConstraint(fields=[consolidado, socio, tipo_beneficio])
  2. Check monto_aprobado >= 0

### 2.7 Modelo Auditoria
- Tabla: Auditoria
- Campos:
  1. id (BigAutoField, PK)
  2. sindicato (ForeignKey Sindicato, on_delete=PROTECT, obligatorio)
  3. usuario (ForeignKey User, on_delete=SET_NULL, null=True)
  4. accion (CharField(40), obligatorio)
  5. entidad (CharField(60), obligatorio)
  6. entidad_id (CharField(40), obligatorio)
  7. resumen (CharField(255), obligatorio)
  8. payload (JSONField, null=True, blank=True)
  9. ip_origen (GenericIPAddressField, null=True, blank=True)
  10. created_at (DateTimeField, auto_now_add=True)
- Indices:
  1. Index(sindicato, created_at)
  2. Index(entidad, entidad_id)
  3. Index(usuario)
- Constraints:
  1. Ninguno adicional obligatorio
- Soft delete: No aplica (bitacora inmutable).

## 3) Formato Excel de salida (Consolidado final)

### 3.1 Hoja y estructura
- Nombre hoja: Consolidado
- Fila 1: Titulo (Consolidado descuentos sindicales - {Periodo})
- Fila 2: Metadatos (Sindicato, periodo, fecha generacion)
- Fila 4: Encabezados
- Desde fila 5: detalle por socio
- Ultima fila: totales por columna

### 3.2 Orden de columnas (fijo)
1. RUT
2. Nombre
3. Ayuda Trabajador
4. Clinica OMI
5. Confia
6. Copeuch
7. Deuda Sindical
8. Gas
9. Gimnasio
10. Happyland
11. Mochilas
12. Optica
13. Telefonia
14. Veterinaria
15. Total General

Notas:
- Si una columna no tiene movimientos del periodo, se exporta en 0.
- Total General = suma horizontal de columnas de beneficios por socio.

### 3.3 Formato
- Moneda: CLP sin decimales visuales, separador de miles.
- Valores internos: decimal(12,2) en BD; en Excel se presenta redondeado segun politica (normalmente 0 decimales).
- RUT: texto para no perder formato.
- Nombre: texto.
- Encabezados en negrita.
- Fila de totales en negrita.

### 3.4 Totales
- Por socio: columna Total General.
- Por columna: ultima fila suma cada beneficio y total general global.

### 3.5 Nombre de archivo sugerido
`CONSOLIDADO_{CODIGO_SINDICATO}_{YYYYMM}_v{N}.xlsx`
Ejemplo: `CONSOLIDADO_SINDICATO01_202606_v1.xlsx`

## 4) Reglas de validacion MVP

1. Socio activo
- Regla: solo socios con estado=ACTIVO pueden descontar.
- Resultado: si no cumple -> movimiento RECHAZADO.

2. Licencia medica
- Regla: socio con estado_laboral=LICENCIA_MEDICA queda OBSERVADO (o RECHAZADO segun politica de sindicato).
- Resultado: bloquea aprobacion automatica.

3. Desvinculado
- Regla: estado_laboral=DESVINCULADO no permite descuento.
- Resultado: RECHAZADO.

4. Movimiento duplicado
- Regla: no repetir socio+beneficio+periodo+referencia_externa.
- Resultado: error de validacion y no guarda.

5. Monto cero o negativo
- Regla: monto debe ser > 0.
- Resultado: error de validacion y no guarda.

6. RUT invalido
- Regla: validacion modulo 11 al crear/editar socio y al importar.
- Resultado: no se guarda socio/movimiento asociado.

7. Beneficio inactivo
- Regla: no se puede registrar movimiento sobre beneficio inactivo.
- Resultado: error de validacion.

8. Periodo cerrado
- Regla: consolidado en estado CERRADO o EXPORTADO no admite nuevos movimientos ni cambios.
- Resultado: bloqueo de escritura.

## 5) Backlog por sprint

Recomendacion: sprints de 2 semanas.
Duracion total sugerida: 5 sprints (10 semanas) + 1 semana de estabilizacion opcional.

### Sprint 1 - Fundaciones y seguridad
- Objetivo: dejar base multiempresa y acceso seguro.
- Historias: US-SEG-01, US-SOC-01 (parcial), US-BEN-01 (parcial), US-AUD-01 (base)
- Entregables:
  1. Modelos Sindicato, Usuario-Rol, Auditoria base.
  2. Restriccion por tenant en vistas/API.
  3. CRUD basico Socio y TipoBeneficio.
- Riesgos:
  1. Mala definicion de permisos por rol.
- Criterio de termino:
  1. Usuarios solo ven datos de su sindicato.
  2. CRUD basico funcionando con auditoria create/update.

### Sprint 2 - Operacion de movimientos
- Objetivo: registrar correctamente descuentos del periodo.
- Historias: US-MOV-01, US-MOV-02, US-SOC-02, US-BEN-01
- Entregables:
  1. Modelo Movimiento con constraints.
  2. Pantalla de registro y listado de movimientos por periodo.
  3. Deteccion de duplicados y validaciones de monto/beneficio.
- Riesgos:
  1. Datos iniciales inconsistentes.
- Criterio de termino:
  1. Se pueden registrar movimientos validos sin duplicados.

### Sprint 3 - Validaciones y cierre de periodo
- Objetivo: asegurar calidad antes de consolidar.
- Historias: US-VAL-01, US-CON-01
- Entregables:
  1. Reglas MVP implementadas.
  2. Bandeja de observaciones.
  3. Apertura/cierre de periodo.
- Riesgos:
  1. Politica de licencia medica no cerrada con cliente.
- Criterio de termino:
  1. Cerrar periodo bloquea escrituras y deja trazabilidad.

### Sprint 4 - Consolidado automatico
- Objetivo: producir resultado mensual por socio/beneficio.
- Historias: US-CON-02, US-DAS-01 (parcial)
- Entregables:
  1. Generador consolidado (cabecera + detalle).
  2. Recalculo en periodo abierto.
  3. KPI basico en dashboard.
- Riesgos:
  1. Diferencias con calculo esperado por negocio.
- Criterio de termino:
  1. Consolidado coincide con casos de prueba acordados.

### Sprint 5 - Exportacion y cierre MVP
- Objetivo: archivo final utilizable por empresa y salida a produccion inicial.
- Historias: US-EXP-01, US-DAS-01, US-AUD-01, US-SEG-01 ajustes
- Entregables:
  1. Export Excel formato final.
  2. Trazabilidad de exportacion.
  3. Dashboard minimo completo.
  4. Hardening y despliegue Railway.
- Riesgos:
  1. Ajustes de ultimo minuto en formato Excel.
- Criterio de termino:
  1. Cliente valida archivo y proceso end-to-end.

## 6) Plan de pruebas MVP

### 6.1 Pruebas funcionales
1. Aislamiento multiempresa
- Caso: usuario sindicato A no accede a datos de sindicato B.
- Esperado: 403 o dataset vacio segun endpoint.

2. CRUD socios
- Caso: crear socio con RUT valido; editar estado laboral.
- Esperado: persiste y audita.

3. Registro de movimientos
- Caso: movimiento valido y duplicado.
- Esperado: crea valido; bloquea duplicado.

4. Generacion consolidado
- Caso: periodo con movimientos validos/observados/rechazados.
- Esperado: incluye solo aprobables segun regla.

5. Exportacion Excel
- Caso: exportar consolidado cerrado.
- Esperado: columnas/orden/totales correctos y archivo descargable.

6. Validaciones
- Caso: socio inactivo, desvinculado, licencia, monto <= 0, beneficio inactivo, periodo cerrado.
- Esperado: bloqueo o observacion segun regla.

7. Permisos por rol
- Caso: dirigente sin permiso de edicion.
- Esperado: puede ver dashboard/consolidado pero no editar movimientos.

8. Auditoria
- Caso: crear/editar/eliminar logico/generar/exportar.
- Esperado: evento registrado con usuario y fecha.

### 6.2 Pruebas tecnicas
1. Unit tests: validadores de RUT, reglas de negocio, calculo consolidado.
2. Integration tests: flujo completo movimiento->validacion->consolidado->export.
3. Security tests: tenant scoping y autorizacion por rol.
4. Performance smoke: consolidado de volumen base (ej. 5.000 socios x 12 beneficios).

### 6.3 Criterio de salida QA
- 0 defectos criticos abiertos.
- 0 defectos altos en flujo principal.
- Cobertura de pruebas del dominio critico >= 70% (servicios de consolidado/validacion).

## 7) Exclusiones claras del MVP

Queda fuera explicitamente:
1. Portal del socio.
2. Telefonia avanzada (vencimientos, deuda historica especializada).
3. Gestion documental avanzada.
4. IA Assistant.
5. Integraciones externas (ERP, APIs empresa, SSO corporativo).
6. Aplicacion movil nativa.
7. Reglas complejas parametrizables tipo motor DSL.
8. Automatizaciones fuera del proceso de consolidado mensual.

## 8) Alcance comercial y control de sobredimensionamiento

- Implementacion inicial objetivo: $1.350.000
- Mantencion mensual objetivo: $99.000

Recomendaciones para sostener el margen:
1. Congelar alcance en historias P0 para contrato MVP.
2. Cualquier P1 entra a fase posterior con adenda.
3. Definir y firmar template Excel final en Sprint 1 para evitar retrabajo.
4. Limitar customizaciones por cliente en MVP (configuracion basica, no desarrollo a medida).

## 9) Resumen de horas MVP (realista)

Estimacion recomendada para cumplir calidad minima:
- Rango objetivo: 420 a 520 horas.
- Punto medio planificado: 460 horas.

Distribucion sugerida:
1. Analisis final y especificacion ejecutable: 30 h
2. Backend dominio y seguridad: 170 h
3. Frontend pantallas MVP: 120 h
4. Consolidado + export Excel: 70 h
5. QA + estabilizacion + despliegue: 70 h

Con este alcance, el MVP se mantiene simple, ejecutable y orientado al valor principal: consolidado mensual automatico para descuento por planilla.
