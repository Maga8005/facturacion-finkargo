"""
Funciones auxiliares y utilidades
"""

from typing import Any, Dict, List
from datetime import datetime
import json


def load_json_config(file_path: str) -> Dict:
    """
    Carga un archivo de configuración JSON

    Args:
        file_path: Ruta al archivo JSON

    Returns:
        Diccionario con la configuración
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def save_json_config(data: Dict, file_path: str) -> bool:
    """
    Guarda un diccionario como JSON

    Args:
        data: Datos a guardar
        file_path: Ruta donde guardar

    Returns:
        True si fue exitoso
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error guardando JSON: {e}")
        return False


def format_currency(amount: float) -> str:
    """
    Formatea un número como moneda

    Args:
        amount: Cantidad a formatear

    Returns:
        String formateado como moneda
    """
    return f"${amount:,.2f}"


def format_date(date: datetime, format_str: str = "%Y-%m-%d") -> str:
    """
    Formatea una fecha

    Args:
        date: Fecha a formatear
        format_str: Formato deseado

    Returns:
        String con la fecha formateada
    """
    return date.strftime(format_str)


def log_error(message: str, error: Exception = None):
    """
    Registra un error en el log

    Args:
        message: Mensaje de error
        error: Excepción (opcional)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] ERROR: {message}"
    if error:
        log_message += f" - {str(error)}"
    print(log_message)
    # TODO: Implementar logging a archivo
