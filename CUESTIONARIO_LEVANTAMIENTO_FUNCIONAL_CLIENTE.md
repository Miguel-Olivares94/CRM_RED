# Cuestionario formal de levantamiento funcional

Fecha: 2026-06-12
Proyecto: Plataforma de descuentos sindicales (MVP)
Objetivo del cuestionario: cerrar reglas de negocio y responsabilidades operativas para construir correctamente el proceso de consolidacion mensual.

## 1) Instrucciones de respuesta

- Completar todas las preguntas marcadas como Critica (C).
- Para preguntas con opciones, marcar una o mas alternativas.
- Si aplica excepcion, incluir ejemplo real (periodo, RUT, beneficio, monto).
- Registrar responsable que responde por cada bloque.

## 2) Datos de control de la sesion

- Cliente / Sindicato:
- Empresa pagadora (ej. DHL):
- Fecha de levantamiento:
- Participantes:
- Responsable funcional del sindicato:
- Responsable funcional de empresa pagadora:
- Periodo de referencia analizado (YYYY-MM):

## 3) Preguntas pendientes por tema

### 3.1 Consolidado final

1. (C) Cual es el formato oficial de salida que la empresa acepta hoy?
- Respuesta:

2. (C) El consolidado final debe incluir todos los socios o solo socios con descuento en el periodo?
- Opciones: [ ] Todos [ ] Solo con descuento [ ] Depende de regla
- Respuesta:

3. (C) El total general por socio corresponde a la suma de todas las columnas de beneficio sin excepcion?
- Opciones: [ ] Si [ ] No
- Si no, indicar excepciones:

4. (C) Existen columnas obligatorias fijas aunque no tengan monto (valor 0)?
- Respuesta:

5. (C) Se requiere versionado del consolidado (v1, v2, v3) antes de envio final?
- Opciones: [ ] Si [ ] No
- Regla de versionado:

6. (M) Se necesita firma o aprobacion formal antes de exportar/enviar?
- Opciones: [ ] Si [ ] No
- Quien aprueba:

### 3.2 Reglas de exclusion

7. (C) Que casos excluyen automaticamente un movimiento del consolidado?
- Opciones sugeridas: [ ] RUT invalido [ ] socio inactivo [ ] beneficio inactivo [ ] periodo cerrado [ ] monto invalido [ ] otro
- Detalle:

8. (C) Cuando una regla falla, el movimiento debe quedar en estado observado o rechazado definitivo?
- Opciones: [ ] Observado [ ] Rechazado [ ] Depende
- Criterio:

9. (M) Se permite excepcion manual para incluir un movimiento inicialmente excluido?
- Opciones: [ ] Si [ ] No
- Quien autoriza:

### 3.3 Licencias medicas

10. (C) Si un socio esta en licencia medica durante el periodo, se descuenta o no se descuenta?
- Opciones: [ ] Se descuenta [ ] No se descuenta [ ] Depende de beneficio
- Regla exacta:

11. (C) Si depende de beneficio, indicar cuales si y cuales no.
- Respuesta:

12. (M) La licencia medica se informa antes del cierre o puede llegar retroactiva?
- Opciones: [ ] Antes [ ] Retroactiva [ ] Ambas
- Tratamiento retroactivo:

13. (M) Si hay licencia parcial en el mes, el descuento es total, proporcional o cero?
- Opciones: [ ] Total [ ] Proporcional [ ] Cero [ ] Depende
- Formula:

### 3.4 Desvinculados

14. (C) Desde que fecha exacta un socio desvinculado deja de descontar?
- Opciones: [ ] Fecha carta [ ] Fecha sistema empresa [ ] Fin de mes [ ] Otra
- Regla exacta:

15. (C) Si el movimiento fue cargado antes de saber la desvinculacion, se elimina, se observa o se reprograma?
- Opciones: [ ] Eliminar [ ] Observar [ ] Reprogramar [ ] Otro
- Respuesta:

16. (M) Existen finiquitos o ajustes finales que se deban aplicar al desvinculado?
- Respuesta:

### 3.5 Topes de descuento

17. (C) Existen topes maximos por socio al mes?
- Opciones: [ ] Si [ ] No
- Monto o porcentaje:

18. (C) Existen topes por tipo de beneficio?
- Opciones: [ ] Si [ ] No
- Detalle por beneficio:

19. (M) Si supera tope, que prioridad se aplica para recortar?
- Opciones: [ ] Orden fijo [ ] Prorrata [ ] Manual
- Orden/prioridad:

20. (M) El remanente no descontado pasa al mes siguiente?
- Opciones: [ ] Si [ ] No [ ] Depende
- Regla:

### 3.6 Telefonia

21. (C) Telefonia se descuenta por monto fijo, por cuota o por consumo del mes?
- Opciones: [ ] Fijo [ ] Cuota [ ] Consumo [ ] Mixto
- Regla:

22. (C) La planilla de telefonia llega con identificador unico por socio/linea para detectar duplicados?
- Opciones: [ ] Si [ ] No
- Campo identificador:

