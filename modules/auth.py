"""
Módulo de Autenticación - Sistema de Facturación Finkargo
Maneja la autenticación de usuarios con Google OAuth
"""

import streamlit as st
from streamlit_google_auth import Authenticate
from typing import Optional, List


class AuthManager:
    """
    Gestor de autenticación para la aplicación.

    Implementa autenticación OAuth con Google y verifica usuarios autorizados.
    """

    def __init__(self):
        """Inicializa el gestor de autenticación con las credenciales de secrets.toml"""
        try:
            import os

            self.authorized_emails = st.secrets["authorized_users"]["emails"]

            # Ruta al archivo de credenciales
            credentials_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'google_credentials.json')

            # Inicializar el autenticador con las credenciales del archivo JSON
            self.authenticator = Authenticate(
                secret_credentials_path=credentials_path,
                cookie_name='facturacion_finkargo_auth',
                cookie_key='facturacion_auth_key',
                redirect_uri=st.secrets.get("redirect_uri", "http://localhost:8501"),
            )
        except KeyError as e:
            st.error(f"❌ Error de configuración: Falta la clave {str(e)} en secrets.toml")
            raise
        except FileNotFoundError:
            st.error(f"❌ Error: No se encontró el archivo de credenciales en {credentials_path}")
            raise

    def login(self) -> bool:
        """
        Muestra la interfaz de login y maneja la autenticación.

        Returns:
            bool: True si el usuario está autenticado y autorizado, False en caso contrario
        """
        # Verificar si ya está autenticado
        if self.is_authenticated():
            return True

        # Mostrar pantalla de login
        self._show_login_page()

        # Verificar autenticación y autorización después de mostrar login
        return self.is_authenticated()

    def is_authenticated(self) -> bool:
        """
        Verifica si el usuario está autenticado y autorizado.

        Returns:
            bool: True si está autenticado y autorizado, False en caso contrario
        """
        # Ejecutar el chequeo de autenticación
        self.authenticator.check_authentification()

        # Verificar si hay información de usuario
        if not hasattr(st.session_state, 'user_info') or st.session_state.user_info is None:
            return False

        if not isinstance(st.session_state.user_info, dict):
            return False

        user_email = st.session_state.user_info.get('email')

        if not user_email:
            return False

        # Verificar si el usuario está autorizado
        if not self.is_authorized(user_email):
            self._show_unauthorized_page(user_email)
            return False

        return True

    def is_authorized(self, email: str) -> bool:
        """
        Verifica si un email está en la lista de usuarios autorizados.

        Args:
            email: Email del usuario a verificar

        Returns:
            bool: True si está autorizado, False en caso contrario
        """
        return email.lower() in [e.lower() for e in self.authorized_emails]

    def logout(self) -> None:
        """Cierra la sesión del usuario"""
        self.authenticator.logout()
        if 'user_info' in st.session_state:
            st.session_state.user_info = None
        # Limpiar todas las claves relacionadas con autenticación
        keys_to_clear = [key for key in st.session_state.keys() if 'auth' in key.lower() or 'token' in key.lower()]
        for key in keys_to_clear:
            del st.session_state[key]

    def get_user_info(self) -> Optional[dict]:
        """
        Obtiene la información del usuario autenticado.

        Returns:
            dict: Información del usuario o None si no está autenticado
        """
        if not hasattr(st.session_state, 'user_info') or st.session_state.user_info is None:
            return None

        return {
            'email': st.session_state.user_info.get('email', ''),
            'name': st.session_state.user_info.get('name', st.session_state.user_info.get('email', '').split('@')[0]),
        }

    def _show_login_page(self) -> None:
        """Muestra la página de login con estilos personalizados"""
        st.markdown("""
            <div style='text-align: center; padding: 50px 20px;'>
                <h1 style='color: #0C147B; font-size: 42px; margin-bottom: 10px;'>
                    📊 Sistema de Facturación
                </h1>
                <h2 style='color: #6B7280; font-size: 24px; font-weight: 400; margin-bottom: 40px;'>
                    Finkargo
                </h2>
                <div style='background: linear-gradient(135deg, #0C147B 0%, #1E3A8A 100%);
                            padding: 40px;
                            border-radius: 16px;
                            box-shadow: 0 10px 30px rgba(12, 20, 123, 0.15);
                            max-width: 500px;
                            margin: 0 auto;'>
                    <h3 style='color: white; font-size: 20px; margin-bottom: 20px;'>
                        🔐 Acceso Restringido
                    </h3>
                    <p style='color: #E5E7EB; font-size: 16px; margin-bottom: 30px;'>
                        Este sistema es exclusivo para el equipo de facturación.
                        Inicia sesión con tu cuenta de Google autorizada.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Botón de login centrado
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            self.authenticator.login()

    def _show_unauthorized_page(self, email: str) -> None:
        """
        Muestra mensaje de acceso no autorizado.

        Args:
            email: Email del usuario no autorizado
        """
        st.markdown(f"""
            <div style='text-align: center; padding: 50px 20px;'>
                <div style='background: #FEF2F2;
                            border: 2px solid #FCA5A5;
                            padding: 40px;
                            border-radius: 16px;
                            max-width: 600px;
                            margin: 0 auto;'>
                    <h2 style='color: #DC2626; font-size: 28px; margin-bottom: 15px;'>
                        ⛔ Acceso No Autorizado
                    </h2>
                    <p style='color: #991B1B; font-size: 16px; margin-bottom: 10px;'>
                        La cuenta <strong>{email}</strong> no tiene permisos para acceder a este sistema.
                    </p>
                    <p style='color: #7F1D1D; font-size: 14px;'>
                        Si crees que esto es un error, contacta al administrador del sistema.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Botón de logout
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                self.logout()
                st.rerun()

    def show_user_info_sidebar(self) -> None:
        """Muestra información del usuario en el sidebar"""
        # Intentar obtener información del usuario
        user_info = self.get_user_info()

        with st.sidebar:
            st.markdown("---")
            st.markdown("### 🔐 Sesión")

            if user_info and user_info.get('email'):
                st.success(f"✓ Conectado como: **{user_info.get('name', 'Usuario')}**")
                st.caption(f"📧 {user_info['email']}")
            else:
                st.info("✓ Sesión activa")

            st.markdown("")

            # Botón de logout siempre visible con key única
            if st.button("🚪 Cerrar Sesión", use_container_width=True, type="primary", key="logout_button"):
                self.logout()
                st.rerun()
