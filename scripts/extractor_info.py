"""
Extractor de información de ENTE y fuente de financiamiento
Analiza nombres de archivos y contenido de documentos
"""

import re
from pathlib import Path


class ExtractorInfo:
    """Extrae ENTE y fuente de financiamiento de archivos y documentos"""

    # Fuentes de financiamiento conocidas (acrónimos comunes)
    FUENTES_CONOCIDAS = {
        'SA': 'Situación de Auditoría',
        'PRAS': 'Programa de Saneamiento',
        'PDP': 'Programa de Desarrollo Productivo',
        'R': 'Regular',
        'PEFCF': 'Programa Especial de Fomento al Campo y Forestal',
        'FONDO_GENERAL': 'Fondo General',
        'RECURSOS_PROPIOS': 'Recursos Propios',
        'TRANSFERENCIAS': 'Transferencias Federales',
        'CREDITO': 'Crédito',
        'OTROS': 'Otros Recursos'
    }

    # Patrones de ENTES (instituciones)
    ENTES_PATRONES = [
        r'\d+\.\s*([A-Z][A-Z\s]+)',  # "12. FIDECIX" o "12.FIDECIX"
        r'ENTE[:\s]+([A-Z][A-Z\s]+)',  # "ENTE: NOMBRE"
        r'INSTITUCIÓN[:\s]+([A-Z][A-Z\s]+)',  # "INSTITUCIÓN: NOMBRE"
        r'ENTIDAD[:\s]+([A-Z][A-Z\s]+)',  # "ENTIDAD: NOMBRE"
    ]

    def __init__(self):
        pass

    def extraer_de_nombre_archivo(self, filename):
        """
        Extrae ENTE y fuente de financiamiento del nombre del archivo

        Ejemplos:
        - "12.FIDECIX_RRyPE_ENE_ENE_SA.docx" -> ENTE: "12.FIDECIX", FUENTE: "SA"
        - "SECRETARIA_FINANZAS_PRAS_2024.xlsx" -> ENTE: "SECRETARIA FINANZAS", FUENTE: "PRAS"

        Returns:
            dict: {'ente': str, 'fuente': str, 'patron_detectado': str}
        """
        filename = Path(filename).stem  # Sin extensión

        # Intentar patrón: [NUMERO].[ENTE]_..._[FUENTE]
        patron1 = r'^(\d+\.?\s*[A-Z]+)[_\s].*?[_\s]([A-Z]+)$'
        match = re.search(patron1, filename)
        if match:
            ente = match.group(1).replace('_', ' ').strip()
            fuente = match.group(2).strip()
            return {
                'ente': ente,
                'fuente': fuente,
                'fuente_descripcion': self.FUENTES_CONOCIDAS.get(fuente, fuente),
                'patron_detectado': 'numero_ente_fuente'
            }

        # Intentar patrón: [NOMBRE]_[FUENTE]
        for fuente_key in self.FUENTES_CONOCIDAS.keys():
            if fuente_key in filename.upper():
                # Extraer la parte antes de la fuente como ENTE
                partes = filename.split('_')
                ente_partes = []
                for parte in partes:
                    if parte.upper() == fuente_key:
                        break
                    ente_partes.append(parte)

                ente = ' '.join(ente_partes).strip()
                if ente:
                    return {
                        'ente': ente.upper(),
                        'fuente': fuente_key,
                        'fuente_descripcion': self.FUENTES_CONOCIDAS[fuente_key],
                        'patron_detectado': 'nombre_fuente'
                    }

        # Si no se detecta, usar valores por defecto
        return {
            'ente': filename.split('_')[0].upper() if '_' in filename else filename.upper(),
            'fuente': 'NO_ESPECIFICADA',
            'fuente_descripcion': 'No especificada',
            'patron_detectado': 'por_defecto'
        }

    def extraer_de_documento_docx(self, doc):
        """
        Busca ENTE y fuente de financiamiento en el contenido del documento Word

        Args:
            doc: Documento python-docx

        Returns:
            dict: {'ente': str or None, 'fuente': str or None}
        """
        resultado = {'ente': None, 'fuente': None}

        # Buscar en párrafos
        for parrafo in doc.paragraphs:
            texto = parrafo.text.strip()

            # Buscar ENTE
            if not resultado['ente']:
                for patron in self.ENTES_PATRONES:
                    match = re.search(patron, texto, re.IGNORECASE)
                    if match:
                        resultado['ente'] = match.group(1).strip()
                        break

            # Buscar fuente de financiamiento
            if not resultado['fuente']:
                texto_upper = texto.upper()
                if 'FUENTE' in texto_upper or 'FINANCIAMIENTO' in texto_upper:
                    for fuente_key in self.FUENTES_CONOCIDAS.keys():
                        if fuente_key in texto_upper:
                            resultado['fuente'] = fuente_key
                            break

        # Buscar en tablas
        for tabla in doc.tables:
            for fila in tabla.rows:
                for celda in fila.cells:
                    texto = celda.text.strip()

                    # Buscar ENTE
                    if not resultado['ente']:
                        for patron in self.ENTES_PATRONES:
                            match = re.search(patron, texto, re.IGNORECASE)
                            if match:
                                resultado['ente'] = match.group(1).strip()
                                break

                    # Buscar fuente
                    if not resultado['fuente']:
                        texto_upper = texto.upper()
                        for fuente_key in self.FUENTES_CONOCIDAS.keys():
                            if fuente_key in texto_upper:
                                resultado['fuente'] = fuente_key
                                break

        return resultado

    def extraer_de_documento_xlsx(self, filepath):
        """
        Busca ENTE y fuente de financiamiento en el contenido del Excel

        Args:
            filepath: Ruta del archivo Excel

        Returns:
            dict: {'ente': str or None, 'fuente': str or None}
        """
        import pandas as pd

        resultado = {'ente': None, 'fuente': None}

        try:
            excel_data = pd.ExcelFile(filepath)

            # Buscar en todas las hojas
            for sheet_name in excel_data.sheet_names:
                df = excel_data.parse(sheet_name)

                # Buscar en las primeras filas (típicamente contienen encabezados)
                for i in range(min(20, len(df))):
                    for col in df.columns:
                        cell_value = str(df.iloc[i][col])

                        # Buscar ENTE
                        if not resultado['ente']:
                            for patron in self.ENTES_PATRONES:
                                match = re.search(patron, cell_value, re.IGNORECASE)
                                if match:
                                    resultado['ente'] = match.group(1).strip()
                                    break

                        # Buscar fuente
                        if not resultado['fuente']:
                            cell_upper = cell_value.upper()
                            for fuente_key in self.FUENTES_CONOCIDAS.keys():
                                if fuente_key in cell_upper:
                                    resultado['fuente'] = fuente_key
                                    break

                    if resultado['ente'] and resultado['fuente']:
                        break

                if resultado['ente'] and resultado['fuente']:
                    break

        except Exception as e:
            print(f"Error al extraer info de XLSX: {e}")

        return resultado

    def extraer_completo(self, filepath, doc=None):
        """
        Extrae ENTE y fuente combinando nombre de archivo y contenido

        Args:
            filepath: Ruta del archivo
            doc: Documento python-docx (opcional, solo para DOCX)

        Returns:
            dict: {
                'ente': str,
                'fuente': str,
                'fuente_descripcion': str,
                'origen_ente': 'archivo' | 'contenido',
                'origen_fuente': 'archivo' | 'contenido'
            }
        """
        # Extraer del nombre de archivo
        info_archivo = self.extraer_de_nombre_archivo(filepath)

        # Extraer del contenido
        if filepath.lower().endswith('.docx') and doc:
            info_contenido = self.extraer_de_documento_docx(doc)
        elif filepath.lower().endswith('.xlsx'):
            info_contenido = self.extraer_de_documento_xlsx(filepath)
        else:
            info_contenido = {'ente': None, 'fuente': None}

        # Combinar resultados (priorizar contenido sobre archivo)
        ente_final = info_contenido.get('ente') or info_archivo.get('ente', 'ENTE_NO_ESPECIFICADO')
        fuente_final = info_contenido.get('fuente') or info_archivo.get('fuente', 'NO_ESPECIFICADA')

        return {
            'ente': ente_final,
            'fuente': fuente_final,
            'fuente_descripcion': self.FUENTES_CONOCIDAS.get(fuente_final, fuente_final),
            'origen_ente': 'contenido' if info_contenido.get('ente') else 'archivo',
            'origen_fuente': 'contenido' if info_contenido.get('fuente') else 'archivo',
            'patron_detectado': info_archivo.get('patron_detectado')
        }


# Instancia global del extractor
extractor = ExtractorInfo()
