// ============================================
// Solventación - JavaScript Principal
// Sistema de Procesamiento de Documentos
// ============================================

// Estado de la aplicación
const state = {
    files: [],
    results: []
};

// ============================================
// Inicialización
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    loadStats();
    setInterval(loadStats, 30000); // Actualizar stats cada 30 segundos
});

function initializeApp() {
    // Elementos del DOM
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const clearBtn = document.getElementById('clearBtn');

    // Event Listeners - Drop Zone
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);
    dropZone.addEventListener('click', () => fileInput.click());

    // Event Listeners - File Input
    fileInput.addEventListener('change', handleFileSelect);

    // Event Listeners - Buttons
    uploadBtn.addEventListener('click', uploadFiles);
    clearBtn.addEventListener('click', clearFiles);

    console.log('✓ Aplicación inicializada correctamente');
}

// ============================================
// Manejo de Drag & Drop
// ============================================
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('drag-over');

    const files = Array.from(e.dataTransfer.files);
    addFiles(files);
}

function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    addFiles(files);
}

// ============================================
// Gestión de Archivos
// ============================================
function addFiles(files) {
    const validFiles = files.filter(file => {
        const ext = file.name.split('.').pop().toLowerCase();
        if (!['docx', 'xlsx'].includes(ext)) {
            showNotification(`Archivo no válido: ${file.name}`, 'error');
            return false;
        }
        if (file.size > 16 * 1024 * 1024) {
            showNotification(`Archivo demasiado grande: ${file.name}`, 'error');
            return false;
        }
        return true;
    });

    state.files.push(...validFiles);
    updateFilesList();
    showUploadActions();
}

function removeFile(index) {
    state.files.splice(index, 1);
    updateFilesList();

    if (state.files.length === 0) {
        hideUploadActions();
    }
}

function clearFiles() {
    state.files = [];
    updateFilesList();
    hideUploadActions();
}

function updateFilesList() {
    const filesList = document.getElementById('filesList');

    if (state.files.length === 0) {
        filesList.innerHTML = '';
        return;
    }

    filesList.innerHTML = state.files.map((file, index) => {
        const ext = file.name.split('.').pop().toLowerCase();
        const icon = ext === 'docx' ? 'fa-file-word' : 'fa-file-excel';
        const size = formatFileSize(file.size);

        return `
            <div class="file-item">
                <div class="file-info">
                    <i class="fas ${icon} file-icon ${ext}"></i>
                    <div class="file-details">
                        <h4>${file.name}</h4>
                        <span class="file-size">${size}</span>
                    </div>
                </div>
                <button class="file-remove" onclick="removeFile(${index})">
                    <i class="fas fa-trash"></i> Eliminar
                </button>
            </div>
        `;
    }).join('');
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// ============================================
// Upload de Archivos
// ============================================
async function uploadFiles() {
    if (state.files.length === 0) {
        showNotification('No hay archivos para procesar', 'warning');
        return;
    }

    const formData = new FormData();
    state.files.forEach(file => {
        formData.append('files[]', file);
    });

    showProgress();

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Error en el servidor');
        }

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        state.results = data.results;
        displayResults();
        clearFiles();
        hideProgress();
        showNotification('Archivos procesados exitosamente', 'success');
        loadStats();

    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al procesar archivos: ' + error.message, 'error');
        hideProgress();
    }
}

