# Arquitectura de la Aplicación de Análisis de Documentos

## Visión General
Sistema modular para procesar automáticamente archivos DOCX y XLSX, extraer información estructurada y generar base de datos consolidada.

## Módulos Principales

### 1. Extractores (processors/)
- `docx_processor_optimized.py`: Procesa archivos DOCX
- `xlsx_processor_optimized.py`: Procesa archivos XLSX
- **Funcionalidades**: Extrae contenido, metadatos, imágenes, propuestas

### 2. Analizador de Metadatos (metadata_analyzer.py)
- **Propósito**: Extrae información clave de nombres y contenido
- **Extrae**:
  - Nombre del ente (ej: FIDECIX, SEPUEDE, etc.)
  - Fuente de financiamiento (ej: SA, PEFCF, R, PRAS, PDP)
  - Periodo (ej: ENE-JUN, ENE-ENE)
  - Tipo de documento (ej: RRyPE, REA)

### 3. Detector de Imágenes (image_validator.py)
- **Propósito**: Validar que PROPUESTA DE SOLVENTACIÓN no contenga imágenes
- **Funcionalidades**:
  - Detecta imágenes dentro de propuestas
  - Reporta archivos con imágenes en propuestas
  - Extrae ubicación exacta de las imágenes

### 4. Consolidador (database_consolidator.py)
- **Propósito**: Genera base de datos consolidada
- **Estructura de salida**:
  - Organizado por Ente
  - Sub-organizado por Fuente de Financiamiento
  - Con histórico completo de propuestas
- **Formato de salida**: Excel con múltiples hojas

### 5. Procesador por Lotes (batch_processor.py)
- **Propósito**: Punto de entrada principal
- **Funcionalidades**:
  - Procesa todos los archivos de una carpeta
  - Genera reportes consolidados
  - Maneja errores y excepciones
  - Muestra progreso en tiempo real

## Flujo de Datos

```
[Archivos DOCX/XLSX] 
    ↓
[Extractores] → Contenido + Metadatos + Imágenes
    ↓
[Metadata Analyzer] → Ente + Financiamiento + Periodo
    ↓
[Image Validator] → Reportes de imágenes en propuestas
    ↓
[Database Consolidator] → Base de datos consolidada (Excel)
    ↓
[Salida: base_datos_consolidada.xlsx + reportes_imagenes.json]
```

## Principios de Diseño
1. **Modularidad**: Cada módulo tiene una responsabilidad única
2. **Reutilización**: Usa los procesadores existentes
3. **Claridad**: Nombres de funciones y variables autodescriptivos
4. **Documentación**: Docstrings en español
5. **Sin redundancias**: Evita duplicación de código

## Archivos de Salida
- `base_datos_consolidada.xlsx`: Base de datos organizada
- `reportes_imagenes.json`: Archivos con imágenes en propuestas
- `logs/procesamiento.log`: Registro detallado de operaciones
