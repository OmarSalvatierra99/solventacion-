"""
Validador de Imágenes en Propuestas de Solventación
Detecta y reporta imágenes dentro de propuestas, lo cual está prohibido
"""

import os
from typing import Dict, List, Optional
from datetime import datetime


class ImageValidator:
    """
    Valida que las propuestas de solventación no contengan imágenes
    Detecta y reporta cualquier imagen encontrada en propuestas
    """

    def __init__(self):
        """Inicializa el validador de imágenes"""
        self.reportes = []

    def validar_propuestas_docx(self, nombre_archivo: str, contenido_extraido: Dict) -> Dict:
        """
        Valida propuestas en un archivo DOCX para detectar imágenes

        Args:
            nombre_archivo: Nombre del archivo DOCX
            contenido_extraido: Contenido extraído por el procesador DOCX

        Returns:
            Diccionario con el reporte de validación
        """
        reporte = {
            'nombre_archivo': nombre_archivo,
            'tipo_archivo': 'DOCX',
            'fecha_validacion': datetime.now().isoformat(),
            'tiene_imagenes_en_propuestas': False,
            'total_imagenes_documento': 0,
            'imagenes_detectadas': [],
            'propuestas_con_imagenes': [],
            'estado': 'VÁLIDO'
        }

        # Verificar si hay imágenes en el documento
        imagenes_info = contenido_extraido.get('metadatos', {}).get('imagenes', {})
        total_imagenes = imagenes_info.get('cantidad', 0)
        reporte['total_imagenes_documento'] = total_imagenes

        if total_imagenes > 0:
            # Obtener detalles de las imágenes
            imagenes_detalles = imagenes_info.get('detalles', [])

            # Para archivos DOCX, si hay imágenes en el documento,
            # asumimos que podrían estar en las propuestas
            # (la ubicación exacta requiere análisis más profundo del XML)

            propuestas = contenido_extraido.get('contenido', {}).get('propuestas', [])

            if len(propuestas) > 0 and total_imagenes > 0:
                # Marcar como potencialmente problemático
                reporte['tiene_imagenes_en_propuestas'] = True
                reporte['estado'] = 'ADVERTENCIA'

                # Registrar las imágenes encontradas
                for idx, imagen in enumerate(imagenes_detalles):
                    reporte['imagenes_detectadas'].append({
                        'indice': imagen.get('indice'),
                        'tipo': imagen.get('tipo'),
                        'nombre': imagen.get('nombre'),
                        'tamaño_bytes': imagen.get('tamaño_bytes'),
                        'ubicacion': 'Documento (ubicación exacta requiere análisis detallado)'
                    })

                # Advertir sobre todas las propuestas
                for propuesta in propuestas:
                    reporte['propuestas_con_imagenes'].append({
                        'numero': propuesta.get('numero'),
                        'observacion': propuesta.get('observacion_texto', '')[:100],
                        'advertencia': f'El documento contiene {total_imagenes} imagen(es). Revisar manualmente.'
                    })

        return reporte

    def validar_propuestas_xlsx(self, nombre_archivo: str, contenido_extraido: Dict) -> Dict:
        """
        Valida propuestas en un archivo XLSX para detectar imágenes

        Args:
            nombre_archivo: Nombre del archivo XLSX
            contenido_extraido: Contenido extraído por el procesador XLSX

        Returns:
            Diccionario con el reporte de validación
        """
        reporte = {
            'nombre_archivo': nombre_archivo,
            'tipo_archivo': 'XLSX',
            'fecha_validacion': datetime.now().isoformat(),
            'tiene_imagenes_en_propuestas': False,
            'total_imagenes_documento': 0,
            'imagenes_detectadas': [],
            'propuestas_con_imagenes': [],
            'estado': 'VÁLIDO'
        }

        # Verificar si hay imágenes en el documento
        total_imagenes = contenido_extraido.get('estadisticas', {}).get('total_imagenes', 0)
        reporte['total_imagenes_documento'] = total_imagenes

        if total_imagenes > 0:
            # Obtener hojas con imágenes
            hojas_completas = contenido_extraido.get('contenido', {}).get('hojas_completas', [])
            propuestas = contenido_extraido.get('contenido', {}).get('propuestas', [])

            # Construir un mapa de hojas con imágenes
            hojas_con_imagenes = {}
            for hoja in hojas_completas:
                nombre_hoja = hoja.get('nombre')
                imagenes_hoja = hoja.get('imagenes', [])

                if len(imagenes_hoja) > 0:
                    hojas_con_imagenes[nombre_hoja] = imagenes_hoja

                    # Registrar las imágenes
                    for imagen in imagenes_hoja:
                        posicion = imagen.get('posicion', {})
                        reporte['imagenes_detectadas'].append({
                            'hoja': nombre_hoja,
                            'indice': imagen.get('indice'),
                            'formato': imagen.get('formato'),
                            'columna': posicion.get('columna') if posicion else 'desconocida',
                            'fila': posicion.get('fila') if posicion else 'desconocida',
                            'tamaño_bytes': imagen.get('tamaño_bytes')
                        })

            # Verificar si alguna propuesta está en una hoja con imágenes
            for propuesta in propuestas:
                hoja_propuesta = propuesta.get('hoja')
                fila_propuesta = propuesta.get('fila')

                if hoja_propuesta in hojas_con_imagenes:
                    # Hay imágenes en la misma hoja que la propuesta
                    imagenes_hoja = hojas_con_imagenes[hoja_propuesta]

                    # Verificar si hay imágenes cerca de la fila de la propuesta
                    imagenes_cercanas = []
                    for imagen in imagenes_hoja:
                        posicion = imagen.get('posicion', {})
                        if posicion:
                            fila_imagen = posicion.get('fila')
                            if fila_imagen is not None and fila_propuesta is not None:
                                # Si la imagen está dentro de +/- 10 filas de la propuesta
                                if abs(fila_imagen - fila_propuesta) <= 10:
                                    imagenes_cercanas.append(imagen)

                    if imagenes_cercanas or len(imagenes_hoja) > 0:
                        reporte['tiene_imagenes_en_propuestas'] = True
                        reporte['estado'] = 'ADVERTENCIA'

                        reporte['propuestas_con_imagenes'].append({
                            'numero': propuesta.get('numero'),
                            'hoja': hoja_propuesta,
                            'fila': fila_propuesta,
                            'observacion': propuesta.get('observacion_texto', '')[:100],
                            'advertencia': f'Hoja "{hoja_propuesta}" contiene {len(imagenes_hoja)} imagen(es)',
                            'imagenes_cercanas': len(imagenes_cercanas)
                        })

        return reporte

    def validar_archivo(self, nombre_archivo: str, contenido_extraido: Dict) -> Dict:
        """
        Valida un archivo (DOCX o XLSX) para detectar imágenes en propuestas

        Args:
            nombre_archivo: Nombre del archivo
            contenido_extraido: Contenido extraído por los procesadores

        Returns:
            Diccionario con el reporte de validación
        """
        tipo_archivo = contenido_extraido.get('tipo_archivo', '').upper()

        if tipo_archivo == 'DOCX':
            reporte = self.validar_propuestas_docx(nombre_archivo, contenido_extraido)
        elif tipo_archivo == 'XLSX':
            reporte = self.validar_propuestas_xlsx(nombre_archivo, contenido_extraido)
        else:
            reporte = {
                'nombre_archivo': nombre_archivo,
                'tipo_archivo': tipo_archivo,
                'fecha_validacion': datetime.now().isoformat(),
                'estado': 'ERROR',
                'error': f'Tipo de archivo no soportado: {tipo_archivo}'
            }

        self.reportes.append(reporte)
        return reporte

    def generar_reporte_consolidado(self) -> Dict:
        """
        Genera un reporte consolidado de todas las validaciones

        Returns:
            Diccionario con el reporte consolidado
        """
        total_archivos = len(self.reportes)
        archivos_con_advertencias = sum(1 for r in self.reportes if r.get('estado') == 'ADVERTENCIA')
        archivos_validos = sum(1 for r in self.reportes if r.get('estado') == 'VÁLIDO')
        total_imagenes = sum(r.get('total_imagenes_documento', 0) for r in self.reportes)

        reporte_consolidado = {
            'fecha_generacion': datetime.now().isoformat(),
            'total_archivos_validados': total_archivos,
            'archivos_validos': archivos_validos,
            'archivos_con_advertencias': archivos_con_advertencias,
            'total_imagenes_detectadas': total_imagenes,
            'resumen': {
                'estado_general': 'VÁLIDO' if archivos_con_advertencias == 0 else 'ADVERTENCIAS_ENCONTRADAS'
            },
            'reportes_individuales': self.reportes
        }

        # Crear lista de archivos problemáticos
        archivos_problematicos = [
            r for r in self.reportes
            if r.get('tiene_imagenes_en_propuestas', False)
        ]

        reporte_consolidado['archivos_con_imagenes_en_propuestas'] = archivos_problematicos

        return reporte_consolidado

    def limpiar_reportes(self):
        """Limpia la lista de reportes para empezar una nueva validación"""
        self.reportes = []


# Instancia global del validador
validator = ImageValidator()


def validar_archivo(nombre_archivo: str, contenido_extraido: Dict) -> Dict:
    """
    Función de conveniencia para validar un archivo

    Args:
        nombre_archivo: Nombre del archivo a validar
        contenido_extraido: Contenido extraído por los procesadores

    Returns:
        Diccionario con el reporte de validación
    """
    return validator.validar_archivo(nombre_archivo, contenido_extraido)


def generar_reporte_consolidado() -> Dict:
    """
    Función de conveniencia para generar reporte consolidado

    Returns:
        Diccionario con el reporte consolidado
    """
    return validator.generar_reporte_consolidado()


def limpiar_reportes():
    """Función de conveniencia para limpiar reportes"""
    validator.limpiar_reportes()