// ============================================
// Mostrar Resultados
// ============================================
function displayResults() {
    const resultsSection = document.getElementById('resultsSection');
    const resultsGrid = document.getElementById('resultsGrid');

    if (state.results.length === 0) {
        resultsSection.style.display = 'none';
        return;
    }

    resultsSection.style.display = 'block';

    // Recopilar todas las propuestas de todos los archivos
    const todasLasPropuestas = [];

    state.results.forEach((result, resultIndex) => {
        if (result.status === 'success' && result.data?.contenido?.propuestas) {
            result.data.contenido.propuestas.forEach((propuesta) => {
                todasLasPropuestas.push({
                    ...propuesta,
                    archivo: result.filename,
                    resultIndex: resultIndex,
                    metadatos: result.data.metadatos
                });
            });
        }
    });

    // Mostrar todas las propuestas en tarjetas individuales
    if (todasLasPropuestas.length > 0) {
        resultsGrid.innerHTML = `
            <div class="propuestas-header">
                <h2><i class="fas fa-file-alt"></i> Propuestas de Solventación Extraídas (${todasLasPropuestas.length})</h2>
                <div class="propuestas-actions">
                    <button class="btn btn-success" onclick="exportToCSV()">
                        <i class="fas fa-file-csv"></i> Exportar todo a CSV
                    </button>
                    <button class="btn btn-info" onclick="copiarTodasPropuestas()">
                        <i class="fas fa-copy"></i> Copiar todas
                    </button>
                </div>
            </div>
            ${todasLasPropuestas.map((propuesta, index) => createPropuestaCard(propuesta, index)).join('')}
        `;
    } else {
        // Si no hay propuestas, mostrar resumen de archivos
        resultsGrid.innerHTML = state.results.map((result, index) => {
            if (result.status === 'error' || result.data?.error) {
                return createErrorCard(result);
            }
            return createFileInfoCard(result, index);
        }).join('') + `
            <div class="no-propuestas-warning">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>No se encontraron propuestas de solventación</h3>
                <p>Los archivos fueron procesados correctamente, pero no se encontraron propuestas con el formato esperado.</p>
            </div>
        `;
    }

    // Scroll suave a resultados
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function createPropuestaCard(propuesta, index) {
    const observacionTexto = stripHtmlTags(propuesta.observacion);
    const propuestaTexto = stripHtmlTags(propuesta.propuesta_html);

    return `
        <div class="propuesta-card" id="propuesta-${index}">
            <div class="propuesta-header">
                <div class="propuesta-numero">
                    <i class="fas fa-hashtag"></i>
                    <span>Propuesta ${propuesta.numero}</span>
                </div>
                <div class="propuesta-archivo-info">
                    <i class="fas fa-file"></i>
                    <span>${propuesta.archivo}</span>
                    ${propuesta.hoja ? `<span class="propuesta-hoja"><i class="fas fa-table"></i> ${propuesta.hoja}</span>` : ''}
                </div>
            </div>

            <div class="propuesta-metadata">
                <div class="metadata-item">
                    <i class="fas fa-user"></i>
                    <span>Autor: ${propuesta.metadatos?.autor || 'Desconocido'}</span>
                </div>
                <div class="metadata-item">
                    <i class="fas fa-user-edit"></i>
                    <span>Modificado por: ${propuesta.metadatos?.ultima_modificacion_por || 'Desconocido'}</span>
                </div>
                <div class="metadata-item">
                    <i class="fas fa-calendar"></i>
                    <span>Fecha: ${propuesta.metadatos?.fecha_modificacion ? new Date(propuesta.metadatos.fecha_modificacion).toLocaleDateString('es-MX') : 'N/A'}</span>
                </div>
            </div>

            ${observacionTexto !== 'Sin observación' ? `
                <div class="propuesta-observacion">
                    <h4><i class="fas fa-exclamation-circle"></i> Observación</h4>
                    <div class="observacion-content">${propuesta.observacion}</div>
                </div>
            ` : ''}

            <div class="propuesta-contenido">
                <div class="propuesta-contenido-header">
                    <h4><i class="fas fa-clipboard-check"></i> Propuesta de Solventación</h4>
                    <button class="btn btn-primary btn-small" onclick="copiarPropuesta(${index})" title="Copiar propuesta">
                        <i class="fas fa-copy"></i> Copiar
                    </button>
                </div>
                <div class="propuesta-texto" id="propuesta-texto-${index}">
                    ${propuesta.propuesta_html}
                </div>
            </div>
        </div>
    `;
}

function createFileInfoCard(result, index) {
    const ext = result.filename.split('.').pop().toLowerCase();
    const icon = ext === 'docx' ? 'fa-file-word' : 'fa-file-excel';
    const iconColor = ext === 'docx' ? '#2b5797' : '#217346';

    return `
        <div class="result-card">
            <div class="result-header">
                <i class="fas ${icon} result-icon" style="color: ${iconColor}"></i>
                <div class="result-title">
                    <h3>${result.filename}</h3>
                    <span class="result-type">${result.data.tipo_archivo}</span>
                </div>
            </div>
            <div class="result-body">
                ${createResultSummary(result.data)}
            </div>
            <div class="result-actions">
                <button class="btn btn-primary btn-small" onclick="showDetails(${index})">
                    <i class="fas fa-eye"></i> Ver Detalles
                </button>
                <button class="btn btn-success btn-small" onclick="downloadResult('${result.result_file}')">
                    <i class="fas fa-download"></i> Descargar JSON
                </button>
            </div>
        </div>
    `;
}

function createResultSummary(data) {
    // Verificar si hay un error en los datos
    if (data.error || !data.estadisticas || !data.metadatos) {
        return `
            <div class="result-stat" style="color: var(--error)">
                <span>Error:</span>
                <strong>${data.error || 'Datos incompletos'}</strong>
            </div>
        `;
    }

    if (data.tipo_archivo === 'DOCX') {
        return `
            <div class="result-stat">
                <span>Párrafos:</span>
                <strong>${data.estadisticas.total_parrafos || 0}</strong>
            </div>
            <div class="result-stat">
                <span>Palabras:</span>
                <strong>${data.estadisticas.total_palabras || 0}</strong>
            </div>
            <div class="result-stat">
                <span>Tablas:</span>
                <strong>${data.estadisticas.total_tablas || 0}</strong>
            </div>
            <div class="result-stat">
                <span>Propuestas:</span>
                <strong>${data.estadisticas.total_propuestas || 0}</strong>
            </div>
            <div class="result-stat">
                <span>Autor:</span>
                <strong>${data.metadatos.autor || 'Desconocido'}</strong>
            </div>
        `;
    } else if (data.tipo_archivo === 'XLSX') {
        return `
            <div class="result-stat">
                <span>Hojas:</span>
                <strong>${data.metadatos.total_hojas || 0}</strong>
            </div>
            <div class="result-stat">
                <span>Celdas con datos:</span>
                <strong>${data.estadisticas.total_celdas_con_datos || 0}</strong>
            </div>
            <div class="result-stat">
                <span>Fórmulas:</span>
                <strong>${data.estadisticas.total_formulas || 0}</strong>
            </div>
            <div class="result-stat">
                <span>Propuestas:</span>
                <strong>${data.estadisticas.total_propuestas || 0}</strong>
            </div>
            <div class="result-stat">
                <span>Autor:</span>
                <strong>${data.metadatos.autor || 'Desconocido'}</strong>
            </div>
        `;
    }
    return '';
}

function createErrorCard(result) {
    return `
        <div class="result-card" style="border-color: var(--error)">
            <div class="result-header">
                <i class="fas fa-exclamation-circle result-icon" style="color: var(--error)"></i>
                <div class="result-title">
                    <h3>${result.filename}</h3>
                    <span class="result-type" style="background: rgba(239, 68, 68, 0.2); color: var(--error)">ERROR</span>
                </div>
            </div>
            <div class="result-body">
                <p style="color: var(--error)">${result.error}</p>
            </div>
        </div>
    `;
}

// ============================================
// Modal de Detalles
// ============================================
function showDetails(index) {
    const result = state.results[index];
    const modal = document.getElementById('detailsModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');

    modalTitle.textContent = `Detalles: ${result.filename}`;
    modalBody.innerHTML = createDetailedView(result.data);

    modal.classList.add('active');
}

function closeModal() {
    const modal = document.getElementById('detailsModal');
    modal.classList.remove('active');
}

function createDetailedView(data) {
    let html = '<div style="color: var(--text-primary)">';

    // Verificar si hay error
    if (data.error) {
        html += `<div style="color: var(--error); padding: 2rem; text-align: center;">
            <i class="fas fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 1rem;"></i>
            <h3>Error al procesar el archivo</h3>
            <p>${data.error}</p>
        </div>`;
        html += '</div>';
        return html;
    }

    // Metadatos
    if (data.metadatos && Object.keys(data.metadatos).length > 0) {
        html += '<h4 style="color: var(--primary-light); margin-bottom: 1rem;">Metadatos</h4>';
        html += '<table style="width: 100%; margin-bottom: 2rem; border-collapse: collapse;">';
        for (const [key, value] of Object.entries(data.metadatos)) {
            html += `
                <tr style="border-bottom: 1px solid rgba(59, 130, 246, 0.1);">
                    <td style="padding: 0.5rem; color: var(--text-secondary)">${key}:</td>
                    <td style="padding: 0.5rem; color: var(--text-primary); font-weight: 500">${value || 'N/A'}</td>
                </tr>
            `;
        }
        html += '</table>';
    }

    // Estadísticas
    if (data.estadisticas && Object.keys(data.estadisticas).length > 0) {
        html += '<h4 style="color: var(--primary-light); margin-bottom: 1rem;">Estadísticas</h4>';
        html += '<table style="width: 100%; margin-bottom: 2rem; border-collapse: collapse;">';
        for (const [key, value] of Object.entries(data.estadisticas)) {
            html += `
                <tr style="border-bottom: 1px solid rgba(59, 130, 246, 0.1);">
                    <td style="padding: 0.5rem; color: var(--text-secondary)">${key}:</td>
                    <td style="padding: 0.5rem; color: var(--text-primary); font-weight: 500">${JSON.stringify(value)}</td>
                </tr>
            `;
        }
        html += '</table>';
    }

    // Contenido específico
    if (data.tipo_archivo === 'DOCX' && data.contenido?.titulos?.length > 0) {
        html += '<h4 style="color: var(--primary-light); margin-bottom: 1rem;">Títulos</h4>';
        html += '<ul style="list-style: none; padding: 0; margin-bottom: 2rem;">';
        data.contenido.titulos.forEach(titulo => {
            html += `<li style="padding: 0.5rem; margin-bottom: 0.5rem; background: rgba(59, 130, 246, 0.05); border-radius: 8px;">
                <strong>Nivel ${titulo.nivel}:</strong> ${titulo.texto}
            </li>`;
        });
        html += '</ul>';
    }

    if (data.tipo_archivo === 'XLSX' && data.metadatos?.nombres_hojas) {
        html += '<h4 style="color: var(--primary-light); margin-bottom: 1rem;">Hojas</h4>';
        html += '<ul style="list-style: none; padding: 0;">';
        data.metadatos.nombres_hojas.forEach(hoja => {
            html += `<li style="padding: 0.5rem; margin-bottom: 0.5rem; background: rgba(59, 130, 246, 0.05); border-radius: 8px;">
                <i class="fas fa-table"></i> ${hoja}
            </li>`;
        });
        html += '</ul>';
    }

    html += '</div>';
    return html;
}

// ============================================
// Copiar al Portapapeles
// ============================================
async function copiarPropuesta(index) {
    try {
        const propuestaElement = document.getElementById(`propuesta-texto-${index}`);
        if (!propuestaElement) {
            throw new Error('Propuesta no encontrada');
        }

        // Obtener el texto sin las etiquetas HTML
        const texto = stripHtmlTags(propuestaElement.innerHTML);

        // Copiar al portapapeles
        await navigator.clipboard.writeText(texto);

        // Notificación de éxito
        showNotification('Propuesta copiada al portapapeles', 'success');

        // Efecto visual en el botón
        const buttons = document.querySelectorAll(`#propuesta-${index} .btn-primary`);
        buttons.forEach(btn => {
            const originalHTML = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-check"></i> ¡Copiado!';
            btn.style.backgroundColor = 'var(--success)';

            setTimeout(() => {
                btn.innerHTML = originalHTML;
                btn.style.backgroundColor = '';
            }, 2000);
        });

    } catch (error) {
        console.error('Error al copiar:', error);
        showNotification('Error al copiar al portapapeles', 'error');
    }
}

async function copiarTodasPropuestas() {
    try {
        // Recopilar todas las propuestas
        const todasPropuestas = [];

        state.results.forEach(result => {
            if (result.status === 'success' && result.data?.contenido?.propuestas) {
                result.data.contenido.propuestas.forEach(propuesta => {
                    const observacion = stripHtmlTags(propuesta.observacion);
                    const propuestaTexto = stripHtmlTags(propuesta.propuesta_html);

                    todasPropuestas.push(
                        `=================================================\n` +
                        `PROPUESTA ${propuesta.numero}\n` +
                        `Archivo: ${result.filename}\n` +
                        `${propuesta.hoja ? `Hoja: ${propuesta.hoja}\n` : ''}` +
                        `=================================================\n\n` +
                        `OBSERVACIÓN:\n${observacion}\n\n` +
                        `PROPUESTA DE SOLVENTACIÓN:\n${propuestaTexto}\n\n`
                    );
                });
            }
        });

        if (todasPropuestas.length === 0) {
            showNotification('No hay propuestas para copiar', 'warning');
            return;
        }

        const textoCompleto = todasPropuestas.join('\n');
        await navigator.clipboard.writeText(textoCompleto);

        showNotification(`${todasPropuestas.length} propuestas copiadas al portapapeles`, 'success');

    } catch (error) {
        console.error('Error al copiar:', error);
        showNotification('Error al copiar al portapapeles', 'error');
    }
}

// ============================================
// Descarga de Resultados
// ============================================
function downloadResult(filename) {
    window.location.href = `/download/${filename}`;
    showNotification('Descargando resultado...', 'info');
}

function exportToCSV() {
    if (state.results.length === 0) {
        showNotification('No hay resultados para exportar', 'warning');
        return;
    }

    // Recopilar todas las propuestas de todos los archivos procesados
    const todasPropuestas = [];

    state.results.forEach(result => {
        if (result.status === 'success' && result.data?.contenido?.propuestas) {
            result.data.contenido.propuestas.forEach(propuesta => {
                todasPropuestas.push({
                    archivo: result.filename,
                    numero: propuesta.numero,
                    observacion: stripHtmlTags(propuesta.observacion),
                    propuesta: stripHtmlTags(propuesta.propuesta_html),
                    hoja: propuesta.hoja || 'N/A'
                });
            });
        }
    });

    if (todasPropuestas.length === 0) {
        showNotification('No hay propuestas para exportar', 'warning');
        return;
    }

    // Crear CSV
    const headers = ['Archivo', 'Número', 'Observación', 'Propuesta de Solventación', 'Hoja'];
    const csvRows = [headers.join(',')];

    todasPropuestas.forEach(prop => {
        const row = [
            escapeCsvValue(prop.archivo),
            prop.numero,
            escapeCsvValue(prop.observacion),
            escapeCsvValue(prop.propuesta),
            escapeCsvValue(prop.hoja)
        ];
        csvRows.push(row.join(','));
    });

    const csvContent = csvRows.join('\n');
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', `solventacion_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showNotification(`CSV exportado con ${todasPropuestas.length} propuestas`, 'success');
}

function stripHtmlTags(html) {
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    return tmp.textContent || tmp.innerText || '';
}

function escapeCsvValue(value) {
    if (value === null || value === undefined) return '';
    const stringValue = String(value);
    // Escapar comillas dobles y envolver en comillas si contiene comas, saltos de línea o comillas
    if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
        return '"' + stringValue.replace(/"/g, '""') + '"';
    }
    return stringValue;
}

// ============================================
// Estadísticas
// ============================================
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        document.getElementById('totalUploads').textContent = data.total_uploads;
        document.getElementById('totalResults').textContent = data.total_results;
    } catch (error) {
        console.error('Error al cargar estadísticas:', error);
    }
}

