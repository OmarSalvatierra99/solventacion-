"""
Analizador de Metadatos para Documentos de Solventación
Extrae información clave: Ente, Fuente de Financiamiento, Periodo, Tipo de Documento
"""

import re
import os
from typing import Dict, Optional, List
from pathlib import Path


class MetadataAnalyzer:
    """
    Analiza nombres de archivos y contenido para extraer metadatos estructurados
    """

    # Fuentes de financiamiento conocidas
    FUENTES_FINANCIAMIENTO = {
        'SA': 'Subsidio para la Asistencia',
        'PEFCF': 'Programa de Estímulo a la Función de Ciencia y Formación',
        'R': 'Recursos Propios',
        'PRAS': 'Programa de Recursos de Alta Seguridad',
        'PDP': 'Programa de Desarrollo Profesional',
        'PEFCF': 'Programa Especial de Fondos y Contingencias Fiscales',
        'REA': 'Recursos Extraordinarios Adicionales',
        'RRyPE': 'Resultados de Revisión y Propuestas de Entrega'
    }

    # Entes conocidos
    ENTES_CONOCIDOS = [
        'FIDECIX', 'SEPUEDE', 'FIDEGAR', 'FIDEAPECH', 'FIDE',
        'COEPRIST', 'DIF', 'SEPE', 'CEA', 'ITE'
    ]

    def __init__(self):
        """Inicializa el analizador de metadatos"""
        pass

    def extraer_ente_de_nombre_archivo(self, nombre_archivo: str) -> Optional[str]:
        """
        Extrae el nombre del ente del nombre del archivo

        Args:
            nombre_archivo: Nombre del archivo (con o sin ruta)

        Returns:
            Nombre del ente o None si no se encuentra

        Ejemplos:
            "12.FIDECIX_RRyPE_ENE_JUN_SA.docx" -> "FIDECIX"
            "SEPUEDE_informe.xlsx" -> "SEPUEDE"
        """
        nombre_base = os.path.basename(nombre_archivo)

        # Buscar entes conocidos en el nombre
        for ente in self.ENTES_CONOCIDOS:
            if ente in nombre_base.upper():
                return ente

        # Intentar extraer usando patrones comunes
        # Patrón: número.ENTE_resto
        match = re.search(r'\d+\.([A-Z]+)_', nombre_base.upper())
        if match:
            return match.group(1)

        # Patrón: ENTE_resto (sin número)
        match = re.search(r'^([A-Z]+)_', nombre_base.upper())
        if match:
            return match.group(1)

        return "DESCONOCIDO"

    def extraer_fuente_financiamiento(self, nombre_archivo: str, contenido_hojas: Optional[List[str]] = None) -> List[str]:
        """
        Extrae la(s) fuente(s) de financiamiento del nombre del archivo o del contenido

        Args:
            nombre_archivo: Nombre del archivo
            contenido_hojas: Lista de nombres de hojas (para archivos XLSX)

        Returns:
            Lista de fuentes de financiamiento encontradas

        Ejemplos:
            "12.FIDECIX_RRyPE_ENE_JUN_SA.docx" -> ["SA"]
            XLSX con hojas ['SA', 'PEFCF', 'R'] -> ["SA", "PEFCF", "R"]
        """
        fuentes_encontradas = []
        nombre_base = os.path.basename(nombre_archivo).upper()

        # Buscar en el nombre del archivo
        for codigo, descripcion in self.FUENTES_FINANCIAMIENTO.items():
            # Buscar código al final del nombre (antes de la extensión)
            if f"_{codigo}." in nombre_base or f"_{codigo}_" in nombre_base or nombre_base.endswith(f"_{codigo}"):
                if codigo not in fuentes_encontradas:
                    fuentes_encontradas.append(codigo)

        # Buscar en nombres de hojas (para XLSX)
        if contenido_hojas:
            for hoja in contenido_hojas:
                hoja_upper = hoja.upper()
                for codigo in self.FUENTES_FINANCIAMIENTO.keys():
                    if hoja_upper == codigo or f"_{codigo}" in hoja_upper or f"{codigo}_" in hoja_upper:
                        if codigo not in fuentes_encontradas:
                            fuentes_encontradas.append(codigo)

        return fuentes_encontradas if fuentes_encontradas else ["NO_ESPECIFICADA"]

    def extraer_periodo(self, nombre_archivo: str) -> Optional[str]:
        """
        Extrae el periodo del nombre del archivo

        Args:
            nombre_archivo: Nombre del archivo

        Returns:
            Periodo encontrado o None

        Ejemplos:
            "12.FIDECIX_RRyPE_ENE_JUN_SA.docx" -> "ENE_JUN"
            "informe_ENE_ENE.xlsx" -> "ENE_ENE"
        """
        nombre_base = os.path.basename(nombre_archivo).upper()

        # Patrón para periodos: MES_MES (ej: ENE_JUN, ENE_ENE)
        meses = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']

        for i, mes1 in enumerate(meses):
            for mes2 in meses:
                patron = f"{mes1}_{mes2}"
                if patron in nombre_base:
                    return patron

        # Buscar años
        match = re.search(r'20\d{2}', nombre_base)
        if match:
            return match.group(0)

        return None

    def extraer_tipo_documento(self, nombre_archivo: str) -> Optional[str]:
        """
        Extrae el tipo de documento del nombre del archivo

        Args:
            nombre_archivo: Nombre del archivo

        Returns:
            Tipo de documento o None

        Ejemplos:
            "12.FIDECIX_RRyPE_ENE_JUN_SA.docx" -> "RRyPE"
            "12.FIDECIX_REA_RRyPE_ENE_JUN_SA.docx" -> "REA_RRyPE"
        """
        nombre_base = os.path.basename(nombre_archivo).upper()

        # Buscar tipos de documento conocidos
        tipos_conocidos = ['RRyPE', 'REA', 'INFORME', 'REPORTE', 'PROPUESTA']

        for tipo in tipos_conocidos:
            if tipo in nombre_base:
                # Si encuentra REA y RRyPE, combinar
                if 'REA' in nombre_base and 'RRyPE' in nombre_base:
                    return "REA_RRyPE"
                return tipo

        return "GENERAL"

    def analizar_archivo(self, nombre_archivo: str, contenido_extraido: Optional[Dict] = None) -> Dict[str, any]:
        """
        Analiza un archivo completo y extrae todos los metadatos relevantes

        Args:
            nombre_archivo: Nombre del archivo
            contenido_extraido: Contenido extraído por los procesadores (opcional)

        Returns:
            Diccionario con todos los metadatos extraídos
        """
        # Extraer nombres de hojas si es XLSX
        hojas = None
        if contenido_extraido and 'metadatos' in contenido_extraido:
            hojas = contenido_extraido['metadatos'].get('nombres_hojas')

        # Extraer todos los metadatos
        ente = self.extraer_ente_de_nombre_archivo(nombre_archivo)
        fuentes = self.extraer_fuente_financiamiento(nombre_archivo, hojas)
        periodo = self.extraer_periodo(nombre_archivo)
        tipo_doc = self.extraer_tipo_documento(nombre_archivo)

        metadatos = {
            'nombre_archivo': os.path.basename(nombre_archivo),
            'ruta_completa': nombre_archivo,
            'ente': ente,
            'fuentes_financiamiento': fuentes,
            'periodo': periodo,
            'tipo_documento': tipo_doc,
            'extension': Path(nombre_archivo).suffix.lower()
        }

        # Agregar información del contenido extraído si existe
        if contenido_extraido:
            metadatos['tiene_propuestas'] = len(contenido_extraido.get('contenido', {}).get('propuestas', [])) > 0
            metadatos['total_propuestas'] = len(contenido_extraido.get('contenido', {}).get('propuestas', []))

            # Detectar si tiene imágenes
            if contenido_extraido.get('tipo_archivo') == 'DOCX':
                imagenes_info = contenido_extraido.get('metadatos', {}).get('imagenes', {})
                metadatos['tiene_imagenes'] = imagenes_info.get('tiene_imagenes', False)
                metadatos['cantidad_imagenes'] = imagenes_info.get('cantidad', 0)
            elif contenido_extraido.get('tipo_archivo') == 'XLSX':
                metadatos['cantidad_imagenes'] = contenido_extraido.get('estadisticas', {}).get('total_imagenes', 0)
                metadatos['tiene_imagenes'] = metadatos['cantidad_imagenes'] > 0

        return metadatos

    def agrupar_por_ente_y_financiamiento(self, lista_metadatos: List[Dict]) -> Dict[str, Dict[str, List[Dict]]]:
        """
        Agrupa una lista de metadatos por ente y fuente de financiamiento

        Args:
            lista_metadatos: Lista de diccionarios de metadatos

        Returns:
            Diccionario anidado: {ente: {fuente: [metadatos]}}
        """
        agrupado = {}

        for metadata in lista_metadatos:
            ente = metadata.get('ente', 'DESCONOCIDO')
            fuentes = metadata.get('fuentes_financiamiento', ['NO_ESPECIFICADA'])

            # Inicializar ente si no existe
            if ente not in agrupado:
                agrupado[ente] = {}

            # Agregar a cada fuente de financiamiento
            for fuente in fuentes:
                if fuente not in agrupado[ente]:
                    agrupado[ente][fuente] = []

                agrupado[ente][fuente].append(metadata)

        return agrupado


# Instancia global del analizador
analyzer = MetadataAnalyzer()


def analizar_archivo(nombre_archivo: str, contenido_extraido: Optional[Dict] = None) -> Dict[str, any]:
    """
    Función de conveniencia para analizar un archivo

    Args:
        nombre_archivo: Nombre del archivo a analizar
        contenido_extraido: Contenido extraído por los procesadores (opcional)

    Returns:
        Diccionario con metadatos extraídos
    """
    return analyzer.analizar_archivo(nombre_archivo, contenido_extraido)


def agrupar_metadatos(lista_metadatos: List[Dict]) -> Dict[str, Dict[str, List[Dict]]]:
    """
    Función de conveniencia para agrupar metadatos

    Args:
        lista_metadatos: Lista de diccionarios de metadatos

    Returns:
        Diccionario agrupado por ente y fuente de financiamiento
    """
    return analyzer.agrupar_por_ente_y_financiamiento(lista_metadatos)
