"""
Servicio de detección de duplicados
Usa comparación exacta (hash) y semántica (OpenAI) como respaldo
"""

import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from scripts.database import db

# Cargar variables de entorno
load_dotenv()


class DuplicateDetector:
    """Detector de propuestas duplicadas usando comparación exacta y IA"""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.use_ai = bool(os.getenv('OPENAI_API_KEY'))

    def limpiar_html(self, html_texto):
        """Elimina etiquetas HTML y espacios extra para comparación limpia"""
        if not html_texto:
            return ""
        # Eliminar etiquetas HTML
        texto_limpio = re.sub(r'<[^>]+>', '', html_texto)
        # Normalizar espacios
        texto_limpio = ' '.join(texto_limpio.split())
        return texto_limpio.strip()

    def comparar_exacto(self, texto1, texto2):
        """Comparación exacta de textos (ignorando formato HTML)"""
        limpio1 = self.limpiar_html(texto1).lower()
        limpio2 = self.limpiar_html(texto2).lower()
        return limpio1 == limpio2

    def detectar_duplicado_con_ia(self, observacion_nueva, propuesta_nueva,
                                   observacion_existente, propuesta_existente):
        """
        Usa OpenAI para determinar si dos propuestas son similares semánticamente

        Returns:
            dict: {
                'es_duplicado': bool,
                'es_version': bool,  # True si es una evolución/corrección de la propuesta
                'similitud': float (0-100),
                'explicacion': str,
                'cambios_detectados': list
            }
        """
        if not self.use_ai:
            return {
                'es_duplicado': False,
                'es_version': False,
                'similitud': 0,
                'explicacion': 'OpenAI API no configurada',
                'cambios_detectados': []
            }

        try:
            # Limpiar HTML para análisis
            obs_nueva_limpia = self.limpiar_html(observacion_nueva)
            prop_nueva_limpia = self.limpiar_html(propuesta_nueva)
            obs_exist_limpia = self.limpiar_html(observacion_existente)
            prop_exist_limpia = self.limpiar_html(propuesta_existente)

            prompt = f"""Eres un experto en análisis de documentos de auditoría y solventación.

Analiza estas dos propuestas de solventación y determina:
1. ¿Son DUPLICADOS? (mismo contenido, posiblemente con pequeñas diferencias de formato)
2. ¿Es la segunda una NUEVA VERSIÓN de la primera? (misma observación pero propuesta mejorada/corregida)
3. ¿Qué porcentaje de similitud tienen? (0-100)
4. ¿Cuáles son los cambios principales?

PROPUESTA EXISTENTE:
Observación: {obs_exist_limpia}
Propuesta: {prop_exist_limpia}

PROPUESTA NUEVA:
Observación: {obs_nueva_limpia}
Propuesta: {prop_nueva_limpia}

Responde ÚNICAMENTE en formato JSON:
{{
    "es_duplicado": true/false,
    "es_version": true/false,
    "similitud": 0-100,
    "explicacion": "explicación breve",
    "cambios_detectados": ["cambio1", "cambio2", ...]
}}

IMPORTANTE:
- es_duplicado = true si son prácticamente idénticas (>95% similitud)
- es_version = true si la observación es similar pero la propuesta cambió significativamente
- Si es_version = true, entonces es_duplicado = false
"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un analista experto en documentos de auditoría. Respondes solo en JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )

            # Extraer respuesta JSON
            import json
            respuesta_texto = response.choices[0].message.content.strip()

            # Limpiar markdown si existe
            if respuesta_texto.startswith('```'):
                respuesta_texto = respuesta_texto.split('```')[1]
                if respuesta_texto.startswith('json'):
                    respuesta_texto = respuesta_texto[4:]

            resultado = json.loads(respuesta_texto)

            return resultado

        except Exception as e:
            print(f"Error en detección con IA: {str(e)}")
            return {
                'es_duplicado': False,
                'es_version': False,
                'similitud': 0,
                'explicacion': f'Error al analizar: {str(e)}',
                'cambios_detectados': []
            }

    def verificar_propuesta(self, ente_id, fuente_id, observacion_texto,
                           propuesta_texto, observacion_html, propuesta_html):
        """
        Verifica si una propuesta es duplicada o una nueva versión

        Returns:
            dict: {
                'es_duplicado_exacto': bool,
                'es_duplicado_semantico': bool,
                'es_nueva_version': bool,
                'propuesta_existente_id': int or None,
                'similitud': float,
                'explicacion': str,
                'accion_recomendada': 'insertar' | 'marcar_duplicado' | 'crear_version'
            }
        """
        # 1. Verificar duplicado exacto por hash
        hash_contenido = db.calcular_hash(observacion_texto or '', propuesta_texto)
        propuesta_existente = db.buscar_propuesta_existente(hash_contenido, ente_id, fuente_id)

        if propuesta_existente:
            return {
                'es_duplicado_exacto': True,
                'es_duplicado_semantico': False,
                'es_nueva_version': False,
                'propuesta_existente_id': propuesta_existente['id'],
                'similitud': 100,
                'explicacion': 'Propuesta idéntica encontrada (hash exacto)',
                'accion_recomendada': 'marcar_duplicado'
            }

        # 2. Si no hay duplicado exacto, buscar propuestas similares con IA
        # Obtener todas las propuestas del mismo ente y fuente
        propuestas_ente = db.obtener_propuestas_por_ente(ente_id)
        propuestas_fuente = [p for p in propuestas_ente
                             if p['fuente_financiamiento_id'] == fuente_id]

        mejor_similitud = 0
        mejor_match = None
        resultado_ia = None

        for propuesta_existente in propuestas_fuente:
            # Comparar con IA
            resultado = self.detectar_duplicado_con_ia(
                observacion_texto,
                propuesta_texto,
                propuesta_existente['observacion_texto'],
                propuesta_existente['propuesta_texto']
            )

            if resultado['similitud'] > mejor_similitud:
                mejor_similitud = resultado['similitud']
                mejor_match = propuesta_existente
                resultado_ia = resultado

        # 3. Tomar decisión basada en similitud
        if mejor_similitud >= 95 and resultado_ia and resultado_ia['es_duplicado']:
            return {
                'es_duplicado_exacto': False,
                'es_duplicado_semantico': True,
                'es_nueva_version': False,
                'propuesta_existente_id': mejor_match['id'],
                'similitud': mejor_similitud,
                'explicacion': resultado_ia.get('explicacion', 'Propuesta muy similar detectada por IA'),
                'cambios_detectados': resultado_ia.get('cambios_detectados', []),
                'accion_recomendada': 'marcar_duplicado'
            }

        elif mejor_similitud >= 70 and resultado_ia and resultado_ia['es_version']:
            return {
                'es_duplicado_exacto': False,
                'es_duplicado_semantico': False,
                'es_nueva_version': True,
                'propuesta_existente_id': mejor_match['id'],
                'similitud': mejor_similitud,
                'explicacion': resultado_ia.get('explicacion', 'Nueva versión de propuesta existente'),
                'cambios_detectados': resultado_ia.get('cambios_detectados', []),
                'accion_recomendada': 'crear_version'
            }

        # 4. Si no es duplicado ni versión, es una propuesta nueva
        return {
            'es_duplicado_exacto': False,
            'es_duplicado_semantico': False,
            'es_nueva_version': False,
            'propuesta_existente_id': None,
            'similitud': mejor_similitud if mejor_match else 0,
            'explicacion': 'Propuesta única, sin duplicados detectados',
            'cambios_detectados': [],
            'accion_recomendada': 'insertar'
        }


# Instancia global del detector
detector = DuplicateDetector()
