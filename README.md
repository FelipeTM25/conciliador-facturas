# Conciliador de facturas y retenciones

Prototipo que concilia un archivo de facturas de proveedores contra el registro contable. Valida cálculos de IVA, retenciones y totales, detecta duplicados y facturas sin contabilizar, y muestra un resumen con el detalle de cada inconsistencia.

- **Backend:** API en Python con FastAPI y pandas.
- **Frontend:** aplicación web en Angular.

## Requisitos previos

| Herramienta | Versión usada | Notas |
|---|---|---|
| Python | 3.12.10 | Mínimo recomendado: 3.10 |
| pip | 25.x | Incluido con Python |
| Node.js | 24.16.0 | Mínimo: 20.19 (requerido por Angular 20) |
| npm | 11.13.0 | Incluido con Node.js |

No se requiere base de datos ni variables de entorno.

## Estructura del proyecto

```
conciliador-facturas/
├── backend/
│   ├── app/
│   │   ├── main.py           # Aplicación FastAPI y configuración CORS
│   │   ├── api.py            # Endpoint POST /api/conciliacion
│   │   ├── csv_reader.py     # Lectura y validación de los CSV
│   │   ├── conciliacion.py   # Reglas de conciliación
│   │   └── schemas.py        # Modelos de respuesta
│   └── requirements.txt
├── frontend/                 # Aplicación Angular
└── data/                     # Archivos de prueba
    ├── facturas.csv
    └── contabilidad.csv
```

## Instalación y ejecución

Se necesitan dos terminales: una para el backend y otra para el frontend.

### 1. Backend

```bash
cd backend
python -m venv .venv
```

Activar el entorno virtual:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Instalar dependencias y levantar el servidor:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

La API queda disponible en `http://127.0.0.1:8000`.

- Verificación: `http://127.0.0.1:8000/health` debe responder `{"status":"ok"}`.
- Documentación interactiva (Swagger): `http://127.0.0.1:8000/docs`.

Dependencias (`backend/requirements.txt`):

| Paquete | Versión |
|---|---|
| fastapi | 0.128.8 |
| uvicorn[standard] | 0.39.0 |
| pandas | 2.3.3 |
| python-multipart | 0.0.20 |
| pydantic | 2.13.5 |

### 2. Frontend

```bash
cd frontend
npm install
npm start
```

La aplicación queda disponible en `http://localhost:4200`.

Dependencias principales: Angular 20.3, TypeScript 5.9, RxJS 7.8 (ver `frontend/package.json`).

## Configuración

- **URL del backend:** el frontend consume `http://127.0.0.1:8000/api/conciliacion`, definida en `frontend/src/app/services/conciliacion.service.ts`. Si el backend corre en otro puerto, se debe actualizar allí.
- **CORS:** el backend acepta peticiones de `http://localhost:4200` y `http://127.0.0.1:4200`, configurado en `backend/app/main.py`. Si el frontend corre en otro origen, se debe agregar allí.

## Uso

1. Con backend y frontend en ejecución, abrir `http://localhost:4200`.
2. Cargar `data/facturas.csv` en **Facturas** y `data/contabilidad.csv` en **Contabilidad**.
3. Presionar **Procesar**.
4. Revisar el resumen y el detalle; el detalle se puede filtrar por estado (Todas, Correcta, Con inconsistencia).

También se puede probar la API directamente:

```bash
curl -X POST http://127.0.0.1:8000/api/conciliacion \
  -F "facturas=@data/facturas.csv" \
  -F "contabilidad=@data/contabilidad.csv"
```

## Formato de los archivos

Archivos CSV separados por comas, con encabezado, en UTF-8 o Latin-1.

**facturas.csv**

`id_factura, nit_proveedor, fecha_factura, concepto, base_gravable, tarifa_iva, valor_iva, tarifa_retencion, valor_retencion, total_factura`

**contabilidad.csv**

