# Guía de Uso - Sistema de Análisis de Documentos de Solventación

## Descripción General

Esta aplicación procesa automáticamente archivos DOCX y XLSX de propuestas de solventación, extrayendo información estructurada y generando una base de datos consolidada.

## Características Principales

✓ **Lectura automática** de todos los archivos .xlsx y .docx
✓ **Extracción inteligente** de información clave:
  - Nombre del ente
  - Fuente de financiamiento
  - Periodo
  - Propuestas de solventación
  - Observaciones

✓ **Validación de imágenes** en propuestas de solventación
✓ **Base de datos consolidada** en Excel organizada por ente y financiamiento
✓ **Reportes detallados** en JSON para análisis adicional

## Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Instalar Dependencias

```bash
pip install -r requirements.txt
```

Las dependencias principales son:
- `python-docx`: Para procesar archivos DOCX
- `openpyxl`: Para procesar archivos XLSX
- `pandas`: Para manipulación de datos
- `tqdm`: Para barras de progreso
- `Flask`: Para interfaz web (opcional)

## Uso Básico

### 1. Procesamiento por Lotes (Recomendado)

El procesamiento por lotes es el método principal para analizar múltiples archivos.

```bash
# Procesar archivos en la carpeta 'ejemplos' (por defecto)
python batch_processor.py

# Especificar carpeta de entrada y salida
python batch_processor.py --entrada ./mis_documentos --salida ./resultados

# Ver ayuda
python batch_processor.py --help
```

### 2. Estructura de Carpetas

```
solventacion-/
├── ejemplos/                    # Carpeta de entrada (archivos a procesar)
│   ├── archivo1.docx
│   ├── archivo2.xlsx
│   └── ...
│
├── resultados_consolidados/     # Carpeta de salida (resultados)
│   ├── base_datos_consolidada_YYYYMMDD_HHMMSS.xlsx
│   ├── reporte_imagenes_YYYYMMDD_HHMMSS.json
│   ├── estadisticas_YYYYMMDD_HHMMSS.json
│   ├── resumen_procesamiento_YYYYMMDD_HHMMSS.json
│   ├── individuales/           # Resultados JSON individuales
│   └── logs/                   # Logs de procesamiento
│
└── ...
```

## Archivos de Salida

### 1. Base de Datos Consolidada (Excel)

**Archivo:** `base_datos_consolidada_YYYYMMDD_HHMMSS.xlsx`

**Hojas del Excel:**

- **Base de Datos Completa**: Todos los registros consolidados
  - Columnas: Ente, Fuente de Financiamiento, Periodo, Tipo Documento, Archivo Origen, Número Propuesta, Observación, Propuesta de Solventación, Hoja, Fila, Fecha Procesamiento

- **Ente_[NOMBRE]**: Una hoja por cada ente detectado

- **Por Fuente Financiamiento**: Resumen agrupado por fuente

- **Resumen Estadístico**: Estadísticas generales del procesamiento

### 2. Reporte de Imágenes (JSON)

**Archivo:** `reporte_imagenes_YYYYMMDD_HHMMSS.json`

Contiene información sobre imágenes detectadas en propuestas de solventación:

```json
{
  "fecha_generacion": "2025-11-21T00:05:19.206804",
  "total_archivos_validados": 13,
  "archivos_validos": 12,
  "archivos_con_advertencias": 1,
  "total_imagenes_detectadas": 4,
  "archivos_con_imagenes_en_propuestas": [...]
}
```

### 3. Estadísticas Consolidadas (JSON)

**Archivo:** `estadisticas_YYYYMMDD_HHMMSS.json`

Estadísticas del procesamiento:

```json
{
  "total_registros": 87,
  "total_archivos": 13,
  "total_entes": 4,
  "total_fuentes": 7,
  "entes": ["FIDECIX", "SEPUEDE", ...],
  "fuentes": ["SA", "PEFCF", "R", ...],
  "distribucion_por_ente": {...},
  "distribucion_por_fuente": {...}
}
```

### 4. Resumen de Procesamiento (JSON)

**Archivo:** `resumen_procesamiento_YYYYMMDD_HHMMSS.json`

Resumen completo del procesamiento con todas las estadísticas.

## Uso Programático

### Procesar un Archivo Individual

```python
from processors.docx_processor_optimized import process_docx
from processors.xlsx_processor_optimized import process_xlsx
from metadata_analyzer import analizar_archivo
from image_validator import validar_archivo

# Procesar archivo DOCX
contenido = process_docx('ruta/archivo.docx')

# Extraer metadatos
metadatos = analizar_archivo('ruta/archivo.docx', contenido)

# Validar imágenes
reporte_imagenes = validar_archivo('ruta/archivo.docx', contenido)

# Procesar archivo XLSX
contenido_xlsx = process_xlsx('ruta/archivo.xlsx')
```

