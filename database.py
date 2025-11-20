"""
Base de datos para gestión de propuestas de solventación
Maneja ENTES, fuentes de financiamiento, propuestas y versiones
"""

import sqlite3
import hashlib
import json
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager


class Database:
    """Gestor de base de datos SQLite para propuestas de solventación"""

    def __init__(self, db_path='solventacion.db'):
        self.db_path = db_path
        self.init_database()

    @contextmanager
    def get_connection(self):
        """Context manager para conexiones de base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def init_database(self):
        """Inicializa las tablas de la base de datos"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Tabla de ENTES
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS entes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    descripcion TEXT,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Tabla de fuentes de financiamiento
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fuentes_financiamiento (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    descripcion TEXT,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Tabla principal de propuestas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS propuestas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ente_id INTEGER NOT NULL,
                    fuente_financiamiento_id INTEGER NOT NULL,
                    numero INTEGER NOT NULL,
                    observacion_texto TEXT,
                    propuesta_texto TEXT NOT NULL,
                    observacion_html TEXT,
                    propuesta_html TEXT NOT NULL,
                    archivo_origen TEXT,
                    tipo_archivo TEXT,
                    hoja_origen TEXT,
                    hash_contenido TEXT UNIQUE NOT NULL,
                    version_actual INTEGER DEFAULT 1,
                    es_duplicado BOOLEAN DEFAULT 0,
                    propuesta_original_id INTEGER,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ente_id) REFERENCES entes(id),
                    FOREIGN KEY (fuente_financiamiento_id) REFERENCES fuentes_financiamiento(id),
                    FOREIGN KEY (propuesta_original_id) REFERENCES propuestas(id)
                )
            ''')

            # Índices para búsqueda rápida
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_propuestas_hash
                ON propuestas(hash_contenido)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_propuestas_ente
                ON propuestas(ente_id)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_propuestas_fuente
                ON propuestas(fuente_financiamiento_id)
            ''')

            # Tabla de versiones de propuestas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS versiones_propuestas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    propuesta_id INTEGER NOT NULL,
                    version INTEGER NOT NULL,
                    observacion_texto TEXT,
                    propuesta_texto TEXT NOT NULL,
                    observacion_html TEXT,
                    propuesta_html TEXT NOT NULL,
                    motivo_cambio TEXT,
                    hash_contenido TEXT NOT NULL,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (propuesta_id) REFERENCES propuestas(id),
                    UNIQUE(propuesta_id, version)
                )
            ''')

            # Tabla de estadísticas de procesamiento
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS estadisticas_procesamiento (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo_archivo TEXT,
                    archivo_nombre TEXT,
                    total_propuestas INTEGER,
                    duplicados_detectados INTEGER,
                    versiones_creadas INTEGER,
                    fecha_procesamiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def get_or_create_ente(self, nombre, descripcion=None):
        """Obtiene o crea un ENTE"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Buscar existente
            cursor.execute('SELECT id FROM entes WHERE nombre = ?', (nombre,))
            row = cursor.fetchone()

            if row:
                return row[0]

            # Crear nuevo
            cursor.execute(
                'INSERT INTO entes (nombre, descripcion) VALUES (?, ?)',
                (nombre, descripcion)
            )
            return cursor.lastrowid

    def get_or_create_fuente(self, nombre, descripcion=None):
        """Obtiene o crea una fuente de financiamiento"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Buscar existente
            cursor.execute('SELECT id FROM fuentes_financiamiento WHERE nombre = ?', (nombre,))
            row = cursor.fetchone()

            if row:
                return row[0]

            # Crear nuevo
            cursor.execute(
                'INSERT INTO fuentes_financiamiento (nombre, descripcion) VALUES (?, ?)',
                (nombre, descripcion)
            )
            return cursor.lastrowid

    def calcular_hash(self, observacion_texto, propuesta_texto):
        """Calcula hash único para detectar duplicados"""
        contenido = f"{observacion_texto}||{propuesta_texto}"
        return hashlib.sha256(contenido.encode('utf-8')).hexdigest()

    def buscar_propuesta_existente(self, hash_contenido, ente_id, fuente_id):
        """Busca una propuesta existente por hash, ente y fuente"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, version_actual, propuesta_texto, observacion_texto,
                       propuesta_html, observacion_html
                FROM propuestas
                WHERE hash_contenido = ? AND ente_id = ? AND fuente_financiamiento_id = ?
            ''', (hash_contenido, ente_id, fuente_id))

            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'version_actual': row[1],
                    'propuesta_texto': row[2],
                    'observacion_texto': row[3],
                    'propuesta_html': row[4],
                    'observacion_html': row[5]
                }
            return None

    def insertar_propuesta(self, ente_id, fuente_id, numero, observacion_texto,
                          propuesta_texto, observacion_html, propuesta_html,
                          archivo_origen, tipo_archivo, hoja_origen=None):
        """Inserta una nueva propuesta"""
        hash_contenido = self.calcular_hash(observacion_texto or '', propuesta_texto)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO propuestas (
                    ente_id, fuente_financiamiento_id, numero,
                    observacion_texto, propuesta_texto,
                    observacion_html, propuesta_html,
                    archivo_origen, tipo_archivo, hoja_origen,
                    hash_contenido, version_actual
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            ''', (ente_id, fuente_id, numero, observacion_texto, propuesta_texto,
                  observacion_html, propuesta_html, archivo_origen, tipo_archivo,
                  hoja_origen, hash_contenido))

            propuesta_id = cursor.lastrowid

            # Crear primera versión
            self.crear_version(propuesta_id, 1, observacion_texto, propuesta_texto,
                              observacion_html, propuesta_html, hash_contenido,
                              "Versión inicial")

            return propuesta_id

    def marcar_como_duplicado(self, propuesta_id, propuesta_original_id):
        """Marca una propuesta como duplicado"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE propuestas
                SET es_duplicado = 1, propuesta_original_id = ?
                WHERE id = ?
            ''', (propuesta_original_id, propuesta_id))

    def crear_version(self, propuesta_id, version, observacion_texto, propuesta_texto,
                     observacion_html, propuesta_html, hash_contenido, motivo_cambio):
        """Crea una nueva versión de una propuesta"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO versiones_propuestas (
                    propuesta_id, version, observacion_texto, propuesta_texto,
                    observacion_html, propuesta_html, hash_contenido, motivo_cambio
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (propuesta_id, version, observacion_texto, propuesta_texto,
                  observacion_html, propuesta_html, hash_contenido, motivo_cambio))

    def actualizar_propuesta_con_version(self, propuesta_id, observacion_texto,
                                        propuesta_texto, observacion_html,
                                        propuesta_html, motivo_cambio="Actualización"):
        """Actualiza una propuesta creando una nueva versión"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Obtener versión actual
            cursor.execute('SELECT version_actual FROM propuestas WHERE id = ?', (propuesta_id,))
            row = cursor.fetchone()
            version_actual = row[0]
            nueva_version = version_actual + 1

            # Calcular nuevo hash
            hash_contenido = self.calcular_hash(observacion_texto or '', propuesta_texto)

            # Actualizar propuesta principal
            cursor.execute('''
                UPDATE propuestas
                SET observacion_texto = ?, propuesta_texto = ?,
                    observacion_html = ?, propuesta_html = ?,
                    hash_contenido = ?, version_actual = ?,
                    fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (observacion_texto, propuesta_texto, observacion_html,
                  propuesta_html, hash_contenido, nueva_version, propuesta_id))

            # Crear nueva versión
            self.crear_version(propuesta_id, nueva_version, observacion_texto,
                              propuesta_texto, observacion_html, propuesta_html,
                              hash_contenido, motivo_cambio)

            return nueva_version

    def obtener_propuestas_por_ente(self, ente_id):
        """Obtiene todas las propuestas de un ENTE"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.*, e.nombre as ente_nombre, f.nombre as fuente_nombre
                FROM propuestas p
                JOIN entes e ON p.ente_id = e.id
                JOIN fuentes_financiamiento f ON p.fuente_financiamiento_id = f.id
                WHERE p.ente_id = ?
                ORDER BY p.fecha_creacion DESC
            ''', (ente_id,))

            return [dict(row) for row in cursor.fetchall()]

    def obtener_versiones_propuesta(self, propuesta_id):
        """Obtiene todas las versiones de una propuesta"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM versiones_propuestas
                WHERE propuesta_id = ?
                ORDER BY version DESC
            ''', (propuesta_id,))

            return [dict(row) for row in cursor.fetchall()]

    def obtener_estadisticas(self):
        """Obtiene estadísticas generales del sistema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # Total de entes
            cursor.execute('SELECT COUNT(*) FROM entes')
            stats['total_entes'] = cursor.fetchone()[0]

            # Total de fuentes
            cursor.execute('SELECT COUNT(*) FROM fuentes_financiamiento')
            stats['total_fuentes'] = cursor.fetchone()[0]

            # Total de propuestas
            cursor.execute('SELECT COUNT(*) FROM propuestas')
            stats['total_propuestas'] = cursor.fetchone()[0]

            # Propuestas únicas (no duplicadas)
            cursor.execute('SELECT COUNT(*) FROM propuestas WHERE es_duplicado = 0')
            stats['propuestas_unicas'] = cursor.fetchone()[0]

            # Duplicados detectados
            cursor.execute('SELECT COUNT(*) FROM propuestas WHERE es_duplicado = 1')
            stats['duplicados_detectados'] = cursor.fetchone()[0]

            # Total de versiones
            cursor.execute('SELECT COUNT(*) FROM versiones_propuestas')
            stats['total_versiones'] = cursor.fetchone()[0]

            return stats

    def obtener_todas_propuestas(self, limit=100, offset=0):
        """Obtiene todas las propuestas con paginación"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.*, e.nombre as ente_nombre, f.nombre as fuente_nombre
                FROM propuestas p
                JOIN entes e ON p.ente_id = e.id
                JOIN fuentes_financiamiento f ON p.fuente_financiamiento_id = f.id
                ORDER BY p.fecha_creacion DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))

            return [dict(row) for row in cursor.fetchall()]

    def registrar_procesamiento(self, tipo_archivo, archivo_nombre, total_propuestas,
                               duplicados_detectados, versiones_creadas):
        """Registra estadísticas de un procesamiento"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO estadisticas_procesamiento (
                    tipo_archivo, archivo_nombre, total_propuestas,
                    duplicados_detectados, versiones_creadas
                ) VALUES (?, ?, ?, ?, ?)
            ''', (tipo_archivo, archivo_nombre, total_propuestas,
                  duplicados_detectados, versiones_creadas))


# Instancia global de la base de datos
db = Database()
