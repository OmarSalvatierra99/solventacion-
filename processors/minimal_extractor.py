"""
Extractor MINIMALISTA de campos específicos de documentos de solventación
Extrae solo los campos necesarios de forma simple y rápida
"""

import pandas as pd
from openpyxl import load_workbook
from docx import Document
from html import escape
from typing import Dict, List, Any
import re


class MinimalExtractor:
    """Extractor minimalista que se enfoca en campos específicos"""

    def __init__(self):
        # Campos que buscamos extraer
        self.campos_busqueda = {
            'poliza': ['PÓLIZA', 'POLIZA', 'DOCUMENTO'],
            'fecha': ['FECHA'],
            'concepto': ['CONCEPTO'],
            'importe': ['IMPORTE'],
            'monto_observado': ['MONTO OBSERVADO', 'MONTO', 'OBSERVADO'],
            'descripcion': ['DESCRIPCIÓN', 'DESCRIPCION', 'RESULTADO'],
            'normatividad': ['NORMATIVIDAD', 'INCUMPLIDA'],
            'propuesta': ['PROPUESTA', 'SOLVENTACIÓN', 'SOLVENTACION']
        }

    def _limpiar_texto(self, texto: Any) -> str:
        """Limpia y normaliza texto"""
        if texto is None:
            return ""
        if not isinstance(texto, str):
            texto = str(texto)
        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto

    def _normalizar_busqueda(self, texto: str) -> str:
        """Normaliza texto para búsqueda"""
        if not texto:
            return ""
        texto = texto.upper()
        texto = texto.replace('Á', 'A').replace('É', 'E').replace('Í', 'I')
        texto = texto.replace('Ó', 'O').replace('Ú', 'U').replace('Ñ', 'N')
        return texto

    def _contiene_campo(self, texto: str, palabras_clave: List[str]) -> bool:
        """Verifica si el texto contiene alguna de las palabras clave"""
        if not texto:
            return False
        texto_norm = self._normalizar_busqueda(texto)
        return any(palabra in texto_norm for palabra in palabras_clave)

    def extraer_xlsx(self, filepath: str) -> List[Dict[str, Any]]:
        """Extrae campos de un archivo XLSX de forma minimalista"""
        propuestas = []

        try:
            excel_data = pd.ExcelFile(filepath)
            wb = load_workbook(filepath)
            numero_global = 1

            for sheet_name in excel_data.sheet_names:
                df = excel_data.parse(sheet_name)
                sheet = wb[sheet_name]

                # Buscar filas que contengan "PROPUESTA DE SOLVENTACIÓN"
                for i, row in df.iterrows():
                    propuesta_data = {
                        'numero': numero_global,
                        'hoja': sheet_name,
                        'fila': i + 2,
                        'poliza': None,
                        'fecha': None,
                        'concepto': None,
                        'importe': None,
                        'monto_observado': None,
                        'descripcion': None,
                        'normatividad': None,
                        'propuesta': None
                    }

                    encontro_propuesta = False

                    # Buscar en cada celda de la fila
                    for idx in range(len(row)):
                        cell_value = row.iloc[idx]
                        cell_text = str(cell_value) if cell_value else ""

                        # Si encontramos "PROPUESTA DE SOLVENTACIÓN"
                        if self._contiene_campo(cell_text, self.campos_busqueda['propuesta']):
                            # Buscar propuesta en celdas siguientes
                            if idx + 1 < len(row):
                                propuesta_value = row.iloc[idx + 1]
                                if propuesta_value and str(propuesta_value).strip():
                                    propuesta_data['propuesta'] = self._limpiar_texto(propuesta_value)
                                    encontro_propuesta = True

                        # Buscar otros campos en la misma fila o cercanas
                        if self._contiene_campo(cell_text, self.campos_busqueda['poliza']) and idx + 1 < len(row):
                            propuesta_data['poliza'] = self._limpiar_texto(row.iloc[idx + 1])

                        if self._contiene_campo(cell_text, self.campos_busqueda['fecha']) and idx + 1 < len(row):
                            propuesta_data['fecha'] = self._limpiar_texto(row.iloc[idx + 1])

                        if self._contiene_campo(cell_text, self.campos_busqueda['concepto']) and idx + 1 < len(row):
                            propuesta_data['concepto'] = self._limpiar_texto(row.iloc[idx + 1])

                        if self._contiene_campo(cell_text, self.campos_busqueda['importe']) and idx + 1 < len(row):
                            propuesta_data['importe'] = self._limpiar_texto(row.iloc[idx + 1])

                        if self._contiene_campo(cell_text, self.campos_busqueda['monto_observado']) and idx + 1 < len(row):
                            propuesta_data['monto_observado'] = self._limpiar_texto(row.iloc[idx + 1])

                        if self._contiene_campo(cell_text, self.campos_busqueda['descripcion']) and idx + 1 < len(row):
                            propuesta_data['descripcion'] = self._limpiar_texto(row.iloc[idx + 1])

                        if self._contiene_campo(cell_text, self.campos_busqueda['normatividad']) and idx + 1 < len(row):
                            propuesta_data['normatividad'] = self._limpiar_texto(row.iloc[idx + 1])

                    # Si encontramos una propuesta, agregarla
                    if encontro_propuesta and propuesta_data['propuesta']:
                        propuestas.append(propuesta_data)
                        numero_global += 1

            return propuestas

        except Exception as e:
            print(f"Error en extracción XLSX minimal: {e}")
            return []

    def extraer_docx(self, filepath: str) -> List[Dict[str, Any]]:
        """Extrae campos de un archivo DOCX de forma minimalista"""
        propuestas = []

        try:
            doc = Document(filepath)
            numero_global = 1

            # Buscar en tablas
            for tabla_idx, tabla in enumerate(doc.tables):
                for row_idx, row in enumerate(tabla.rows):
                    propuesta_data = {
                        'numero': numero_global,
                        'tabla': tabla_idx + 1,
                        'fila': row_idx + 1,
                        'poliza': None,
                        'fecha': None,
                        'concepto': None,
                        'importe': None,
                        'monto_observado': None,
                        'descripcion': None,
                        'normatividad': None,
                        'propuesta': None
                    }

                    encontro_propuesta = False

                    # Buscar en cada celda
                    for cell_idx, cell in enumerate(row.cells):
                        cell_text = cell.text.strip()

                        # Si encontramos "PROPUESTA DE SOLVENTACIÓN"
                        if self._contiene_campo(cell_text, self.campos_busqueda['propuesta']):
                            # Buscar propuesta en celda siguiente
                            if cell_idx + 1 < len(row.cells):
                                propuesta_value = row.cells[cell_idx + 1].text.strip()
                                if propuesta_value:
                                    propuesta_data['propuesta'] = propuesta_value
                                    encontro_propuesta = True

                        # Buscar otros campos
                        if self._contiene_campo(cell_text, self.campos_busqueda['poliza']) and cell_idx + 1 < len(row.cells):
                            propuesta_data['poliza'] = row.cells[cell_idx + 1].text.strip()

                        if self._contiene_campo(cell_text, self.campos_busqueda['fecha']) and cell_idx + 1 < len(row.cells):
                            propuesta_data['fecha'] = row.cells[cell_idx + 1].text.strip()

                        if self._contiene_campo(cell_text, self.campos_busqueda['concepto']) and cell_idx + 1 < len(row.cells):
                            propuesta_data['concepto'] = row.cells[cell_idx + 1].text.strip()

                        if self._contiene_campo(cell_text, self.campos_busqueda['importe']) and cell_idx + 1 < len(row.cells):
                            propuesta_data['importe'] = row.cells[cell_idx + 1].text.strip()

                        if self._contiene_campo(cell_text, self.campos_busqueda['monto_observado']) and cell_idx + 1 < len(row.cells):
                            propuesta_data['monto_observado'] = row.cells[cell_idx + 1].text.strip()

                        if self._contiene_campo(cell_text, self.campos_busqueda['descripcion']) and cell_idx + 1 < len(row.cells):
                            propuesta_data['descripcion'] = row.cells[cell_idx + 1].text.strip()

                        if self._contiene_campo(cell_text, self.campos_busqueda['normatividad']) and cell_idx + 1 < len(row.cells):
                            propuesta_data['normatividad'] = row.cells[cell_idx + 1].text.strip()

                    # Si encontramos una propuesta, agregarla
                    if encontro_propuesta and propuesta_data['propuesta']:
                        propuestas.append(propuesta_data)
                        numero_global += 1

            return propuestas

        except Exception as e:
            print(f"Error en extracción DOCX minimal: {e}")
            return []

    def formatear_para_api(self, propuestas: List[Dict[str, Any]], tipo_archivo: str) -> Dict[str, Any]:
        """Formatea las propuestas para la API (compatible con formato existente)"""

        # Convertir al formato esperado por el frontend
        propuestas_formateadas = []

        for prop in propuestas:
            # Crear HTML simple para visualización
            descripcion_html = f"<p>{escape(prop.get('descripcion', 'N/A'))}</p>" if prop.get('descripcion') else "<p>N/A</p>"
            normatividad_html = f"<p>{escape(prop.get('normatividad', 'N/A'))}</p>" if prop.get('normatividad') else "<p>N/A</p>"
            propuesta_html = f"<p>{escape(prop.get('propuesta', 'N/A'))}</p>" if prop.get('propuesta') else "<p>N/A</p>"

            # Combinar descripción y normatividad como "observación"
            observacion_partes = []
            if prop.get('descripcion'):
                observacion_partes.append(f"DESCRIPCIÓN DEL RESULTADO:\n{prop.get('descripcion')}")
            if prop.get('normatividad'):
                observacion_partes.append(f"NORMATIVIDAD INCUMPLIDA:\n{prop.get('normatividad')}")

            observacion_texto = "\n\n".join(observacion_partes) if observacion_partes else "Sin observación"
            observacion_html = "<br>".join([descripcion_html, normatividad_html]) if observacion_partes else "<p>Sin observación</p>"

            propuestas_formateadas.append({
                'numero': prop.get('numero'),
                'hoja': prop.get('hoja') or f"Tabla {prop.get('tabla', 'N/A')}",
                'fila': prop.get('fila'),
                # Campos específicos extraídos
                'poliza': prop.get('poliza'),
                'fecha': prop.get('fecha'),
                'concepto': prop.get('concepto'),
                'importe': prop.get('importe'),
                'monto_observado': prop.get('monto_observado'),
                'descripcion': prop.get('descripcion'),
                'normatividad': prop.get('normatividad'),
                # Formato compatible con frontend existente
                'observacion': observacion_html,
                'observacion_texto': observacion_texto,
                'propuesta_texto': prop.get('propuesta', 'N/A'),
                'propuesta_html': propuesta_html,
                'metodo_extraccion': 'minimal'
            })

        return {
            'propuestas': propuestas_formateadas,
            'total': len(propuestas_formateadas),
            'metodo': 'minimal_extractor'
        }


# Instancia global
extractor = MinimalExtractor()


def process_with_minimal(filepath: str, tipo_archivo: str) -> Dict[str, Any]:
    """Procesa un archivo con el extractor minimalista"""

    if tipo_archivo.upper() == 'XLSX':
        propuestas = extractor.extraer_xlsx(filepath)
    elif tipo_archivo.upper() == 'DOCX':
        propuestas = extractor.extraer_docx(filepath)
    else:
        return {'error': f'Tipo de archivo no soportado: {tipo_archivo}'}

    return extractor.formatear_para_api(propuestas, tipo_archivo)
