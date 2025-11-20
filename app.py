"""
Solventación - Sistema de Procesamiento de Documentos
Procesa archivos DOCX y XLSX para extraer información institucional
"""

from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json
from pathlib import Path

# Módulos de procesamiento
# Usar procesadores optimizados por defecto (fallback a OpenAI incluido)
from processors.docx_processor_optimized import process_docx as process_docx_full
from processors.xlsx_processor_optimized import process_xlsx as process_xlsx_full

# Extractor minimalista (solo campos esenciales)
from processors.minimal_extractor import process_with_minimal

# Configuración: usar extractor minimalista por defecto
USE_MINIMAL_EXTRACTOR = True  # Cambiar a False para usar extractor completo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'solventacion-2024-secure-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['ALLOWED_EXTENSIONS'] = {'docx', 'xlsx'}

# Crear carpetas necesarias
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
Path('resultados').mkdir(exist_ok=True)

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    """Página principal con la interfaz de carga"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Procesa los archivos subidos"""
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

                if USE_MINIMAL_EXTRACTOR:
                    # Usar extractor minimalista (solo campos esenciales)
                    propuestas_data = process_with_minimal(filepath, ext.upper())

                    # Crear estructura compatible con frontend
                    data = {
                        'tipo_archivo': ext.upper(),
                        'nombre_archivo': filename,
                        'procesado_en': datetime.now().isoformat(),
                        'metodo_extraccion': 'minimal',
                        'estadisticas': {
                            'total_propuestas': propuestas_data.get('total', 0),
                            'metodo': propuestas_data.get('metodo', 'minimal_extractor')
                        },
                        'contenido': {
                            'propuestas': propuestas_data.get('propuestas', [])
                        },
                        'extraccion_exitosa': True
                    }
                else:
                    # Usar extractor completo (con todo el contenido)
                    if ext == 'docx':
                        data = process_docx_full(filepath)
                    elif ext == 'xlsx':
                        data = process_xlsx_full(filepath)

                # Guardar resultado
                result_filename = f"resultado_{timestamp}_{filename}.json"
                result_path = os.path.join('resultados', result_filename)

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
    """Descarga el archivo de resultados"""
    try:
        filepath = os.path.join('resultados', secure_filename(filename))
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/stats')
def get_stats():
    """Obtiene estadísticas de procesamiento"""
    try:
        uploads_count = len(os.listdir(app.config['UPLOAD_FOLDER']))
        results_count = len(os.listdir('resultados'))

        return jsonify({
            'total_uploads': uploads_count,
            'total_results': results_count,
            'last_update': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Solventación - Sistema de Procesamiento de Documentos")
    print("=" * 60)
    print(f"📂 Carpeta de uploads: {app.config['UPLOAD_FOLDER']}")
    print(f"📊 Carpeta de resultados: resultados")
    print(f"🌐 Puerto: 5023")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5023, debug=True)
