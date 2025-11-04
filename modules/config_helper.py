"""
Helper para manejar configuración en desarrollo y producción
Soporta lectura desde:
- Variables de entorno (Render, Railway, etc.)
- Streamlit secrets (desarrollo local)
"""

import os
import json
import streamlit as st
from typing import Dict, Any, Optional


def get_service_account_info() -> Optional[Dict[str, Any]]:
    """
    Obtiene la información del Service Account de Google

    Returns:
        Dict con la información del service account o None si no existe
    """
    # Opción 1: Variable de entorno (PRODUCCIÓN - Render, Railway, etc.)
    service_account_json = os.getenv('SERVICE_ACCOUNT_JSON')
    if service_account_json:
        try:
            return json.loads(service_account_json)
        except json.JSONDecodeError as e:
            st.error(f"❌ Error al parsear SERVICE_ACCOUNT_JSON: {str(e)}")
            return None

    # Opción 2: Archivo local (DESARROLLO)
    try:
        service_account_file = 'config/service_account.json'
        if os.path.exists(service_account_file):
            with open(service_account_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"❌ Error al leer service_account.json: {str(e)}")
        return None

    # Si no se encuentra en ningún lado
    st.error("❌ No se encontró configuración de Service Account")
    st.info("💡 En desarrollo: coloca `config/service_account.json`")
    st.info("💡 En producción: configura variable `SERVICE_ACCOUNT_JSON`")
    return None


def get_drive_folder_id() -> str:
    """
    Obtiene el ID de la carpeta de Google Drive

    Returns:
        String con el folder ID o string vacío
    """
    # Opción 1: Variable de entorno (PRODUCCIÓN)
    folder_id = os.getenv('drive_folder_id')
    if folder_id:
        return folder_id

    # Opción 2: Streamlit secrets (DESARROLLO)
    try:
        if 'drive_folder_id' in st.secrets:
            return st.secrets['drive_folder_id']
    except:
        pass

    return ""


def get_users() -> Dict[str, str]:
    """
    Obtiene el diccionario de usuarios autorizados

    Returns:
        Dict con {username: password}
    """
    # Opción 1: Variable de entorno JSON (PRODUCCIÓN)
    users_json = os.getenv('USERS_JSON')
    if users_json:
        try:
            return json.loads(users_json)
        except json.JSONDecodeError:
            st.error("❌ Error al parsear USERS_JSON")
            return {}

    # Opción 2: Streamlit secrets (DESARROLLO)
    try:
        if 'users' in st.secrets:
            return dict(st.secrets['users'])
    except:
        pass

    # Opción 3: Variables individuales (PRODUCCIÓN alternativa)
    # Ejemplo: USER_MARIA, USER_MALEJA
    users = {}
    for key, value in os.environ.items():
        if key.startswith('USER_'):
            username = key.replace('USER_', '').lower().replace('_', '.')
            users[username] = value

    if users:
        return users

    # Si no hay usuarios configurados
    st.error("❌ No se encontraron usuarios configurados")
    st.info("💡 En desarrollo: configura `users` en `.streamlit/secrets.toml`")
    st.info("💡 En producción: configura variable `USERS_JSON`")
    return {}


def is_production() -> bool:
    """
    Detecta si la aplicación está corriendo en producción

    Returns:
        True si está en producción, False si está en desarrollo
    """
    # Render usa esta variable
    if os.getenv('RENDER'):
        return True

    # Railway usa esta
    if os.getenv('RAILWAY_ENVIRONMENT'):
        return True

    # Streamlit Cloud usa esta
    if os.getenv('STREAMLIT_SHARING_MODE'):
        return True

    # Heroku usa esta
    if os.getenv('DYNO'):
        return True

    # Por defecto, asumimos desarrollo
    return False


def get_environment_name() -> str:
    """
    Obtiene el nombre del entorno actual

    Returns:
        'production' o 'development'
    """
    return 'production' if is_production() else 'development'


def log_config_info():
    """
    Muestra información de la configuración actual (solo en desarrollo)
    """
    if not is_production():
        st.sidebar.caption(f"🔧 Entorno: {get_environment_name()}")

        # Verificar service account
        if get_service_account_info():
            st.sidebar.caption("✅ Service Account: OK")
        else:
            st.sidebar.caption("❌ Service Account: No configurado")

        # Verificar drive folder
        if get_drive_folder_id():
            st.sidebar.caption("✅ Drive Folder ID: OK")
        else:
            st.sidebar.caption("❌ Drive Folder ID: No configurado")

        # Verificar usuarios
        users = get_users()
        if users:
            st.sidebar.caption(f"✅ Usuarios: {len(users)} configurados")
        else:
            st.sidebar.caption("❌ Usuarios: No configurados")