### Crear Base de Datos Consolidada Manualmente

```python
from metadata_analyzer import analizar_archivo
from database_consolidator import agregar_datos_archivo, generar_excel_consolidado

# Procesar múltiples archivos
for archivo in archivos:
    contenido = process_docx(archivo)  # o process_xlsx
    metadatos = analizar_archivo(archivo, contenido)
    agregar_datos_archivo(metadatos, contenido)

# Generar Excel consolidado
generar_excel_consolidado('mi_base_datos.xlsx')
```

## Formato de Nombres de Archivo

Para una mejor extracción de metadatos, use el siguiente formato:

```
[Número].[ENTE]_[TipoDoc]_[Mes1]_[Mes2]_[Fuente].docx
```

**Ejemplos:**
- `12.FIDECIX_RRyPE_ENE_JUN_SA.docx`
- `5.SEPUEDE_REA_RRyPE_ENE_ENE_PEFCF.xlsx`

**Componentes:**
- **Número**: Identificador numérico (opcional)
- **ENTE**: Nombre del ente (FIDECIX, SEPUEDE, etc.)
- **TipoDoc**: Tipo de documento (RRyPE, REA, etc.)
- **Mes1_Mes2**: Periodo (ENE_JUN, ENE_ENE, etc.)
- **Fuente**: Fuente de financiamiento (SA, PEFCF, R, PRAS, PDP)

## Fuentes de Financiamiento Reconocidas

- **SA**: Subsidio para la Asistencia
- **PEFCF**: Programa Especial de Fondos y Contingencias Fiscales
- **R**: Recursos Propios
- **PRAS**: Programa de Recursos de Alta Seguridad
- **PDP**: Programa de Desarrollo Profesional
- **REA**: Recursos Extraordinarios Adicionales

## Detección de Imágenes

La aplicación detecta y reporta imágenes en las propuestas de solventación:

- ✓ **Válido**: No hay imágenes en propuestas
- ⚠ **Advertencia**: Se detectaron imágenes en propuestas o en hojas que contienen propuestas

Los archivos con advertencias se listan en el reporte de imágenes para revisión manual.

## Solución de Problemas

### Error: "No se encontraron archivos para procesar"

**Solución:** Verifique que la carpeta de entrada existe y contiene archivos .docx o .xlsx

### Error: "ModuleNotFoundError"

**Solución:** Instale las dependencias con `pip install -r requirements.txt`

### Error al procesar un archivo específico

**Solución:** Revise el log en `resultados_consolidados/logs/` para ver el error detallado

### No se extraen propuestas de un archivo

**Posibles causas:**
1. El archivo no contiene tablas con el texto "PROPUESTA DE SOLVENTACIÓN"
2. La estructura del archivo es diferente a la esperada
3. El archivo está corrupto

**Solución:** Revise el archivo individual en `resultados_consolidados/individuales/`

## Arquitectura del Sistema

El sistema está compuesto por módulos independientes:

1. **Procesadores** (`processors/`): Extraen contenido de DOCX y XLSX
2. **Analizador de Metadatos** (`metadata_analyzer.py`): Extrae información estructurada
3. **Validador de Imágenes** (`image_validator.py`): Detecta imágenes en propuestas
4. **Consolidador** (`database_consolidator.py`): Genera base de datos en Excel
5. **Procesador por Lotes** (`batch_processor.py`): Punto de entrada principal

## Interfaz Web (Opcional)

También puede usar la interfaz web Flask:

```bash
python app.py
```

Acceda a: `http://localhost:5023`

## Ejemplos de Uso

### Ejemplo 1: Procesar carpeta de documentos

```bash
python batch_processor.py --entrada /ruta/a/documentos --salida /ruta/a/resultados
```

### Ejemplo 2: Análisis rápido de estadísticas

```python
from batch_processor import BatchProcessor

processor = BatchProcessor('ejemplos', 'resultados')
processor.procesar_todos()
```

### Ejemplo 3: Validar solo imágenes

```python
from image_validator import validar_archivo
from processors.docx_processor_optimized import process_docx

contenido = process_docx('archivo.docx')
reporte = validar_archivo('archivo.docx', contenido)

if reporte['tiene_imagenes_en_propuestas']:
    print(f"⚠ Advertencia: {reporte['nombre_archivo']} contiene imágenes")
```

## Soporte y Contribuciones

Para reportar problemas o sugerir mejoras, consulte el archivo `README.md` o contacte al equipo de desarrollo.

## Licencia

Ver archivo `LICENSE` para más información.
