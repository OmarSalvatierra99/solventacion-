# Solventación - Sistema Optimizado de Procesamiento de Documentos

## 📋 Descripción General

Sistema de procesamiento inteligente de documentos DOCX y XLSX para extracción de propuestas de solventación, con extracción completa y fiel del contenido, preservando estructura, formatos y estilos.

## 🎯 Características Principales

### ✅ Extracción Completa y Fiel
- **TODO el contenido** se extrae, no solo propuestas específicas
- **Preserva estructura** completa: títulos, párrafos, tablas, listas
- **Mantiene formatos**: negritas, cursivas, subrayado, colores, fuentes, tamaños
- **Extrae imágenes** con datos binarios en base64
- **Respeta estilos**: alineación, rellenos, bordes, fusión de celdas

### 🚀 Optimizaciones Implementadas

1. **Procesadores Optimizados**
   - `processors/xlsx_processor_optimized.py` - Procesamiento completo de Excel
   - `processors/docx_processor_optimized.py` - Procesamiento completo de Word

2. **Extracción Inteligente**
   - **Método principal**: Lógica estructurada que busca patrones
   - **Fallback automático**: OpenAI solo cuando la lógica estructurada falla
   - **No ignora datos**: Procesa TODAS las apariciones, no solo la primera

3. **Rendimiento**
   - Procesamiento eficiente con iteradores
   - Manejo optimizado de memoria
   - Caché de estilos y formatos
   - Extracción paralela cuando es posible

## 📁 Estructura del Proyecto

```
solventacion-/
├── app.py                              # Aplicación Flask principal
├── config.py                           # Configuración centralizada
├── database.py                         # Gestión de BD SQLite
├── duplicate_detector.py               # Detección de duplicados
├── extractor_info.py                   # Extractor de ENTE y fuentes
├── processors/
│   ├── __init__.py
│   ├── docx_processor.py              # Procesador DOCX original
│   ├── docx_processor_optimized.py    # ✨ Procesador DOCX optimizado
│   ├── xlsx_processor.py              # Procesador XLSX original
│   └── xlsx_processor_optimized.py    # ✨ Procesador XLSX optimizado
├── uploads/                            # Archivos subidos
├── resultados/                         # Resultados JSON
├── templates/                          # Plantillas HTML
├── static/                            # Archivos estáticos
└── requirements.txt                    # Dependencias

```

## 🔧 Instalación

```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd solventacion-

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno (opcional)
cp .env.example .env
# Editar .env y agregar tu OPENAI_API_KEY si deseas el fallback a IA
```

## 🚀 Uso

### Iniciar el servidor

```bash
python app.py
```

El servidor estará disponible en `http://localhost:5023`

### Procesar archivos

1. Abre tu navegador en `http://localhost:5023`
2. Sube archivos DOCX o XLSX
3. El sistema procesará automáticamente:
   - Extraerá TODO el contenido
   - Buscará propuestas de solventación
   - Detectará duplicados
   - Generará JSON con resultados

### Resultado del procesamiento

Cada archivo procesado genera un JSON con:

```json
{
  "tipo_archivo": "DOCX/XLSX",
  "nombre_archivo": "documento.docx",
  "procesado_en": "2024-01-20T10:30:00",
  "metadatos": {
    "autor": "...",
    "titulo": "...",
    "fecha_creacion": "...",
    "imagenes": {
      "tiene_imagenes": true,
      "cantidad": 5,
      "detalles": [...]
    }
  },
  "estadisticas": {
    "total_propuestas": 10,
    "total_palabras": 5000,
    "metodo_extraccion_usado": "estructurado"
  },
  "contenido": {
    "documento_completo_html": "...",
    "propuestas": [
      {
        "numero": 1,
        "observacion_texto": "...",
        "observacion_html": "<p>...</p>",
        "propuesta_texto": "...",
        "propuesta_html": "<p><b>...</b></p>",
        "metodo_extraccion": "estructurado"
      }
    ]
  }
}
```

## 🧠 Lógica de Procesamiento

### XLSX (Excel)

1. **Extracción Estructurada** (método principal):
   - Lee todas las hojas del archivo
   - Busca patrones "OBSERVACIÓN" y "PROPUESTA DE SOLVENTACIÓN"
   - Extrae contenido con estilos (negritas, colores, rellenos)
   - Procesa celdas fusionadas correctamente
   - Extrae imágenes embebidas con posición y datos

2. **Fallback a OpenAI** (solo si falla):
   - Se activa cuando no se encuentran propuestas
   - Envía tabla HTML a GPT-4o-mini
   - Extrae propuestas usando IA
   - Marca método como "openai_fallback"

### DOCX (Word)