// ============================================
// UI Helpers
// ============================================
function showUploadActions() {
    document.getElementById('uploadActions').style.display = 'flex';
}

function hideUploadActions() {
    document.getElementById('uploadActions').style.display = 'none';
}

function showProgress() {
    const progressContainer = document.getElementById('progressContainer');
    const progressFill = document.getElementById('progressFill');

    progressContainer.style.display = 'block';
    progressFill.style.width = '0%';

    // Simulación de progreso
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 30;
        if (progress > 90) progress = 90;
        progressFill.style.width = progress + '%';
    }, 300);

    progressContainer.dataset.interval = interval;
}

function hideProgress() {
    const progressContainer = document.getElementById('progressContainer');
    const progressFill = document.getElementById('progressFill');
    const interval = progressContainer.dataset.interval;

    if (interval) {
        clearInterval(parseInt(interval));
    }

    progressFill.style.width = '100%';

    setTimeout(() => {
        progressContainer.style.display = 'none';
        progressFill.style.width = '0%';
    }, 500);
}

function showNotification(message, type = 'info') {
    // Crear notificación
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? 'var(--success)' : type === 'error' ? 'var(--error)' : type === 'warning' ? 'var(--warning)' : 'var(--info)'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-xl);
        z-index: 10000;
        animation: slideIn 0.3s ease;
        max-width: 400px;
    `;

    const icon = type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : type === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle';

    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <i class="fas ${icon}"></i>
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(notification);

    // Eliminar después de 3 segundos
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Animaciones de notificaciones
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Cerrar modal con ESC
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
    }
});

// Cerrar modal al hacer clic fuera
document.getElementById('detailsModal').addEventListener('click', (e) => {
    if (e.target.id === 'detailsModal') {
        closeModal();
    }
});

console.log('🚀 Sistema de Solventación iniciado correctamente');
