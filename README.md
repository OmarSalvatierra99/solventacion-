# 🚀 Solventación - Sistema Optimizado de Procesamiento de Documentos

Sistema inteligente de procesamiento de documentos DOCX y XLSX con extracción completa y fiel del contenido.

## ✨ Características Principales

- ✅ **Extracción completa** de TODO el contenido de los documentos
- ✅ **Preserva formatos**: negritas, cursivas, colores, estilos
- ✅ **Extrae imágenes** con datos binarios
- ✅ **Detecta duplicados** automáticamente
- ✅ **Fallback inteligente** a OpenAI solo cuando es necesario
- ✅ **Optimizado** para rendimiento máximo

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

Lee [Claude.md](./Claude.md) para documentación completa.

## 🎯 Uso Básico

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

Edita `config.py`:

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

- [Claude.md](./Claude.md) - Documentación completa y técnica
- [config.py](./config.py) - Opciones de configuración

## 🤝 Soporte

Para problemas o preguntas, revisa [Claude.md](./Claude.md) sección "Solución de Problemas".

---

**Versión**: 2.0.0 (Optimizada)
**Actualizado**: Enero 2025
