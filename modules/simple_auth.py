"""
Módulo de Autenticación Simple - Sistema de Facturación Finkargo
Sistema de login con usuarios y contraseñas locales
"""

import streamlit as st
import hashlib
from typing import Optional, Dict


class SimpleAuthManager:
    """
    Gestor de autenticación simple para la aplicación.

    Usa usuarios y contraseñas configurados en secrets.toml
    """

    def __init__(self):
        """Inicializa el gestor de autenticación"""
        try:
            # Cargar usuarios desde secrets.toml
            self.users = dict(st.secrets["users"])
        except KeyError:
            st.error("❌ Error: No se encontró la configuración de usuarios en secrets.toml")
            self.users = {}

    def hash_password(self, password: str) -> str:
        """
        Genera hash SHA256 de una contraseña.

        Args:
            password: Contraseña en texto plano

        Returns:
            Hash de la contraseña
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_login(self, username: str, password: str) -> bool:
        """
        Verifica credenciales de usuario.

        Args:
            username: Nombre de usuario
            password: Contraseña

        Returns:
            True si las credenciales son correctas
        """
        if username not in self.users:
            return False

        # Verificar contraseña
        stored_password = self.users[username]

        # Si la contraseña almacenada es un hash (64 caracteres hex), comparar hashes
        if len(stored_password) == 64 and all(c in '0123456789abcdef' for c in stored_password.lower()):
            return self.hash_password(password) == stored_password
        else:
            # Contraseña en texto plano (para desarrollo)
            return password == stored_password

    def login(self) -> bool:
        """
        Muestra la interfaz de login y maneja la autenticación.

        Returns:
            True si el usuario está autenticado
        """
        # Verificar si ya está autenticado
        if 'authenticated' in st.session_state and st.session_state.authenticated:
            return True

        # Mostrar pantalla de login
        self._show_login_page()

        return False

    def logout(self) -> None:
        """Cierra la sesión del usuario"""
        st.session_state.authenticated = False
        st.session_state.username = None

    def get_current_user(self) -> Optional[str]:
        """
        Obtiene el nombre del usuario actual.

        Returns:
            Nombre de usuario o None
        """
        if 'username' in st.session_state:
            return st.session_state.username
        return None

    def _show_login_page(self) -> None:
        """Muestra la página de login"""
        st.markdown("""
            <div style='text-align: center; padding: 50px 20px 30px 20px;'>
                <h1 style='color: #0C147B; font-size: 42px; margin-bottom: 10px;'>
                    📊 Sistema de Facturación
                </h1>
                <h2 style='color: #6B7280; font-size: 24px; font-weight: 400; margin-bottom: 20px;'>
                    Finkargo
                </h2>
            </div>
        """, unsafe_allow_html=True)

        # CSS para ajustar el input de contraseña
        st.markdown("""
            <style>
            /* Contenedor del campo de contraseña - flex con gap */
            [data-testid="stForm"] div[data-baseweb="base-input"] {
                display: flex !important;
                gap: 10px !important;
                align-items: center !important;
            }

            /* Input de contraseña - 80% de ancho */
            [data-testid="stForm"] div[data-baseweb="base-input"] > div:first-child {
                flex: 0 0 80% !important;
                max-width: 80% !important;
            }

            /* Botón del ojo - más ancho, padding y centrado */
            [data-testid="stForm"] button[aria-label*="password"] {
                flex: 0 0 auto !important;
                width: auto !important;
                min-width: 60px !important;
                padding: 8px 16px !important;
                height: auto !important;
                margin: 0 !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }

            /* Ícono dentro del botón - centrado */
            [data-testid="stForm"] button[aria-label*="password"] svg {
                width: 20px !important;
                height: 20px !important;
                display: block !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # Formulario de login
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                st.markdown("### 🔑 Iniciar Sesión")

                username = st.text_input("👤 Usuario", placeholder="Ingresa tu usuario")
                password = st.text_input("🔒 Contraseña", type="password", placeholder="Ingresa tu contraseña")

                submit = st.form_submit_button("Iniciar Sesión", use_container_width=True, type="primary")

                if submit:
                    if not username or not password:
                        st.error("⚠️ Por favor ingresa usuario y contraseña")
                    elif self.verify_login(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.success("✅ Login exitoso!")
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")

    def show_user_info_sidebar(self) -> None:
        """Muestra información del usuario en el sidebar"""
        username = self.get_current_user()

        with st.sidebar:
            st.markdown("---")
            st.markdown("### 🔐 Sesión")

            if username:
                st.success(f"✓ Conectado como: **{username}**")
            else:
                st.info("✓ Sesión activa")

            st.markdown("")

            # Botón de logout
            if st.button("🚪 Cerrar Sesión", use_container_width=True, type="primary", key="logout_sidebar"):
                self.logout()
                st.rerun()