`id_factura, fecha_contabilizacion, cuenta_contable, centro_costo, valor_debito, valor_credito, estado`

Si un archivo no es CSV, está vacío, no tiene registros o le faltan columnas, la API responde con un error 400 que indica el problema.

## Reglas de conciliación

Cada factura se marca como **Correcta** o **Con inconsistencia**. Las causas posibles son:

| Causa | Regla |
|---|---|
| Campos obligatorios vacíos | Falta algún dato obligatorio de la factura |
| Factura duplicada | El `id_factura` aparece más de una vez en facturas |
| IVA no coincide con base × tarifa | `valor_iva` difiere de `base_gravable × tarifa_iva` |
| Total no coincide con base + IVA − retención | `total_factura` difiere de `base_gravable + IVA − valor_retencion` |
| Sin registro contable | La factura no existe en contabilidad |
| Registro contable duplicado | La factura tiene más de un registro en contabilidad |
| Registro contable no contabilizado | El estado contable es distinto de `Contabilizada` |

Las comparaciones de valores usan una tolerancia de ±1 peso para absorber diferencias de redondeo.

### Decisión abierta: IVA incorrecto y validación del total

Cuando el IVA reportado no coincide con `base_gravable × tarifa_iva`, queda por definir con el equipo funcional si también se debe reportar que el total no cuadra, o si eso ya se deduce del error de IVA.

**Comportamiento actual del prototipo:** el total se valida contra el IVA **calculado**, no contra el reportado. Así, cada causa señala un error independiente:

- Si el total es coherente con el IVA correcto, solo se reporta *IVA no coincide*. Es el caso de FAC-0006 y FAC-0018 en los archivos de prueba: el IVA reportado está mal, pero el total corresponde a base + IVA correcto − retención.
- Si el total tampoco cuadra con el IVA correcto, se reportan ambas causas.

**Alternativa:** validar el total contra el IVA reportado, para detectar también facturas cuya suma interna no es coherente. En ese caso, FAC-0006 y FAC-0018 mostrarían además *Total no coincide*, aunque el total sea el valor que realmente debería pagarse.

## Resultados con los archivos de prueba

| Indicador | Valor |
|---|---|
| Total de facturas | 50 |
| Correctas | 28 |
| Con inconsistencias | 22 |

## Documentación adicional

- `docs/`: presentación ejecutiva del prototipo dirigida al equipo funcional.

## Declaración sobre el uso de inteligencia artificial

Durante el desarrollo usé Claude (Anthropic) como asistente de programación, de forma consciente y declarada.

**Contexto.** Mi experiencia principal está en análisis de datos y en desarrollo backend con Java y Spring Boot; Python no es mi lenguaje habitual. Elegí Python con pandas porque es la herramienta más adecuada para procesar y cruzar archivos tabulares, y usé la IA para cerrar la brecha con el lenguaje y sus librerías.

**Lo que hice yo:**

- Analicé los archivos de facturas y contabilidad, identifiqué los tipos de inconsistencia presentes y definí las reglas de conciliación (cálculo de IVA, total, duplicados, registros faltantes o no contabilizados).
- Definí la arquitectura de la solución (API + aplicación web) y el alcance del prototipo.
- Revisé, ejecuté y validé el resultado contra los archivos de prueba, comprobando que las inconsistencias detectadas correspondieran con los datos.

**En lo que me apoyé en la IA:**

- **Backend:** implementación en Python de las reglas definidas (lectura y validación de CSV con pandas, lógica de conciliación y endpoint con FastAPI), adaptando a Python los conceptos que manejo en Spring Boot.
- **Frontend:** estilos visuales con la identidad de Bancolombia y el filtro del detalle por estado.
- **Documentación:** redacción de este README y de la presentación ejecutiva, a partir del código y de los resultados reales del prototipo.

Todo el código generado fue revisado y probado antes de incluirlo, y puedo explicar las decisiones y reglas de la solución.
