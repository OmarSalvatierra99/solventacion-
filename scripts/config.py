"""
Configuración del sistema de procesamiento de documentos
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ==============================
# CONFIGURACIÓN DE PROCESADORES
# ==============================

# Usar procesadores optimizados (recomendado)
# Los procesadores optimizados extraen TODO el contenido fielmente
# y solo usan OpenAI como fallback cuando la lógica estructurada falla
USE_OPTIMIZED_PROCESSORS = True

# ==============================
# CONFIGURACIÓN DE OPENAI
# ==============================

# OpenAI se usa SOLO como fallback cuando la extracción estructurada falla
# No es necesario si tus archivos tienen estructura clara
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
ENABLE_OPENAI_FALLBACK = bool(OPENAI_API_KEY)

# Modelo de OpenAI a usar (más barato y rápido)
OPENAI_MODEL = "gpt-4o-mini"

# ==============================
# CONFIGURACIÓN DE EXTRACCIÓN
# ==============================

# Extraer contenido completo de documentos (no solo propuestas)
EXTRACT_FULL_CONTENT = True

# Extraer imágenes en formato base64
EXTRACT_IMAGES = True

# Preservar formatos y estilos en HTML
PRESERVE_STYLES = True

# ==============================
# CONFIGURACIÓN DE RENDIMIENTO
# ==============================

# Tamaño máximo de archivo (16MB por defecto)
MAX_FILE_SIZE = 16 * 1024 * 1024

# Timeout para procesamiento de archivos grandes (segundos)
PROCESSING_TIMEOUT = 300

# Usar caché para resultados
USE_CACHE = False

# ==============================
# CONFIGURACIÓN DE BASE DE DATOS
# ==============================

# Detectar duplicados automáticamente
AUTO_DETECT_DUPLICATES = True

# Crear versiones automáticamente
AUTO_CREATE_VERSIONS = True

# ==============================
# CONFIGURACIÓN DE LOGGING
# ==============================

# Nivel de logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Mostrar información detallada de procesamiento
VERBOSE = os.getenv('VERBOSE', 'True').lower() == 'true'

# ==============================
# RUTAS
# ==============================

UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'resultados'
DATABASE_PATH = 'solventacion.db'
