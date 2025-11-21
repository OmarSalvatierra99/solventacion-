"""
Procesador por Lotes
Punto de entrada principal para procesar múltiples archivos DOCX y XLSX
Genera base de datos consolidada y reportes de validación
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from tqdm import tqdm

# Importar procesadores
from processors.docx_processor_optimized import process_docx
from processors.xlsx_processor_optimized import process_xlsx

# Importar módulos propios
from metadata_analyzer import analizar_archivo
from image_validator import validar_archivo, generar_reporte_consolidado, limpiar_reportes
from database_consolidator import (
    agregar_datos_archivo,
    generar_excel_consolidado,
    obtener_estadisticas,
    limpiar_datos
)


class BatchProcessor:
    """
    Procesador por lotes para análisis masivo de documentos
    """

    def __init__(self, carpeta_entrada: str = 'ejemplos', carpeta_salida: str = 'resultados_consolidados'):
        """
        Inicializa el procesador por lotes

        Args:
            carpeta_entrada: Carpeta donde se encuentran los archivos a procesar
            carpeta_salida: Carpeta donde se guardarán los resultados
        """
        self.carpeta_entrada = Path(carpeta_entrada)
        self.carpeta_salida = Path(carpeta_salida)
        self.carpeta_salida.mkdir(exist_ok=True)

        # Configurar logging
        self._configurar_logging()

        # Estadísticas de procesamiento
        self.stats = {
            'total_archivos': 0,
            'archivos_exitosos': 0,
            'archivos_con_error': 0,
            'total_propuestas': 0,
            'archivos_con_imagenes': 0
        }

    def _configurar_logging(self):
        """Configura el sistema de logging"""
        log_dir = self.carpeta_salida / 'logs'
        log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f'procesamiento_{timestamp}.log'

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Iniciando procesamiento por lotes")
        self.logger.info(f"Carpeta de entrada: {self.carpeta_entrada}")
        self.logger.info(f"Carpeta de salida: {self.carpeta_salida}")

    def buscar_archivos(self) -> List[Path]:
        """
        Busca todos los archivos DOCX y XLSX en la carpeta de entrada

        Returns:
            Lista de rutas de archivos encontrados
        """
        archivos = []

        # Buscar archivos DOCX
        archivos.extend(self.carpeta_entrada.glob('*.docx'))
        archivos.extend(self.carpeta_entrada.glob('*.DOCX'))

        # Buscar archivos XLSX
        archivos.extend(self.carpeta_entrada.glob('*.xlsx'))
        archivos.extend(self.carpeta_entrada.glob('*.XLSX'))

        # Filtrar archivos temporales de Office (que empiezan con ~$)
        archivos = [f for f in archivos if not f.name.startswith('~$')]

        self.logger.info(f"Encontrados {len(archivos)} archivos para procesar")
        return sorted(archivos)

    def procesar_archivo(self, ruta_archivo: Path) -> Dict:
        """
        Procesa un archivo individual

        Args:
            ruta_archivo: Ruta del archivo a procesar

        Returns:
            Diccionario con el resultado del procesamiento
        """
        self.logger.info(f"Procesando: {ruta_archivo.name}")

        resultado = {
            'nombre_archivo': ruta_archivo.name,
            'ruta': str(ruta_archivo),
            'exito': False,
            'error': None
        }

        try:
            # 1. Extraer contenido según el tipo de archivo
            extension = ruta_archivo.suffix.lower()

            if extension == '.docx':
                contenido_extraido = process_docx(str(ruta_archivo))
            elif extension == '.xlsx':
                contenido_extraido = process_xlsx(str(ruta_archivo))
            else:
                raise ValueError(f"Tipo de archivo no soportado: {extension}")

            # Verificar si la extracción fue exitosa
            if not contenido_extraido.get('extraccion_exitosa', False):
                raise Exception(contenido_extraido.get('error', 'Error desconocido en la extracción'))

            # 2. Analizar metadatos
            metadatos = analizar_archivo(str(ruta_archivo), contenido_extraido)

            # 3. Validar imágenes en propuestas
            reporte_imagenes = validar_archivo(str(ruta_archivo), contenido_extraido)

            # 4. Agregar a la base de datos consolidada
            agregar_datos_archivo(metadatos, contenido_extraido)

            # 5. Actualizar estadísticas
            num_propuestas = len(contenido_extraido.get('contenido', {}).get('propuestas', []))
            self.stats['total_propuestas'] += num_propuestas
            self.stats['archivos_exitosos'] += 1

            if reporte_imagenes.get('tiene_imagenes_en_propuestas', False):
                self.stats['archivos_con_imagenes'] += 1

            # 6. Guardar resultado individual
            self._guardar_resultado_individual(ruta_archivo.stem, {
                'metadatos': metadatos,
                'contenido': contenido_extraido,
                'validacion_imagenes': reporte_imagenes
            })

            resultado['exito'] = True
            resultado['metadatos'] = metadatos
            resultado['num_propuestas'] = num_propuestas

            self.logger.info(f"✓ {ruta_archivo.name}: {num_propuestas} propuestas extraídas")

        except Exception as e:
            self.logger.error(f"✗ Error procesando {ruta_archivo.name}: {str(e)}")
            resultado['error'] = str(e)
            self.stats['archivos_con_error'] += 1

        return resultado

    def _guardar_resultado_individual(self, nombre_base: str, resultado: Dict):
        """
        Guarda el resultado individual de un archivo en JSON

        Args:
            nombre_base: Nombre base del archivo (sin extensión)
            resultado: Diccionario con el resultado completo
        """
        archivo_salida = self.carpeta_salida / 'individuales' / f'{nombre_base}_resultado.json'
        archivo_salida.parent.mkdir(exist_ok=True)

        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)

    def procesar_todos(self):
        """
        Procesa todos los archivos encontrados en la carpeta de entrada
        """
        print("\n" + "=" * 80)
        print("  PROCESADOR DE DOCUMENTOS DE SOLVENTACIÓN")
        print("  Análisis Automático de Archivos DOCX y XLSX")
        print("=" * 80 + "\n")

        # Limpiar datos previos
        limpiar_datos()
        limpiar_reportes()

        # Buscar archivos
        archivos = self.buscar_archivos()

        if not archivos:
            self.logger.warning("No se encontraron archivos para procesar")
            print("⚠ No se encontraron archivos en la carpeta de entrada")
            return

        self.stats['total_archivos'] = len(archivos)

        # Procesar cada archivo con barra de progreso
        print(f"\n📂 Procesando {len(archivos)} archivos...\n")

        resultados = []
        for archivo in tqdm(archivos, desc="Progreso", unit="archivo"):
            resultado = self.procesar_archivo(archivo)
            resultados.append(resultado)

        # Generar reportes consolidados
        print("\n📊 Generando reportes consolidados...\n")
        self._generar_reportes_finales()

        # Mostrar resumen
        self._mostrar_resumen()

        print("\n✓ Procesamiento completado exitosamente\n")

    def _generar_reportes_finales(self):
        """Genera todos los reportes finales"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        try:
            # 1. Base de datos consolidada en Excel
            ruta_excel = self.carpeta_salida / f'base_datos_consolidada_{timestamp}.xlsx'
            generar_excel_consolidado(str(ruta_excel))
            self.logger.info(f"Base de datos consolidada: {ruta_excel}")

            # 2. Reporte de imágenes en JSON
            reporte_imagenes = generar_reporte_consolidado()
            ruta_imagenes = self.carpeta_salida / f'reporte_imagenes_{timestamp}.json'
            with open(ruta_imagenes, 'w', encoding='utf-8') as f:
                json.dump(reporte_imagenes, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Reporte de imágenes: {ruta_imagenes}")

            # 3. Estadísticas consolidadas
            estadisticas = obtener_estadisticas()
            ruta_stats = self.carpeta_salida / f'estadisticas_{timestamp}.json'
            with open(ruta_stats, 'w', encoding='utf-8') as f:
                json.dump(estadisticas, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Estadísticas: {ruta_stats}")

            # 4. Resumen de procesamiento
            resumen = {
                'fecha_procesamiento': datetime.now().isoformat(),
                'carpeta_entrada': str(self.carpeta_entrada),
                'carpeta_salida': str(self.carpeta_salida),
                'estadisticas_procesamiento': self.stats,
                'estadisticas_consolidadas': estadisticas,
                'archivos_salida': {
                    'base_datos': str(ruta_excel),
                    'reporte_imagenes': str(ruta_imagenes),
                    'estadisticas': str(ruta_stats)
                }
            }

            ruta_resumen = self.carpeta_salida / f'resumen_procesamiento_{timestamp}.json'
            with open(ruta_resumen, 'w', encoding='utf-8') as f:
                json.dump(resumen, f, ensure_ascii=False, indent=2)

            print(f"  ✓ Base de datos consolidada: {ruta_excel.name}")
            print(f"  ✓ Reporte de imágenes: {ruta_imagenes.name}")
            print(f"  ✓ Estadísticas: {ruta_stats.name}")
            print(f"  ✓ Resumen: {ruta_resumen.name}")

        except Exception as e:
            self.logger.error(f"Error generando reportes finales: {str(e)}")
            print(f"  ✗ Error generando reportes: {str(e)}")

    def _mostrar_resumen(self):
        """Muestra un resumen del procesamiento en la consola"""
        print("\n" + "=" * 80)
        print("  RESUMEN DE PROCESAMIENTO")
        print("=" * 80)
        print(f"  Total de archivos procesados:      {self.stats['total_archivos']}")
        print(f"  Archivos exitosos:                  {self.stats['archivos_exitosos']} ✓")
        print(f"  Archivos con errores:               {self.stats['archivos_con_error']} ✗")
        print(f"  Total de propuestas extraídas:      {self.stats['total_propuestas']}")
        print(f"  Archivos con imágenes en propuestas: {self.stats['archivos_con_imagenes']}")
        print("=" * 80 + "\n")

        # Mostrar estadísticas consolidadas
        try:
            stats_consolidadas = obtener_estadisticas()
            print("  DISTRIBUCIÓN DE DATOS")
            print("  " + "-" * 76)
            print(f"  Entes encontrados:                  {stats_consolidadas.get('total_entes', 0)}")
            print(f"  Fuentes de financiamiento:          {stats_consolidadas.get('total_fuentes', 0)}")
            print(f"  Registros en base de datos:         {stats_consolidadas.get('total_registros', 0)}")
            print("=" * 80 + "\n")
        except:
            pass


def main():
    """Función principal para ejecutar desde línea de comandos"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Procesador por lotes de documentos de solventación',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Procesar archivos de la carpeta 'ejemplos'
  python batch_processor.py

  # Especificar carpeta de entrada y salida
  python batch_processor.py --entrada ./mis_documentos --salida ./resultados

  # Ver ayuda
  python batch_processor.py --help
        """
    )

    parser.add_argument(
        '--entrada',
        type=str,
        default='ejemplos',
        help='Carpeta de entrada con archivos DOCX y XLSX (default: ejemplos)'
    )

    parser.add_argument(
        '--salida',
        type=str,
        default='resultados_consolidados',
        help='Carpeta de salida para resultados (default: resultados_consolidados)'
    )

    args = parser.parse_args()

    # Verificar que la carpeta de entrada existe
    if not Path(args.entrada).exists():
        print(f"✗ Error: La carpeta de entrada '{args.entrada}' no existe")
        sys.exit(1)

    # Crear y ejecutar procesador
    processor = BatchProcessor(
        carpeta_entrada=args.entrada,
        carpeta_salida=args.salida
    )

    try:
        processor.procesar_todos()
    except KeyboardInterrupt:
        print("\n\n⚠ Procesamiento interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error fatal: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