23. (M) Existen vencimientos, mora o intereses en telefonia para MVP?
- Opciones: [ ] Si [ ] No
- Si si, detalle minimo requerido:

24. (M) Se necesita consolidar varias lineas de un socio en una sola columna Telefonia?
- Opciones: [ ] Si [ ] No
- Regla de suma:

### 3.7 Gas

25. (C) Gas se descuenta como monto unico mensual por socio o puede haber multiples movimientos en un mes?
- Opciones: [ ] Unico [ ] Multiples
- Regla:

26. (C) Existen limites por cantidad de vales o monto mensual para gas?
- Opciones: [ ] Si [ ] No
- Limite:

27. (M) Si hay anulacion/devolucion de vale de gas, como se refleja?
- Opciones: [ ] Abono en mismo mes [ ] Ajuste mes siguiente [ ] Otro
- Regla:

### 3.8 Copeuch

28. (C) Copeuch llega como descuento mensual fijo por socio o varian segun estado de deuda?
- Opciones: [ ] Fijo [ ] Variable
- Regla:

29. (C) Si no alcanza capacidad de descuento del mes, como se prioriza Copeuch frente a otros beneficios?
- Respuesta:

30. (M) Se requiere trazabilidad de numero de operacion Copeuch en MVP?
- Opciones: [ ] Si [ ] No
- Campo requerido:

### 3.9 Validaciones actuales (proceso manual)

31. (C) Cuales validaciones se hacen hoy SIEMPRE antes de enviar a empresa?
- Listado obligatorio:

32. (C) Cuales validaciones se hacen solo a veces (segun tiempo o criterio)?
- Listado:

33. (C) Quien ejecuta cada validacion hoy (rol/persona)?
- Respuesta:

34. (M) Existe checklist formal o se realiza por experiencia del equipo?
- Opciones: [ ] Checklist formal [ ] Experiencia [ ] Mixto
- Adjuntar evidencia:

35. (M) Cual es el error mas frecuente detectado en las planillas actuales?
- Respuesta:

### 3.10 Archivos enviados y recibidos con la empresa

36. (C) Que archivos recibe el sindicato desde la empresa y con que frecuencia?
- Nombre archivo / formato / fecha limite:

37. (C) Que archivos envia el sindicato a la empresa y en que fecha de corte?
- Nombre archivo / formato / canal envio:

38. (C) Cual es la fecha limite mensual de envio del consolidado?
- Respuesta:

39. (C) Que pasa si el archivo se envia fuera de plazo?
- Respuesta:

40. (M) Se requiere acuse de recibo formal por parte de la empresa?
- Opciones: [ ] Si [ ] No
- Medio de confirmacion:

41. (M) Se corrige archivo luego del envio? Si si, cual es el procedimiento de reenvio?
- Respuesta:

## 4) Matriz de responsabilidades (AS-IS y TO-BE)

Completar con detalle operativo real.

### 4.1 Procesos actuales (AS-IS)

#### A) Que procesos realiza hoy DHL (empresa pagadora)
- 1.
- 2.
- 3.

#### B) Que procesos realiza hoy el sindicato
- 1.
- 2.
- 3.

### 4.2 Procesos objetivo (TO-BE)

#### C) Que parte debe automatizar el sistema
- 1. Registro de movimientos por beneficio.
- 2. Validaciones de negocio.
- 3. Generacion consolidado mensual.
- 4. Exportacion Excel final.
- 5. Trazabilidad/auditoria del proceso.
- 6. (Completar extras)

#### D) Que parte seguira siendo responsabilidad de la empresa
- 1.
- 2.
- 3.

## 5) Definiciones criticas para cierre de levantamiento

Marcar como Cerrado cuando quede 100% definido.

1. Politica de licencia medica: [ ] Cerrado [ ] Pendiente
2. Politica de desvinculados: [ ] Cerrado [ ] Pendiente
3. Topes y prioridad de descuento: [ ] Cerrado [ ] Pendiente
4. Formato oficial Excel final: [ ] Cerrado [ ] Pendiente
5. Fecha de corte y SLA de envio: [ ] Cerrado [ ] Pendiente
6. Reglas de exclusion definitivas: [ ] Cerrado [ ] Pendiente
7. Responsables por validacion y aprobacion: [ ] Cerrado [ ] Pendiente

## 6) Criterio de salida del levantamiento

El levantamiento se considera completo cuando:
- Todas las preguntas Criticas (C) tienen respuesta validada por cliente.
- Existe un ejemplo real de consolidado esperado con datos anonimizados.
- Quedan definidos: formato final, reglas de exclusion, fechas de corte y responsables.
- Se aprueba por escrito la matriz de responsabilidades DHL/Sindicato/Sistema.

## 7) Firmas de conformidad

- Responsable funcional Sindicato:
- Responsable funcional Empresa:
- Responsable tecnico proyecto:
- Fecha de aprobacion:
