# Analisis de plantillas cliente - Sindicato

Fecha: 2026-06-13
Alcance: evaluar si las 3 fuentes (Gas, Telefonia, Copeuch) permiten construir automaticamente el consolidado mensual en el MVP actual.

## 1) Fuentes analizadas

### Fuente A: Gas
Columnas observadas:
- RUT
- NOMBRE APELLIDO
- SITE
- VALE DE GAS
- MONTO

### Fuente B: Telefonia
Columnas observadas:
- RUT
- Razon social
- Cuenta
- PCS
- Cargo Fijo
- Fecha de entrega

Notas observadas:
- Filas con texto "baja".
- Colores semaforo (verde/amarillo/rojo) que no son datos estructurados por si mismos.

### Fuente C: Copeuch
Columnas observadas (tabla principal):
- RUT
- NOMBRE
- FEC. ING. SOCIO
- ACCIONES
- PRESTAMOS
- TOT. DCTOS.

Notas observadas:
- Casos marcados como "LICENCIA MEDICA".
- Casos marcados como "DESPEDIDO".

## 2) Campos comunes y clave de union

Campos comunes reales entre las 3 fuentes:
- RUT (siempre presente) -> clave de union primaria
- NOMBRE / Razon social (presentes en las 3, con variacion de encabezado)
- MONTO descuento (Gas.MONTO, Telefonia.Cargo Fijo, Copeuch.TOT. DCTOS.)

Campo clave de union propuesto:
- RUT normalizado (sin puntos, con DV, en formato unico por empresa)

## 3) Reglas de exclusion / tratamiento operacional

Reglas detectadas en planillas:
- "despedido" -> excluir de consolidado
- "baja" -> excluir de consolidado
- "licencia medica" -> no excluir automaticamente (regla acordada del proyecto), solo marcar observacion/estado laboral

Reglas compatibles con el servicio actual de consolidado:
- Ya excluye socios DESVINCULADO
- Ya excluye movimientos RECHAZADO
- Ya incluye LICENCIA_MEDICA con motivo_ajuste (no exclusion dura)

Propuesta de derivacion:
- baja, despedido -> socio.estado_laboral = DESVINCULADO
- licencia medica -> socio.estado_laboral = LICENCIA_MEDICA
- monto <= 0 -> fila rechazada (o validacion especifica por fuente antes de crear movimiento)

## 4) Beneficios detectados

Beneficios claros en las 3 fuentes:
- Gas
- Telefonia
- Copeuch

Subdatos de beneficio que hoy vienen en columnas auxiliares:
- Gas: "VALE DE GAS" (ej. 11/15/45 kilos)
- Telefonia: Cuenta, PCS, Fecha de entrega
- Copeuch: Acciones, Prestamos, Fecha ingreso socio

## 5) Mapeo propuesto hacia MovimientoSindicato

Mapeo minimo (operativo) para generar consolidado:

| Fuente | Campo origen | Campo sistema |
|---|---|---|
| Todas | RUT | SocioSindicato.rut |
| Gas | NOMBRE APELLIDO | SocioSindicato.nombre |
| Telefonia | Razon social | SocioSindicato.nombre |
| Copeuch | NOMBRE | SocioSindicato.nombre |
| Gas | SITE | SocioSindicato.site |
| Gas | MONTO | MovimientoSindicato.monto |
| Telefonia | Cargo Fijo | MovimientoSindicato.monto |
| Copeuch | TOT. DCTOS. | MovimientoSindicato.monto |
| Todas | Periodo de carga | MovimientoSindicato.periodo |
| Todas | Tipo de beneficio (Gas/Telefonia/Copeuch) | MovimientoSindicato.tipo_beneficio |
| Todas | Marca de origen (archivo/fila) | MovimientoSindicato.referencia_externa |
| Telefonia | Cuenta / PCS / Fecha entrega | MovimientoSindicato.observacion (texto estructurado) |
| Copeuch | Acciones / Prestamos / observacion estado | MovimientoSindicato.observacion |

## 6) Cobertura actual del sistema vs plantillas

### 6.1 Campos ya cubiertos por el sistema

Cubiertos en modelo/importador:
- RUT
- Nombre
- Monto (> 0)
- Site
- Periodo
- Tipo beneficio
- Observacion
- Referencia externa
- Tenant isolation por empresa

Cubiertos en consolidado/export:
- Agregacion por socio x beneficio
- Totales por socio y total general
- Cierre de periodo y estado exportado
- Auditoria de generar/cerrar/exportar

### 6.2 Campos faltantes o con cobertura parcial

No cubiertos de forma estructurada (hoy quedan en observacion o se pierden):
- Vale de gas (kilos) como dato atomico
- Cuenta
- PCS
- Fecha de entrega
- Acciones
- Prestamos
- Fecha ingreso socio (si viene por fuente)
- Motivo laboral detectado por parsing (baja/despedido/licencia) como dato trazable por fila

## 7) Ajustes menores recomendados al modelo actual

Ajustes pequenos, de bajo impacto, para subir robustez sin rediseno mayor:

1. En MovimientoSindicato agregar `metadata_fuente` (JSONField, default dict)
- Guardar: cuenta, pcs, vale_gas, fecha_entrega, acciones, prestamos, motivo_detectado.

2. En MovimientoSindicato agregar `fuente` (CharField con choices)
- Valores: GAS, TELEFONIA, COPEUCH, OTRO.

3. En importadores por fuente aplicar normalizador de estado laboral
- Si detecta "baja" o "despedido": setear SocioSindicato.estado_laboral=DESVINCULADO.
- Si detecta "licencia medica": setear SocioSindicato.estado_laboral=LICENCIA_MEDICA.

4. Mantener regla vigente del proyecto
- No excluir automaticamente licencias medicas como regla fija.

## 8) Conclusion de factibilidad

Respuesta corta: SI, el consolidado puede construirse desde estas 3 fuentes en el MVP actual.

Nivel estimado de cobertura operativa con modelo actual:
- 80% a 90% del proceso mensual.

Por que si:
- RUT + monto + beneficio + periodo existen en las 3 fuentes y son suficientes para consolidar.
- El consolidado del sistema ya opera por socio/beneficio y estados de periodo.

Que explica el 10%-20% restante:
- Trazabilidad fina de campos fuente (Cuenta/PCS/Prestamos/etc.) no modelada de forma estructurada.
- Reglas laborales detectadas en texto/colores requieren parser por fuente para automatizacion estable.

## 9) Recomendacion para decision MVP

Recomendacion: avanzar con piloto usando las 3 fuentes, con este criterio:
- Carga automatica base para consolidado (RUT, nombre, monto, beneficio, periodo).
- Parser simple de estados (baja/despedido/licencia) antes de consolidar.
- Iteracion corta posterior para agregar `fuente` + `metadata_fuente` y cerrar brecha de trazabilidad.

Con eso, el MVP cubre la operacion principal y reduce trabajo manual de forma significativa sin bloquear salida a cliente.
