# 🚀 Solventación - Sistema Optimizado de Procesamiento de Documentos

Sistema inteligente de procesamiento de documentos DOCX y XLSX con extracción completa y fiel del contenido. Incluye análisis por lotes, validación de imágenes y generación de base de datos consolidada.

## ✨ Características Principales

### Procesamiento de Documentos
- ✅ **Extracción completa** de TODO el contenido de los documentos
- ✅ **Preserva formatos**: negritas, cursivas, colores, estilos
- ✅ **Extrae imágenes** con datos binarios
- ✅ **Fallback inteligente** a OpenAI solo cuando es necesario
- ✅ **Optimizado** para rendimiento máximo

### Análisis Avanzado (NUEVO)
- 🆕 **Análisis por lotes** de múltiples archivos automáticamente
- 🆕 **Extracción de metadatos**: Ente, Fuente de Financiamiento, Periodo
- 🆕 **Validación de imágenes** en propuestas de solventación
- 🆕 **Base de datos consolidada** en Excel organizada por ente y financiamiento
- 🆕 **Reportes detallados** en JSON con estadísticas completas
- 🆕 **Histórico completo** de propuestas por ente y fuente

## 🔧 Instalación Rápida

```bash
# 1. Clonar repositorio
git clone <repository-url>
cd solventacion-

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Iniciar servidor
python app.py
```

Abre `http://localhost:5023` en tu navegador.

## 📖 Documentación Completa

Lee [docs/Claude.md](./docs/Claude.md) para documentación completa.

## 🎯 Modos de Uso

### Modo 1: Procesamiento por Lotes (Recomendado) 🆕

Procesa automáticamente todos los archivos de una carpeta y genera base de datos consolidada:

```bash
python scripts/batch_processor.py --entrada examples --salida resultados_consolidados
```

**Salidas generadas:**
- 📊 Base de datos consolidada en Excel
- 📋 Reporte de imágenes en propuestas
- 📈 Estadísticas de procesamiento
- 📁 Resultados individuales en JSON

### Modo 2: Interfaz Web

Para procesamiento individual con interfaz gráfica:

```bash
python app.py
```

Abre `http://localhost:5023` en tu navegador y:
1. Sube archivos DOCX o XLSX
2. El sistema extrae automáticamente:
   - Propuestas de solventación
   - Contenido completo con formatos
   - Imágenes embebidas
   - Metadatos del documento
3. Descarga resultados en JSON

## 🧠 Métodos de Extracción

### Método Principal: Lógica Estructurada
- Busca patrones específicos en el documento
- Extrae propuestas con su estructura
- Preserva formatos y estilos
- **No requiere OpenAI**

### Fallback: OpenAI (Opcional)
- Se activa SOLO si la lógica estructurada falla
- Requiere `OPENAI_API_KEY` en `.env`
- Usa GPT-4o-mini (más barato y rápido)

## ⚙️ Configuración

Edita `scripts/config.py`:

```python
USE_OPTIMIZED_PROCESSORS = True      # Usar versión optimizada
ENABLE_OPENAI_FALLBACK = True        # Fallback a OpenAI (opcional)
EXTRACT_FULL_CONTENT = True          # Extraer TODO el contenido
EXTRACT_IMAGES = True                # Extraer imágenes
PRESERVE_STYLES = True               # Preservar formatos
```

## 📊 Comparación con Versión Original

| Característica | Original | Optimizado |
|----------------|----------|------------|
| Extrae todas las propuestas | ❌ | ✅ |
| Contenido completo | ❌ | ✅ |
| Formatos completos | ⚠️ | ✅ |
| Imágenes con datos | ❌ | ✅ |
| Fallback inteligente | ❌ | ✅ |
| Optimizado | ⚠️ | ✅ |

## 🔐 Variables de Entorno (Opcionales)

Crea `.env`:

```bash
# Solo necesario si quieres fallback a OpenAI
OPENAI_API_KEY=sk-...

# Opcional
LOG_LEVEL=INFO
VERBOSE=True
```

## 📝 Ejemplo de Resultado

