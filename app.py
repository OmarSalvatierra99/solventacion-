"""
============================================================================
Solventación - Sistema de Procesamiento de Documentos
============================================================================

Aplicación web Flask para procesar archivos DOCX y XLSX.
Extrae propuestas de solventación, observaciones y metadatos institucionales.

Características:
- Extracción completa de contenido con estilos preservados
- Detección de propuestas de solventación y observaciones
- Análisis de metadatos del documento
- Exportación a JSON y CSV
- Interfaz web intuitiva con drag & drop

Autor: Sistema de Gestión Institucional
Última modificación: 2024
============================================================================
"""

# ============================================================================
# IMPORTACIONES
# ============================================================================
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json
from pathlib import Path

# Procesadores optimizados de documentos
from processors.docx_processor_optimized import process_docx
from processors.xlsx_processor_optimized import process_xlsx

# ============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ============================================================================
app = Flask(__name__)

# Configuración de seguridad y límites
app.config['SECRET_KEY'] = 'solventacion-2024-secure-key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB máximo por archivo

# Configuración de carpetas
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'resultados'
app.config['ALLOWED_EXTENSIONS'] = {'docx', 'xlsx'}

# Crear carpetas necesarias si no existen
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
Path(app.config['RESULTS_FOLDER']).mkdir(exist_ok=True)

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def allowed_file(filename):
    """
    Verifica si el archivo tiene una extensión permitida.

    Args:
        filename (str): Nombre del archivo a verificar

    Returns:
        bool: True si la extensión es permitida, False en caso contrario
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# ============================================================================
# RUTAS DE LA APLICACIÓN
# ============================================================================

@app.route('/')
def index():
    """
    Ruta principal de la aplicación.
    Muestra la interfaz de usuario para cargar documentos.
    """
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Procesa los archivos subidos por el usuario.

    Acepta múltiples archivos DOCX y XLSX, los procesa para extraer
    propuestas de solventación y otra información relevante.

    Returns:
        JSON con los resultados del procesamiento o error
    """
    try:
        if 'files[]' not in request.files:
            return jsonify({'error': 'No se enviaron archivos'}), 400

        files = request.files.getlist('files[]')
        results = []

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

                file.save(filepath)

                # Procesar según el tipo de archivo
                ext = filename.rsplit('.', 1)[1].lower()

                if ext == 'docx':
                    data = process_docx(filepath)
                elif ext == 'xlsx':
                    data = process_xlsx(filepath)

                # Guardar resultado en JSON
                result_filename = f"resultado_{timestamp}_{filename}.json"
                result_path = os.path.join(app.config['RESULTS_FOLDER'], result_filename)

                with open(result_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                results.append({
                    'filename': filename,
                    'status': 'success',
                    'data': data,
                    'result_file': result_filename
                })
            else:
                results.append({
                    'filename': file.filename if file else 'unknown',
                    'status': 'error',
                    'error': 'Tipo de archivo no permitido'
                })

        return jsonify({'results': results})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_result(filename):
    """
    Descarga un archivo de resultados JSON.

    Args:
        filename (str): Nombre del archivo a descargar

    Returns:
        El archivo JSON como descarga o error 404
    """
    try:
        filepath = os.path.join(app.config['RESULTS_FOLDER'], secure_filename(filename))
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@app.route('/api/stats')
def get_stats():
    """
    Obtiene estadísticas de uso de la aplicación.

    Returns:
        JSON con el total de archivos subidos, resultados generados y última actualización
    """
    try:
        uploads_count = len(os.listdir(app.config['UPLOAD_FOLDER']))
        results_count = len(os.listdir(app.config['RESULTS_FOLDER']))

        return jsonify({
            'total_uploads': uploads_count,
            'total_results': results_count,
            'last_update': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# PUNTO DE ENTRADA DE LA APLICACIÓN
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 Solventación - Sistema de Procesamiento de Documentos")
    print("=" * 70)
    print(f"📂 Carpeta de uploads:    {app.config['UPLOAD_FOLDER']}")
    print(f"📊 Carpeta de resultados: {app.config['RESULTS_FOLDER']}")
    print(f"📝 Formatos soportados:   {', '.join(app.config['ALLOWED_EXTENSIONS']).upper()}")
    print(f"⚙️  Tamaño máximo:         {app.config['MAX_CONTENT_LENGTH'] // (1024*1024)}MB")
    print(f"🌐 Puerto:                5023")
    print(f"🔗 URL:                   http://localhost:5023")
    print("=" * 70)
    print("✓ Servidor iniciado correctamente")
    print("  Presiona Ctrl+C para detener el servidor")
    print("=" * 70)

    app.run(host='0.0.0.0', port=5023, debug=True)
