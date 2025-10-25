"""
Módulo para procesar archivos Excel de Noova y Netsuite
Clase FileProcessor con funcionalidad completa de consolidación
"""

import pandas as pd
import json
import re
from datetime import datetime
from typing import Dict, Tuple, Optional
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileProcessor:
    """
    Procesador de archivos Excel para consolidación de facturas

    Maneja la lectura, consolidación y preparación de datos de:
    - Netsuite (.xls)
    - Facturas Noova (.xlsx)
    - Notas de Crédito (.xlsx)
    """

    def __init__(self, column_mapping_path: str, classification_rules_path: str):
        """
        Inicializa el procesador cargando configuraciones

        Args:
            column_mapping_path: Ruta al JSON de mapeo de columnas
            classification_rules_path: Ruta al JSON de reglas de clasificación
        """
        try:
            with open(column_mapping_path, 'r', encoding='utf-8') as f:
                self.column_mapping = json.load(f)

            with open(classification_rules_path, 'r', encoding='utf-8') as f:
                self.classification_rules = json.load(f)

            logger.info("✅ Configuraciones cargadas correctamente")
        except FileNotFoundError as e:
            logger.error(f"❌ Archivo de configuración no encontrado: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"❌ Error al decodificar JSON: {e}")
            raise

    def read_netsuite_file(self, file_path: str) -> pd.DataFrame:
        """
        Lee archivo Netsuite (.xls) y retorna DataFrame normalizado

        Args:
            file_path: Ruta al archivo .xls de Netsuite

        Returns:
            DataFrame con columnas: numero_factura, moneda, valor_netsuite
        """
        try:
            config = self.column_mapping['netsuite']
            sheet_name = config['sheet_name']
            cols = config['columns']

            # Intentar leer con openpyxl primero (soporta .xls y .xlsx modernos)
            # Si falla, intentar con xlrd (archivos .xls antiguos)
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
                logger.info("✅ Archivo leído con openpyxl (formato moderno)")
            except Exception as e1:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name, engine='xlrd')
                    logger.info("✅ Archivo leído con xlrd (formato antiguo)")
                except Exception as e2:
                    raise Exception(f"No se pudo leer el archivo con ningún engine. Openpyxl: {str(e1)}, Xlrd: {str(e2)}")

            # Renombrar columnas según mapeo
            df_renamed = df.rename(columns={
                cols['numero_factura']: 'numero_factura',
                cols['moneda']: 'moneda',
                cols['valor']: 'valor_netsuite'
            })

            # Seleccionar solo las columnas necesarias
            df_result = df_renamed[['numero_factura', 'moneda', 'valor_netsuite']].copy()

            # Limpiar y normalizar numero_factura
            df_result['numero_factura'] = df_result['numero_factura'].astype(str).str.strip().str.upper()

            # Convertir valor a numérico
            df_result['valor_netsuite'] = pd.to_numeric(df_result['valor_netsuite'], errors='coerce')

            # Remover filas sin número de factura válido
            df_result = df_result[df_result['numero_factura'].notna()]
            df_result = df_result[df_result['numero_factura'] != 'NAN']

            logger.info(f"✅ Netsuite: {len(df_result)} registros leídos de {file_path}")
            return df_result

        except Exception as e:
            logger.error(f"❌ Error al leer archivo Netsuite: {e}")
            raise

    def read_netsuite_nc_file(self, file_path: str) -> pd.DataFrame:
        """
        Lee archivo Netsuite Notas de Crédito (.xls) y retorna DataFrame normalizado

        Args:
            file_path: Ruta al archivo .xls de Netsuite NC

        Returns:
            DataFrame con columnas: numero_factura, moneda, valor_netsuite
        """
        try:
            config = self.column_mapping['netsuite_nc']
            sheet_name = config['sheet_name']
            cols = config['columns']

            # Intentar leer con openpyxl primero (soporta .xls y .xlsx modernos)
            # Si falla, intentar con xlrd (archivos .xls antiguos)
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
                logger.info("✅ Archivo NC leído con openpyxl (formato moderno)")
            except Exception as e1:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name, engine='xlrd')
                    logger.info("✅ Archivo NC leído con xlrd (formato antiguo)")
                except Exception as e2:
                    raise Exception(f"No se pudo leer el archivo NC con ningún engine. Openpyxl: {str(e1)}, Xlrd: {str(e2)}")

            # Renombrar columnas según mapeo
            df_renamed = df.rename(columns={
                cols['numero_factura']: 'numero_factura',
                cols['moneda']: 'moneda',
                cols['valor']: 'valor_netsuite'
            })

            # Seleccionar solo las columnas necesarias
            df_result = df_renamed[['numero_factura', 'moneda', 'valor_netsuite']].copy()

            # Limpiar y normalizar numero_factura
            df_result['numero_factura'] = df_result['numero_factura'].astype(str).str.strip().str.upper()

            # Convertir valor a numérico
            df_result['valor_netsuite'] = pd.to_numeric(df_result['valor_netsuite'], errors='coerce')

            # Remover filas sin número de factura válido
            df_result = df_result[df_result['numero_factura'].notna()]
            df_result = df_result[df_result['numero_factura'] != 'NAN']

            logger.info(f"✅ Netsuite NC: {len(df_result)} registros leídos de {file_path}")
            return df_result

        except Exception as e:
            logger.error(f"❌ Error al leer archivo Netsuite NC: {e}")
            raise

    def read_noova_file(self, file_path: str, file_type: str) -> pd.DataFrame:
        """
        Lee archivo Noova (.xlsx) de facturas o notas de crédito

        Args:
            file_path: Ruta al archivo .xlsx de Noova
            file_type: 'facturas' o 'notas_credito'

        Returns:
            DataFrame con columnas normalizadas y columna fuente_noova
        """
        try:
            # Determinar configuración según tipo
            config_key = f'noova_{file_type}'
            if config_key not in self.column_mapping:
                raise ValueError(f"Tipo de archivo desconocido: {file_type}")

            config = self.column_mapping[config_key]
            sheet_name = config['sheet_name']
            cols = config['columns']

            # Leer archivo
            df = pd.read_excel(file_path, sheet_name=sheet_name)

            # Renombrar columnas según mapeo
            df_renamed = df.rename(columns={
                cols['fecha']: 'fecha_facturacion',
                cols['numero_factura']: 'numero_factura',
                cols['nit']: 'nit_cliente',
                cols['nombre_cliente']: 'nombre_cliente',
                cols['email']: 'email_cliente',
                cols['estado']: 'estado',
                cols['envio']: 'envio',
                cols['codigo_operacion']: 'codigo_operacion',
                cols['concepto']: 'concepto'
            })

            # Seleccionar columnas necesarias
            columnas_resultado = [
                'fecha_facturacion', 'numero_factura', 'nit_cliente',
                'nombre_cliente', 'email_cliente', 'estado', 'envio',
                'codigo_operacion', 'concepto'
            ]

            df_result = df_renamed[columnas_resultado].copy()

            # Limpiar y normalizar numero_factura
            df_result['numero_factura'] = df_result['numero_factura'].astype(str).str.strip().str.upper()

            # Agregar columna de fuente
            df_result['fuente_noova'] = file_type

            # Remover filas sin número de factura válido
            df_result = df_result[df_result['numero_factura'].notna()]
            df_result = df_result[df_result['numero_factura'] != 'NAN']

            logger.info(f"✅ Noova {file_type}: {len(df_result)} registros leídos de {file_path}")
            return df_result

        except Exception as e:
            logger.error(f"❌ Error al leer archivo Noova ({file_type}): {e}")
            raise

    def extract_prefix(self, numero_factura: str) -> str:
        """
        Extrae el prefijo de un número de factura

        Args:
            numero_factura: Número de factura (ej: 'FE9133', 'ITPA5678')

        Returns:
            Prefijo encontrado o 'DESCONOCIDO'
        """
        if not isinstance(numero_factura, str):
            return 'DESCONOCIDO'

        numero_factura = numero_factura.strip().upper()

        # Orden de prioridad de prefijos (más largo primero)
        prefijos = ['NCFE', 'ITPA', 'ITGC', 'FE', 'GL']

        for prefijo in prefijos:
            if numero_factura.startswith(prefijo):
                return prefijo

        return 'DESCONOCIDO'

    def extract_consecutive(self, numero_factura: str) -> Optional[int]:
        """
        Extrae el número consecutivo de una factura

        Args:
            numero_factura: Número de factura (ej: 'FE9133', 'ITPA5678')

        Returns:
            Número consecutivo o None si no se encuentra
        """
        if not isinstance(numero_factura, str):
            return None

        # Buscar secuencia de dígitos al final
        match = re.search(r'(\d+)$', numero_factura.strip())

        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None

        return None

    def classify_concept(self, concepto: str) -> Tuple[str, str]:
        """
        Clasifica un concepto según las reglas de clasificación

        Args:
            concepto: Texto del concepto a clasificar

        Returns:
            Tupla (categoria, columna_destino)
        """
        if not isinstance(concepto, str) or not concepto.strip():
            return ('sin_clasificar', 'Sin Clasificar')

        concepto_clean = concepto.strip()
        concepto_lower = concepto_clean.lower()

        reglas = self.classification_rules.get('clasificacion_conceptos', {})

        # Primero buscar exact_match
        for categoria, config in reglas.items():
            exact_matches = config.get('exact_match', [])
            for exact in exact_matches:
                if concepto_clean == exact:
                    return (categoria, self._get_column_name(categoria))

        # Luego buscar por keywords (case-insensitive)
        for categoria, config in reglas.items():
            keywords = config.get('keywords', [])
            for keyword in keywords:
                if keyword.lower() in concepto_lower:
                    return (categoria, self._get_column_name(categoria))

        # Si no se encontró clasificación
        return ('sin_clasificar', 'Sin Clasificar')

    def _get_column_name(self, categoria: str) -> str:
        """
        Mapea categoría a nombre de columna destino

        Args:
            categoria: Categoría del concepto

        Returns:
            Nombre de la columna destino
        """
        mapeo = {
            'costos_fijos': 'Valor Costos Fijos',
            'seguro_iva': 'Seguro + Iva',
            'intereses_corriente': 'Int. Corriente Facturado FK',
            'intereses_mora': 'Int. Mora Facturado FK'
        }

        return mapeo.get(categoria, 'Sin Clasificar')

    def consolidate_data(
        self,
        df_netsuite: pd.DataFrame,
        df_facturas: pd.DataFrame,
        df_notas: Optional[pd.DataFrame] = None,
        df_netsuite_nc: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Consolida datos de Netsuite, Facturas y Notas de Crédito

        Args:
            df_netsuite: DataFrame de Netsuite Facturas
            df_facturas: DataFrame de Facturas Noova
            df_notas: DataFrame de Notas de Crédito Noova (opcional)
            df_netsuite_nc: DataFrame de Notas de Crédito Netsuite (opcional)

        Returns:
            DataFrame consolidado con todas las columnas necesarias
        """
        try:
            # Combinar facturas Noova y notas de crédito Noova
            if df_facturas is not None and not df_facturas.empty:
                if df_notas is not None and not df_notas.empty:
                    df_noova_combined = pd.concat([df_facturas, df_notas], ignore_index=True)
                    logger.info(f"📊 Combinando {len(df_facturas)} facturas Noova + {len(df_notas)} notas de crédito Noova")
                else:
                    df_noova_combined = df_facturas.copy()
                    logger.info(f"📊 Procesando {len(df_facturas)} facturas Noova (sin notas de crédito)")
            elif df_notas is not None and not df_notas.empty:
                # Solo hay notas de crédito Noova, sin facturas
                df_noova_combined = df_notas.copy()
                logger.info(f"📊 Procesando {len(df_notas)} notas de crédito Noova (sin facturas)")
            else:
                # No hay datos Noova
                df_noova_combined = None
                logger.warning("⚠️ No hay datos de Noova para procesar")

            # Combinar facturas Netsuite y notas de crédito Netsuite
            if df_netsuite is not None and not df_netsuite.empty:
                if df_netsuite_nc is not None and not df_netsuite_nc.empty:
                    df_netsuite_combined = pd.concat([df_netsuite, df_netsuite_nc], ignore_index=True)
                    logger.info(f"📊 Combinando {len(df_netsuite)} facturas Netsuite + {len(df_netsuite_nc)} notas de crédito Netsuite")
                else:
                    df_netsuite_combined = df_netsuite.copy()
                    logger.info(f"📊 Procesando {len(df_netsuite)} facturas Netsuite (sin notas de crédito)")
            elif df_netsuite_nc is not None and not df_netsuite_nc.empty:
                # Solo hay notas de crédito Netsuite, sin facturas
                df_netsuite_combined = df_netsuite_nc.copy()
                logger.info(f"📊 Procesando {len(df_netsuite_nc)} notas de crédito Netsuite (sin facturas)")
            else:
                # No hay datos Netsuite
                df_netsuite_combined = None
                logger.warning("⚠️ No hay datos de Netsuite para procesar")

            # LEFT JOIN: Noova como base, agregar datos de Netsuite
            if df_noova_combined is not None and df_netsuite_combined is not None:
                df_consolidated = df_noova_combined.merge(
                    df_netsuite_combined,
                    on='numero_factura',
                    how='left'
                )
            elif df_noova_combined is not None:
                # Solo hay datos Noova
                df_consolidated = df_noova_combined.copy()
                logger.warning("⚠️ Consolidación solo con datos de Noova (sin Netsuite)")
            elif df_netsuite_combined is not None:
                # Solo hay datos Netsuite
                df_consolidated = df_netsuite_combined.copy()
                logger.warning("⚠️ Consolidación solo con datos de Netsuite (sin Noova)")
            else:
                # No hay datos de ninguno
                raise ValueError("No hay datos para consolidar. Debes cargar al menos un archivo.")

            logger.info(f"🔗 JOIN completado: {len(df_consolidated)} registros")

            # Extraer prefijo y consecutivo
            df_consolidated['prefijo'] = df_consolidated['numero_factura'].apply(self.extract_prefix)
            df_consolidated['consecutivo'] = df_consolidated['numero_factura'].apply(self.extract_consecutive)

            # Clasificar conceptos
            clasificacion = df_consolidated['concepto'].apply(self.classify_concept)
            df_consolidated['categoria'] = clasificacion.apply(lambda x: x[0])
            df_consolidated['columna_destino'] = clasificacion.apply(lambda x: x[1])

            # Determinar tipo de factura y hoja destino según prefijo
            tipo_factura_map = self.classification_rules.get('tipo_factura_por_prefijo', {})

            df_consolidated['tipo_factura'] = df_consolidated['prefijo'].apply(
                lambda x: tipo_factura_map.get(x, {}).get('tipo', 'Desconocido')
            )

            df_consolidated['hoja_destino'] = df_consolidated['prefijo'].apply(
                lambda x: tipo_factura_map.get(x, {}).get('hoja_destino', 'Sin Hoja')
            )

            # Logging de resultados
            sin_valor = df_consolidated['valor_netsuite'].isna().sum()
            sin_clasificar = (df_consolidated['categoria'] == 'sin_clasificar').sum()

            logger.info(f"📊 Consolidación completada:")
            logger.info(f"  - Total registros: {len(df_consolidated)}")
            logger.info(f"  - Con valor Netsuite: {len(df_consolidated) - sin_valor}")
            logger.info(f"  - Sin valor Netsuite: {sin_valor}")
            logger.info(f"  - Clasificados: {len(df_consolidated) - sin_clasificar}")
            logger.info(f"  - Sin clasificar: {sin_clasificar}")

            return df_consolidated

        except Exception as e:
            logger.error(f"❌ Error en consolidación: {e}")
            raise

    def prepare_for_master_sheet(self, df_consolidated: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Prepara datos consolidados para archivo maestro (Excel con múltiples hojas)

        Args:
            df_consolidated: DataFrame consolidado

        Returns:
            Diccionario con DataFrames por hoja destino
        """
        try:
            datos_por_hoja = {}

            # Agrupar por hoja_destino
            hojas_unicas = df_consolidated['hoja_destino'].unique()

            for hoja in hojas_unicas:
                if hoja == 'Sin Hoja':
                    continue

                df_hoja = df_consolidated[df_consolidated['hoja_destino'] == hoja].copy()

                # Preparar según tipo de hoja
                if hoja == 'Relacion facturas Costos Fijos':
                    df_preparado = self._prepare_costos_fijos(df_hoja)
                elif hoja == 'Relación facturas mandato':
                    df_preparado = self._prepare_interes(df_hoja)
                else:
                    # Hoja genérica
                    df_preparado = df_hoja

                datos_por_hoja[hoja] = df_preparado
                logger.info(f"📄 Hoja '{hoja}': {len(df_preparado)} registros")

            return datos_por_hoja

        except Exception as e:
            logger.error(f"❌ Error al preparar hojas: {e}")
            raise

    def _prepare_costos_fijos(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara datos para hoja 'Relacion facturas Costos Fijos'

        Columnas: Codigo del desembolso, Valor Costos Fijos, Seguro + Iva,
        Int. Corriente Facturado FK, Int. Mora Facturado FK,
        (-) Retencio n en la Fuente, Valor Neto Facturado,
        Fecha Facturacion, # Factura, Validacion Consecutivo, Revision,
        Moneda, Estado, Envio, Fac de la nota Crédito
        """
        # Inicializar columnas de valores
        df['Valor Costos Fijos'] = 0.0
        df['Seguro + Iva'] = 0.0
        df['Int. Corriente Facturado FK'] = 0.0
        df['Int. Mora Facturado FK'] = 0.0

        # Distribuir valores según categoría
        for idx, row in df.iterrows():
            categoria = row['categoria']
            valor = row.get('valor_netsuite', 0)

            if pd.notna(valor):
                if categoria == 'costos_fijos':
                    df.at[idx, 'Valor Costos Fijos'] = valor
                elif categoria == 'seguro_iva':
                    df.at[idx, 'Seguro + Iva'] = valor
                elif categoria == 'intereses_corriente':
                    df.at[idx, 'Int. Corriente Facturado FK'] = valor
                elif categoria == 'intereses_mora':
                    df.at[idx, 'Int. Mora Facturado FK'] = valor

        # Calcular Valor Neto Facturado (suma de B+C+D+E+F)
        # Asumiendo que Retención en la Fuente es 0 por ahora
        df['(-) Retencio n en la Fuente'] = 0.0

        df['Valor Neto Facturado'] = (
            df['Valor Costos Fijos'] +
            df['Seguro + Iva'] +
            df['Int. Corriente Facturado FK'] +
            df['Int. Mora Facturado FK'] +
            df['(-) Retencio n en la Fuente']
        )

        # Preparar columnas finales (SIN TILDES para estandarización)
        df_result = pd.DataFrame({
            'Codigo del desembolso': df['codigo_operacion'],
            'Valor Costos Fijos': df['Valor Costos Fijos'],
            'Seguro + Iva': df['Seguro + Iva'],
            'Int. Corriente Facturado FK': df['Int. Corriente Facturado FK'],
            'Int. Mora Facturado FK': df['Int. Mora Facturado FK'],
            '(-) Retencion en la Fuente': df['(-) Retencio n en la Fuente'],
            'Valor Neto Facturado': df['Valor Neto Facturado'],
            'Fecha Facturacion': df['fecha_facturacion'],
            '# Factura': df['numero_factura'],
            'Validacion Consecutivo': df['consecutivo'],
            'Revision': '',  # Campo vacío para revisión manual
            'Moneda': df['moneda'],
            'Estado': df['estado'],
            'Envio': df['envio'],
            'Fac de la nota Credito': df['fuente_noova'].apply(
                lambda x: 'Nota Credito' if x == 'notas_credito' else ''
            )
        })

        return df_result

    def _prepare_interes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara datos para hoja 'Relación facturas mandato'

        Columnas: Código del desembolso, Mes facturación, Interés Corriente Facturado,
        Interés Mora Facturado Mandato, Valor Neto Facturado, Fecha Factura,
        # Factura, Validacion Consecutivo, Revision, Estado, Envio, Moneda,
        Fac de la nota Crédito
        """
        # Inicializar columnas de valores
        df['Interés Corriente Facturado'] = 0.0
        df['Interés Mora Facturado Mandato'] = 0.0

        # Distribuir valores según categoría
        for idx, row in df.iterrows():
            categoria = row['categoria']
            valor = row.get('valor_netsuite', 0)

            if pd.notna(valor):
                if categoria == 'intereses_corriente':
                    df.at[idx, 'Interés Corriente Facturado'] = valor
                elif categoria == 'intereses_mora':
                    df.at[idx, 'Interés Mora Facturado Mandato'] = valor

        # Calcular Valor Neto Facturado
        df['Valor Neto Facturado'] = (
            df['Interés Corriente Facturado'] +
            df['Interés Mora Facturado Mandato']
        )

        # Calcular Mes facturación (formato: 'ago-25')
        df['Mes facturación'] = df['fecha_facturacion'].apply(self._format_mes_facturacion)

        # Preparar columnas finales (SIN TILDES para estandarización)
        df_result = pd.DataFrame({
            'Codigo del desembolso': df['codigo_operacion'],
            'Mes facturacion': df['Mes facturación'],
            'Interes Corriente Facturado': df['Interés Corriente Facturado'],
            'Interes Mora Facturado Mandato': df['Interés Mora Facturado Mandato'],
            'Valor Neto Facturado': df['Valor Neto Facturado'],
            'Fecha Factura': df['fecha_facturacion'],
            '# Factura': df['numero_factura'],
            'Validacion Consecutivo': df['consecutivo'],
            'Revision': '',  # Campo vacío para revisión manual
            'Estado': df['estado'],
            'Envio': df['envio'],
            'Moneda': df['moneda'],
            'Fac de la nota Credito': df['fuente_noova'].apply(
                lambda x: 'Nota Credito' if x == 'notas_credito' else ''
            )
        })

        return df_result

    def _format_mes_facturacion(self, fecha) -> str:
        """
        Formatea fecha a formato 'ago-25' (mes-año)

        Args:
            fecha: Fecha a formatear

        Returns:
            String en formato 'mes-año' (ej: 'ago-25')
        """
        if pd.isna(fecha):
            return ''

        try:
            if isinstance(fecha, str):
                fecha = pd.to_datetime(fecha)

            # Mapeo de meses en español
            meses = {
                1: 'ene', 2: 'feb', 3: 'mar', 4: 'abr',
                5: 'may', 6: 'jun', 7: 'jul', 8: 'ago',
                9: 'sep', 10: 'oct', 11: 'nov', 12: 'dic'
            }

            mes = meses.get(fecha.month, '')
            año = str(fecha.year)[-2:]  # Últimos 2 dígitos del año

            return f"{mes}-{año}"

        except Exception:
            return ''

    def get_statistics(self, df_consolidated: pd.DataFrame) -> Dict:
        """
        Calcula estadísticas del DataFrame consolidado

        Args:
            df_consolidated: DataFrame consolidado

        Returns:
            Diccionario con estadísticas
        """
        try:
            stats = {
                'total_facturas': len(df_consolidated),
                'total_valor_cop': df_consolidated[
                    df_consolidated['moneda'] == 'COP'
                ]['valor_netsuite'].sum(),
                'total_valor_usd': df_consolidated[
                    df_consolidated['moneda'] == 'USD'
                ]['valor_netsuite'].sum(),
                'por_tipo': df_consolidated['tipo_factura'].value_counts().to_dict(),
                'por_categoria': df_consolidated['categoria'].value_counts().to_dict(),
                'sin_valor': int(df_consolidated['valor_netsuite'].isna().sum()),
                'sin_clasificar': int((df_consolidated['categoria'] == 'sin_clasificar').sum()),
                'facturas_por_hoja': df_consolidated['hoja_destino'].value_counts().to_dict()
            }

            logger.info("📊 Estadísticas calculadas correctamente")
            return stats

        except Exception as e:
            logger.error(f"❌ Error al calcular estadísticas: {e}")
            raise


def process_files(
    netsuite_path: str,
    facturas_path: str,
    notas_credito_path: Optional[str] = None,
    column_mapping_path: str = 'config/column_mapping.json',
    classification_rules_path: str = 'config/classification_rules.json'
) -> Tuple[Dict[str, pd.DataFrame], Dict]:
    """
    Función principal para procesar los 3 archivos Excel

    Args:
        netsuite_path: Ruta al archivo Netsuite (.xls)
        facturas_path: Ruta al archivo de Facturas (.xlsx)
        notas_credito_path: Ruta al archivo de Notas de Crédito (.xlsx) - opcional
        column_mapping_path: Ruta al JSON de mapeo de columnas
        classification_rules_path: Ruta al JSON de reglas de clasificación

    Returns:
        Tupla (datos_por_hoja, estadísticas)
    """
    logger.info("🚀 Iniciando procesamiento de archivos...")

    # Inicializar procesador
    processor = FileProcessor(column_mapping_path, classification_rules_path)

    # Leer archivos
    df_netsuite = processor.read_netsuite_file(netsuite_path)
    df_facturas = processor.read_noova_file(facturas_path, 'facturas')

    df_notas = None
    if notas_credito_path:
        df_notas = processor.read_noova_file(notas_credito_path, 'notas_credito')

    # Consolidar datos
    df_consolidated = processor.consolidate_data(df_netsuite, df_facturas, df_notas)

    # Preparar hojas del archivo maestro
    datos_por_hoja = processor.prepare_for_master_sheet(df_consolidated)

    # Calcular estadísticas
    stats = processor.get_statistics(df_consolidated)

    logger.info("✅ Procesamiento completado exitosamente")

    return datos_por_hoja, stats