```json
{
  "tipo_archivo": "DOCX",
  "metadatos": {
    "autor": "Juan Pérez",
    "total_palabras": 5000,
    "imagenes": {
      "cantidad": 3,
      "detalles": [...]
    }
  },
  "contenido": {
    "documento_completo_html": "<html>...</html>",
    "propuestas": [
      {
        "numero": 1,
        "observacion_html": "<p><b>Observación...</b></p>",
        "propuesta_html": "<p>Propuesta...</p>",
        "metodo_extraccion": "estructurado"
      }
    ]
  }
}
```

## 🚨 Notas Importantes

### OpenAI es OPCIONAL
- El sistema funciona perfectamente SIN OpenAI
- OpenAI solo se usa como fallback cuando falla la lógica principal
- Si no configuras API key, todo funciona igual (sin fallback)

### Rendimiento
- Archivos <1MB: ~1-2 segundos
- Archivos 1-5MB: ~3-5 segundos
- Archivos 5-16MB: ~10-30 segundos

## 📚 Documentación

- **[docs/GUIA_USO.md](./GUIA_USO.md)** - Guía completa de uso del sistema 🆕
- **[docs/ARQUITECTURA.md](./ARQUITECTURA.md)** - Arquitectura y diseño del sistema 🆕
- **[docs/Claude.md](./Claude.md)** - Documentación técnica completa
- **[scripts/config.py](../scripts/config.py)** - Opciones de configuración

## 🏗️ Arquitectura Modular

El sistema está diseñado con una arquitectura modular clara y organizada:

```
solventacion-/
├── docs/                            # 📚 Documentación
│   ├── README.md                    # Este archivo
│   ├── GUIA_USO.md                  # Guía de uso completa
│   ├── ARQUITECTURA.md              # Documentación de arquitectura
│   └── Claude.md                    # Documentación técnica
│
├── scripts/                         # 🔧 Scripts del sistema
│   ├── batch_processor.py           # Procesamiento por lotes 🆕
│   ├── database_consolidator.py     # Base de datos consolidada
│   ├── metadata_analyzer.py         # Análisis de metadatos
│   ├── image_validator.py           # Validación de imágenes
│   ├── database.py                  # Gestión de base de datos
│   ├── duplicate_detector.py        # Detección de duplicados
│   ├── extractor_info.py            # Extracción de información
│   └── config.py                    # Configuración del sistema
│
├── processors/                      # 📄 Procesadores de documentos
│   ├── docx_processor_optimized.py # Procesamiento DOCX optimizado
│   └── xlsx_processor_optimized.py # Procesamiento XLSX optimizado
│
├── static/                          # 🎨 Recursos frontend
│   ├── css/styles.css               # Estilos minimalistas tipo Notion
│   ├── js/app.js                    # Lógica de la interfaz
│   └── img/logo.svg                 # Logo institucional
│
├── templates/                       # 📋 Templates HTML
│   └── index.html                   # Interfaz principal
│
├── examples/                        # 📁 Documentos de ejemplo
│   └── *.docx, *.xlsx              # Archivos de prueba
│
├── app.py                          # 🚀 Servidor Flask (punto de entrada)
├── requirements.txt                # 📦 Dependencias Python
└── .env.example                    # ⚙️ Variables de entorno ejemplo
```

## 🎨 Características Técnicas

### Extracción de Información Clave
- **Ente**: FIDECIX, SEPUEDE, etc.
- **Fuente de Financiamiento**: SA, PEFCF, R, PRAS, PDP, REA
- **Periodo**: ENE_JUN, ENE_ENE, etc.
- **Tipo de Documento**: RRyPE, REA, etc.

### Validación de Contenido
- Detecta imágenes en sección "PROPUESTA DE SOLVENTACIÓN"
- Reporta archivos con imágenes para revisión manual
- Extrae ubicación exacta de imágenes detectadas

### Base de Datos Consolidada
- Organizada por Ente y Fuente de Financiamiento
- Múltiples hojas en Excel para fácil navegación
- Histórico completo de propuestas
- Estadísticas y resúmenes automáticos

## 🤝 Soporte

Para problemas o preguntas:
- Guía de uso: [docs/GUIA_USO.md](./GUIA_USO.md)
- Arquitectura: [docs/ARQUITECTURA.md](./ARQUITECTURA.md)
- Documentación técnica: [docs/Claude.md](./Claude.md)

---

**Versión**: 3.0.0 (Análisis por Lotes + Consolidación)
**Actualizado**: Noviembre 2025