1. **Extracción Estructurada** (método principal):
   - Procesa documento completo preservando estructura
   - Busca en tablas (método principal)
   - Busca en párrafos (backup)
   - Extrae formatos: negritas, cursivas, subrayado, colores
   - Extrae tablas anidadas dentro de celdas
   - Extrae imágenes con datos binarios

2. **Fallback a OpenAI** (solo si falla):
   - Se activa cuando no se encuentran propuestas
   - Envía documento HTML a GPT-4o-mini
   - Extrae propuestas usando IA
   - Marca método como "openai_fallback"

## 📊 Mejoras vs Versión Original

| Característica | Original | Optimizado |
|----------------|----------|------------|
| Extracción de propuestas | ❌ Ignora primera aparición | ✅ Procesa todas |
| Contenido completo | ❌ Solo propuestas | ✅ TODO el documento |
| Formatos y estilos | ⚠️ Básico | ✅ Completo |
| Imágenes | ⚠️ Solo detección | ✅ Extracción con datos |
| Tablas anidadas | ❌ No soporta | ✅ Soporta |
| Celdas fusionadas | ⚠️ Parcial | ✅ Completo |
| Fallback a IA | ❌ No existe | ✅ Automático |
| Rendimiento | ⚠️ Estándar | ✅ Optimizado |

## 🔑 Configuración

Edita `config.py` para ajustar:

```python
# Usar procesadores optimizados
USE_OPTIMIZED_PROCESSORS = True

# Habilitar fallback a OpenAI (requiere API key)
ENABLE_OPENAI_FALLBACK = True

# Extraer contenido completo
EXTRACT_FULL_CONTENT = True

# Extraer imágenes
EXTRACT_IMAGES = True

# Preservar estilos
PRESERVE_STYLES = True
```

## 🔐 Variables de Entorno

Crea un archivo `.env`:

```bash
# OpenAI (opcional, solo para fallback)
OPENAI_API_KEY=sk-...

# Configuración
LOG_LEVEL=INFO
VERBOSE=True
```

## 📝 Notas Importantes

### Cuándo se usa OpenAI

OpenAI **SOLO** se usa como fallback cuando:
- La extracción estructurada no encuentra propuestas
- Hay errores en la lógica principal
- El usuario tiene `OPENAI_API_KEY` configurada

**No se usa OpenAI si**:
- La extracción estructurada funciona correctamente
- No hay API key configurada
- El usuario desactiva el fallback en `config.py`

### Rendimiento

- Archivos pequeños (<1MB): ~1-2 segundos
- Archivos medianos (1-5MB): ~3-5 segundos
- Archivos grandes (5-16MB): ~10-30 segundos

**Con fallback a OpenAI**: +2-5 segundos adicionales

### Límites

- Tamaño máximo: 16MB por archivo
- Formatos soportados: DOCX, XLSX
- Timeout: 5 minutos por archivo

## 🐛 Solución de Problemas

### Error: "OpenAI API key not configured"

**Solución**: Esto NO es un error crítico. OpenAI es opcional.
- Si tus archivos tienen estructura clara, no necesitas OpenAI
- Si quieres el fallback, agrega `OPENAI_API_KEY` en `.env`

### No se encuentran propuestas

**Causas posibles**:
1. El documento no tiene el texto "PROPUESTA DE SOLVENTACIÓN"
2. El formato es muy diferente al esperado

**Soluciones**:
1. Revisa que el documento tenga la estructura esperada
2. Configura OpenAI como fallback
3. Verifica el JSON de salida - puede tener el contenido completo

### Extracción lenta

**Soluciones**:
1. Reduce el tamaño de archivos
2. Desactiva extracción de imágenes si no las necesitas
3. Desactiva `EXTRACT_FULL_CONTENT` si solo necesitas propuestas

## 🔄 Migración desde versión anterior

Si ya usabas el sistema anterior:

1. Los procesadores originales siguen disponibles
2. Para volver a la versión original, edita `app.py`:

```python
# Descomentar estas líneas:
from processors.docx_processor import process_docx
from processors.xlsx_processor import process_xlsx

# Comentar estas:
# from processors.docx_processor_optimized import process_docx
# from processors.xlsx_processor_optimized import process_xlsx
```

## 📚 Dependencias

- Flask 3.0.0 - Framework web
- python-docx 1.1.0 - Procesamiento DOCX
- openpyxl 3.1.2 - Procesamiento XLSX
- pandas 2.3.3 - Manipulación de datos
- openai 1.12.0 - API de OpenAI (opcional)
- python-dotenv 1.0.0 - Variables de entorno

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

[Tu licencia aquí]

## 👨‍💻 Autor

Desarrollado por [Tu nombre]

---

**Versión**: 2.0.0 (Optimizada)
**Fecha**: Enero 2025
**Estado**: ✅ Producción
