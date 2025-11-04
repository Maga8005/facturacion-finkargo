"""
Sistema de Consolidación de Facturas - Finkargo
Aplicación Streamlit para procesar y consolidar datos de facturación
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from modules.drive_manager import DriveManager
from modules.file_processor import FileProcessor
from modules.simple_auth import SimpleAuthManager
import tempfile
import os
import time
from io import BytesIO

# Configuración de la página
st.set_page_config(
    page_title="Facturación Finkargo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar estilos CSS personalizados
def load_css():
    """Carga el archivo CSS personalizado con forzado de recarga"""
    try:
        import os
        import streamlit.components.v1 as components

        # Obtener timestamp para forzar recarga
        css_file = 'assets/styles.css'
        if os.path.exists(css_file):
            with open(css_file, 'r', encoding='utf-8') as f:
                css = f.read()
                # Agregar timestamp como comentario para forzar recarga
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

                # Inyectar solo CSS (sin JavaScript visible)
                st.markdown(f'''
                <style>
                /* CSS v{timestamp} */
                {css}

                /* Fix adicional para forzar texto blanco SOLO en botones primary */
                button[kind="primary"] {{
                    color: white !important;
                }}

                button[kind="primary"] * {{
                    color: white !important;
                }}

                /* Ocultar botón de Deploy y otros elementos de Streamlit */
                #MainMenu {{visibility: hidden;}}
                footer {{visibility: hidden;}}
                .stDeployButton {{display: none;}}
                [data-testid="stToolbar"] {{display: none;}}
                </style>
                ''', unsafe_allow_html=True)

                # Inyectar JavaScript de forma correcta usando components.html
                components.html(
                    """
                    <script>
                    // Buscar el parent window (Streamlit)
                    const parentWindow = window.parent;

                    function forceWhiteButtonText() {
                        const doc = parentWindow.document;
                        // Solo aplicar a botones primary
                        const buttons = doc.querySelectorAll('button[kind="primary"]');

                        buttons.forEach(function(button) {
                            button.style.setProperty('color', 'white', 'important');
                            const children = button.querySelectorAll('*');
                            children.forEach(function(child) {
                                child.style.setProperty('color', 'white', 'important');
                            });
                        });
                    }

                    function forceSidebarOpen() {
                        const doc = parentWindow.document;

                        // Buscar el sidebar
                        const sidebar = doc.querySelector('section[data-testid="stSidebar"]');

                        if (sidebar) {
                            // Forzar que esté visible
                            sidebar.style.display = 'block';
                            sidebar.style.visibility = 'visible';
                            sidebar.style.opacity = '1';
                            sidebar.setAttribute('aria-expanded', 'true');

                            // Remover clases de colapsado
                            sidebar.classList.remove('collapsed');
                        }

                        // OCULTAR COMPLETAMENTE el botón de toggle del sidebar
                        const toggleButtons = doc.querySelectorAll(
                            '[data-testid="collapsedControl"], button[data-testid="collapsedControl"], button[kind="header"], button[data-testid="baseButton-header"], .st-emotion-cache-qmp9ai, button.st-emotion-cache-qmp9ai, .e6f82ta8'
                        );

                        toggleButtons.forEach(function(btn) {
                            btn.style.display = 'none';
                            btn.style.visibility = 'hidden';
                            btn.style.opacity = '0';
                            btn.style.pointerEvents = 'none';
                            btn.style.width = '0';
                            btn.style.height = '0';
                            btn.remove(); // Eliminar del DOM directamente
                        });

                        // También buscar por aria-label
                        const ariaButtons = doc.querySelectorAll('button[aria-label*="sidebar"], button[aria-label*="Sidebar"]');
                        ariaButtons.forEach(function(btn) {
                            btn.style.display = 'none';
                            btn.style.visibility = 'hidden';
                            btn.remove();
                        });

                        // Buscar cualquier botón que esté justo antes o después del sidebar
                        const sidebarButtons = doc.querySelectorAll('section[data-testid="stSidebar"] ~ button, section[data-testid="stSidebar"] + button');
                        sidebarButtons.forEach(function(btn) {
                            if (btn.innerText === '' || btn.querySelector('svg')) {
                                btn.style.display = 'none';
                                btn.remove();
                            }
                        });
                    }

                    // Ejecutar después de cargar
                    setTimeout(forceWhiteButtonText, 500);
                    setTimeout(forceWhiteButtonText, 1000);
                    setTimeout(forceWhiteButtonText, 2000);

                    setTimeout(forceSidebarOpen, 100);
                    setTimeout(forceSidebarOpen, 500);
                    setTimeout(forceSidebarOpen, 1000);
                    setTimeout(forceSidebarOpen, 2000);

                    // Observer para cambios en el DOM
                    const observer = new MutationObserver(function() {
                        forceWhiteButtonText();
                        forceSidebarOpen();
                    });
                    observer.observe(parentWindow.document.body, { childList: true, subtree: true });
                    </script>
                    """,
                    height=0,
                    width=0,
                )
        else:
            st.error(f"⚠️ Archivo CSS no encontrado en: {os.path.abspath(css_file)}")
    except Exception as e:
        st.error(f"❌ Error al cargar estilos: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

# Aplicar estilos
load_css()

# ==================== SISTEMA DE AUTENTICACIÓN ====================

# Inicializar gestor de autenticación
if 'auth_manager' not in st.session_state:
    st.session_state.auth_manager = SimpleAuthManager()

auth_manager = st.session_state.auth_manager

# Verificar autenticación
if not auth_manager.login():
    st.stop()  # Detener ejecución si no está autenticado

# Usuario autenticado - Mostrar botón de logout en sidebar
auth_manager.show_user_info_sidebar()

# ==================== APLICACIÓN PRINCIPAL ====================

# Inicializar session state
if 'consolidated_data' not in st.session_state:
    st.session_state.consolidated_data = None
if 'drive_manager' not in st.session_state:
    st.session_state.drive_manager = None
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'stats' not in st.session_state:
    st.session_state.stats = None
if 'datos_por_hoja' not in st.session_state:
    st.session_state.datos_por_hoja = None
if 'metadata' not in st.session_state:
    st.session_state.metadata = None
if 'master_data' not in st.session_state:
    st.session_state.master_data = None
if 'master_loaded' not in st.session_state:
    st.session_state.master_loaded = False

# Función helper para Drive Manager
@st.cache_resource
def get_drive_manager_cached():
    """Obtener o crear instancia de DriveManager (con caché)"""
    try:
        return DriveManager()
    except Exception as e:
        st.error(f"Error al inicializar DriveManager: {str(e)}")
        return None

def get_drive_manager():
    """Obtener o crear instancia de DriveManager"""
    try:
        if st.session_state.drive_manager is None:
            st.session_state.drive_manager = get_drive_manager_cached()
        return st.session_state.drive_manager
    except:
        return None

# ==================== HELPER FUNCTIONS PARA UI ====================

def create_card(title, content, card_type="default", icon=""):
    """
    Crea una card personalizada con estilos consistentes

    Args:
        title: Título de la card
        content: Contenido HTML o texto
        card_type: "default", "info", "success", "warning"
        icon: Emoji o icono para el título
    """
    card_class = {
        "default": "custom-card",
        "info": "custom-card card-info",
        "success": "custom-card card-success",
        "warning": "custom-card card-warning"
    }

    st.markdown(f"""
    <div class='{card_class.get(card_type, "custom-card")}'>
        <h3 style='font-size: 18px; font-weight: 600; color: #0C147B; margin-bottom: 8px;'>
            {icon} {title}
        </h3>
        <div style='font-size: 14px; color: #6B7280;'>
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_upload_card(title, subtitle, file_key, file_types, is_optional=False):
    """
    Crea una card de carga de archivos compacta

    Args:
        title: Título de la sección
        subtitle: Subtítulo descriptivo
        file_key: Key única para el file_uploader
        file_types: Lista de tipos de archivo aceptados
        is_optional: Si es opcional mostrar label
    """
    optional_text = " (Opcional)" if is_optional else ""

    st.markdown(f"""
    <div class='upload-card'>
        <div style='margin-bottom: 12px;'>
            <div style='font-size: 16px; font-weight: 600; color: #0C147B;'>
                📄 {title}
            </div>
            <div style='font-size: 13px; color: #6B7280;'>
                {subtitle}{optional_text}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        f"Subir {title}",
        type=file_types,
        key=file_key,
        label_visibility="collapsed"
    )

    if uploaded_file:
        st.success(f"✅ {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")

    return uploaded_file

def create_metric_card(value, label, highlight=False):
    """
    Crea una card de métrica compacta

    Args:
        value: Valor numérico a mostrar
        label: Etiqueta de la métrica
        highlight: Si debe destacarse (borde azul)
    """
    border_style = "border: 2px solid #3C47D3;" if highlight else "border: 1px solid #D1D5DB;"
    color = "#3C47D3" if highlight else "#6B7280"

    st.markdown(f"""
    <div style='background: white; {border_style} border-radius: 12px; padding: 20px; text-align: center;'>
        <div style='font-size: 36px; font-weight: 700; color: {color}; margin-bottom: 8px;'>
            {value:,}
        </div>
        <div style='font-size: 14px; color: #6B7280; font-weight: 600;'>
            {label}
        </div>
    </div>
    """, unsafe_allow_html=True)

# Título principal compacto
st.markdown("""
    <div style='text-align: center; margin-bottom: 1.5rem;'>
        <h1 style='font-size: 32px; font-weight: 700; color: #050A53; margin-bottom: 0.5rem; margin-top: 0;'>
            📊 Sistema de Consolidación de Facturas
        </h1>
        <p style='font-size: 14px; color: #6B7280; margin: 0;'>
            Sistema para consolidar facturas de Noova y Netsuite
        </p>
    </div>
""", unsafe_allow_html=True)

# Sección de Google Drive - Disponible en contenido principal
drive_manager_main = get_drive_manager()
drive_connected = drive_manager_main and drive_manager_main.is_authenticated()

st.markdown("""
    <div style='background: white; border: 2px solid #3C47D3; border-radius: 12px; padding: 20px; margin-bottom: 24px;'>
        <div style='display: flex; align-items: center; justify-content: space-between; gap: 20px;'>
            <div style='flex: 1;'>
                <div style='font-size: 16px; font-weight: 600; color: #0C147B; margin-bottom: 8px;'>
                    🔐 Conexión con Google Drive
                </div>
                <div style='font-size: 13px; color: #6B7280;'>
                    Conecta tu cuenta para subir reportes, consultar archivo Master y buscar PDFs de facturas
                </div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Mostrar estado y proceso de conexión
if drive_connected:
    # Usuario conectado
    col_status, col_button = st.columns([2, 1])

    with col_status:
        st.markdown("""
            <div style='background: #D1FAE5; border: 1px solid #10B981; border-radius: 8px; padding: 12px; display: inline-block;'>
                <span style='color: #065F46; font-weight: 600;'>✅ Conectado a Google Drive</span>
            </div>
        """, unsafe_allow_html=True)
        st.caption("✓ Acceso completo a tu cuenta de Drive")

    with col_button:
        if st.button("🔓 Desconectar", use_container_width=True, key="btn_disconnect_main"):
            # Eliminar credenciales
            if 'google_drive_creds' in st.session_state:
                del st.session_state.google_drive_creds
            if 'drive_manager' in st.session_state:
                del st.session_state.drive_manager
            if 'oauth_flow' in st.session_state:
                del st.session_state.oauth_flow

            # Eliminar archivo de token
            import os
            if os.path.exists('token.json'):
                os.remove('token.json')

            st.success("✅ Desconectado correctamente")
            st.rerun()
else:
    # Usuario NO conectado - Mostrar proceso de autenticación
    st.markdown("""
        <div style='background: #FEF3C7; border: 1px solid #F59E0B; border-radius: 8px; padding: 12px; margin-bottom: 16px;'>
            <span style='color: #92400E; font-weight: 600;'>⚠️ No conectado a Google Drive</span>
        </div>
    """, unsafe_allow_html=True)

    # Verificar credenciales
    try:
        client_id = st.secrets.get("client_id", "")
        client_secret = st.secrets.get("client_secret", "")

        if not client_id or not client_secret:
            st.error("❌ Faltan credenciales de Google Drive")
            st.caption("Configura client_id y client_secret en .streamlit/secrets.toml")
        else:
            # Proceso de autenticación en 2 pasos
            st.markdown("#### 📋 Proceso de Autorización")

            with st.expander("📖 ¿Cómo funciona?", expanded=False):
                st.markdown("""
                **Pasos para conectar:**

                1. Click en "Generar URL de autorización"
                2. Se generará una URL especial
                3. Copia la URL y ábrela en tu navegador
                4. Inicia sesión con: **maleja8005@gmail.com**
                5. Acepta los permisos de Google Drive
                6. Google te mostrará un código
                7. Copia el código y pégalo en el campo de abajo
                8. Click en "Conectar"
                """)

            # PASO 1: Generar URL
            if 'oauth_flow' not in st.session_state:
                st.markdown("**📍 Paso 1: Generar URL de autorización**")

                if st.button("🔑 Generar URL de autorización", type="primary", key="btn_gen_url_main"):
                    try:
                        from google_auth_oauthlib.flow import InstalledAppFlow

                        # Crear configuración del cliente
                        client_config = {
                            "installed": {
                                "client_id": client_id,
                                "client_secret": client_secret,
                                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                "token_uri": "https://oauth2.googleapis.com/token",
                                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                                "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"]
                            }
                        }

                        # Crear flujo de OAuth
                        flow = InstalledAppFlow.from_client_config(
                            client_config,
                            scopes=['https://www.googleapis.com/auth/drive']
                        )

                        # Generar URL de autorización - método manual
                        flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
                        auth_url, _ = flow.authorization_url(
                            access_type='offline',
                            prompt='consent'
                        )

                        # Guardar flow en session state
                        st.session_state.oauth_flow = flow
                        st.session_state.auth_url = auth_url

                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error al generar URL: {str(e)}")

            # PASO 2: Mostrar URL y pedir código
            else:
                st.success("✅ URL de autorización generada")

                st.markdown("**📍 Paso 2: Copia esta URL y ábrela en tu navegador**")
                auth_url = st.session_state.get('auth_url', '')

                st.code(auth_url, language=None)

                # Botón para abrir en nueva pestaña
                st.markdown(f"👉 [Abrir URL en nueva pestaña]({auth_url})")

                st.warning("⚠️ Después de autorizar con **maleja8005@gmail.com**, Google te mostrará un código. Cópialo.")

                st.markdown("**📍 Paso 3: Pega el código de autorización**")

                auth_code = st.text_input(
                    "Código de autorización:",
                    type="default",
                    key="auth_code_main",
                    help="Pega aquí el código que Google te mostró"
                )

                col1, col2 = st.columns([1, 1])

                with col1:
                    if st.button("✅ Conectar con este código", type="primary", key="btn_submit_code_main"):
                        if not auth_code:
                            st.warning("⚠️ Por favor ingresa el código primero")
                        else:
                            try:
                                with st.spinner("🔐 Conectando con Google Drive..."):
                                    from googleapiclient.discovery import build

                                    flow = st.session_state.oauth_flow

                                    # Obtener token con el código
                                    flow.fetch_token(code=auth_code.strip())

                                    creds = flow.credentials
                                    st.session_state.google_drive_creds = creds

                                    # Construir servicio para verificar
                                    service = build('drive', 'v3', credentials=creds)

                                    # Guardar en drive_manager
                                    if drive_manager_main:
                                        drive_manager_main.creds = creds
                                        drive_manager_main.service = service
                                        drive_manager_main._save_credentials_to_file()

                                    # Limpiar flow
                                    if 'oauth_flow' in st.session_state:
                                        del st.session_state.oauth_flow
                                    if 'auth_url' in st.session_state:
                                        del st.session_state.auth_url

                                    st.success("✅ ¡Conectado exitosamente!")
                                    st.balloons()
                                    time.sleep(1)
                                    st.rerun()

                            except Exception as e:
                                st.error(f"❌ Error al conectar: {str(e)}")

                                if "invalid_grant" in str(e).lower() or "code" in str(e).lower():
                                    st.warning("💡 El código puede haber expirado. Genera uno nuevo.")
                                else:
                                    st.info("Verifica que el código esté completo y sin espacios extra")

                with col2:
                    if st.button("🔄 Cancelar y generar nuevo código", key="btn_cancel_auth"):
                        if 'oauth_flow' in st.session_state:
                            del st.session_state.oauth_flow
                        if 'auth_url' in st.session_state:
                            del st.session_state.auth_url
                        st.rerun()

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

# Sidebar con diseño mejorado
with st.sidebar:
    st.markdown("### 🔐 Google Drive")

    # Verificar si hay service account configurada
    try:
        import os
        service_account_file = 'config/service_account.json'

        if os.path.exists(service_account_file):
            # Estado: Service Account configurada
            st.markdown("""
                <div class='status-badge-success' style='width: 100%; text-align: center; margin-bottom: 12px;'>
                    ✅ Service Account configurada
                </div>
            """, unsafe_allow_html=True)

            # Verificar si está autenticado
            drive_manager_sidebar = get_drive_manager()

            if drive_manager_sidebar and drive_manager_sidebar.is_authenticated():
                st.markdown("""
                    <div class='status-badge-success' style='width: 100%; text-align: center; margin-bottom: 12px;'>
                        🔗 Conectado a Drive
                    </div>
                """, unsafe_allow_html=True)

                st.caption("📁 Acceso completo a Google Drive")
                st.caption("✓ Consultar archivo Master")
                st.caption("✓ Buscar PDFs")
                st.caption("✓ Generar reportes")
            else:
                st.markdown("""
                    <div class='status-badge-warning' style='width: 100%; text-align: center; margin-bottom: 12px;'>
                        ⚠️ No conectado
                    </div>
                """, unsafe_allow_html=True)

                st.caption("Drive permite:")
                st.caption("• Consultar archivo Master")
                st.caption("• Buscar PDFs de facturas")
                st.caption("• Generar reportes")
        else:
            st.error("❌ Falta archivo de credenciales")
            with st.expander("📖 ¿Cómo configurar?"):
                st.markdown("""
                Coloca el archivo `service_account.json` en:
                ```
                config/service_account.json
                ```

                Este archivo contiene las credenciales de la Service Account de Google Cloud.
                """)
    except Exception as e:
        st.error("❌ Error en configuración")
        st.caption(str(e))

    # Mostrar info de datos procesados con diseño mejorado
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("### 📊 Datos Procesados")

    if st.session_state.processed and st.session_state.stats:
        # Métricas con cards mejoradas
        total_facturas = st.session_state.stats.get('total_facturas', 0)
        facturas_sin_valor = st.session_state.stats.get('sin_valor', 0)

        st.markdown(f"""
            <div style='background: white; border: 1px solid #D1D5DB; border-radius: 12px; padding: 16px; margin-bottom: 12px; text-align: center;'>
                <div style='font-size: 32px; font-weight: 700; color: #0C147B;'>{total_facturas:,}</div>
                <div style='font-size: 14px; color: #6B7280; font-weight: 600;'>Total Facturas</div>
            </div>
        """, unsafe_allow_html=True)

        badge_color = "#10B981" if facturas_sin_valor == 0 else "#F59E0B"
        badge_bg = "#D1FAE5" if facturas_sin_valor == 0 else "#FEF3C7"
        badge_text = "✓ Todo OK" if facturas_sin_valor == 0 else "⚠ Revisar"

        st.markdown(f"""
            <div style='background: white; border: 1px solid #D1D5DB; border-radius: 12px; padding: 16px; text-align: center;'>
                <div style='font-size: 32px; font-weight: 700; color: #0C147B;'>{facturas_sin_valor:,}</div>
                <div style='font-size: 14px; color: #6B7280; font-weight: 600; margin-bottom: 8px;'>Facturas sin valor</div>
                <div style='background: {badge_bg}; color: {badge_color}; padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; display: inline-block;'>
                    {badge_text}
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style='background: #F3F4F6; border: 1px solid #D1D5DB; border-radius: 8px; padding: 16px; text-align: center;'>
                <div style='font-size: 14px; color: #6B7280;'>📂 No hay datos procesados</div>
            </div>
        """, unsafe_allow_html=True)

# ==================== FUNCIONES DE RENDERIZADO POR SECCIÓN ====================

def render_file_upload_section():
    """Sección de carga de archivos Excel"""
    # Header compacto
    st.markdown("## 📁 Carga de Archivos Excel")
    st.markdown("Carga los archivos de Netsuite y Noova para generar el reporte consolidado")

    # Grid 2x2 usando containers y gap pequeño
    with st.container():
        col1, col2 = st.columns(2, gap="medium")

        with col1:
            # Usar helper function para crear upload card
            archivo_netsuite = create_upload_card(
                title="Netsuite Facturas",
                subtitle="Sistema contable - Facturas",
                file_key="netsuite",
                file_types=["xls", "xlsx"],
                is_optional=True
            )

        with col2:
            # Usar helper function para crear upload card
            archivo_netsuite_nc = create_upload_card(
                title="Netsuite Notas Crédito",
                    subtitle="Sistema contable - Notas de crédito",
                    file_key="netsuite_nc",
                    file_types=["xls", "xlsx"],
                    is_optional=True
                )

        # Segunda fila
        with st.container():
            col3, col4 = st.columns(2, gap="medium")

            with col3:
                # Usar helper function para crear upload card
                archivo_facturas = create_upload_card(
                    title="Noova Facturas",
                    subtitle="Sistema de facturación - Facturas emitidas",
                    file_key="facturas",
                    file_types=["xlsx"],
                    is_optional=True
                )

            with col4:
                # Usar helper function para crear upload card
                archivo_notas = create_upload_card(
                    title="Noova Notas Crédito",
                    subtitle="Sistema de facturación - Notas de crédito",
                    file_key="notas_credito",
                    file_types=["xlsx"],
                    is_optional=True
                )

        # Validación de parejas de archivos - más compacta
        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        create_card(
            title="Validación de Archivos",
            content="Verifica que hayas cargado los archivos necesarios antes de procesar",
            card_type="info",
            icon="✅"
        )

        # Pareja 1: Facturas
        pareja_facturas_ok = archivo_netsuite and archivo_facturas
        pareja_facturas_incompleta = (archivo_netsuite and not archivo_facturas) or (not archivo_netsuite and archivo_facturas)
        pareja_facturas_vacia = not archivo_netsuite and not archivo_facturas

        # Pareja 2: Notas Crédito
        pareja_nc_ok = archivo_netsuite_nc and archivo_notas
        pareja_nc_incompleta = (archivo_netsuite_nc and not archivo_notas) or (not archivo_netsuite_nc and archivo_notas)
        pareja_nc_vacia = not archivo_netsuite_nc and not archivo_notas

        # Usar container para validación compacta
        with st.container():
            col_status, col_btn = st.columns([2, 1])

            with col_status:
                # Pareja 1: Facturas
                if pareja_facturas_ok:
                    st.success("✅ **Pareja 1:** Facturas Netsuite + Noova")
                elif pareja_facturas_incompleta:
                    st.error("❌ **Pareja 1:** Facturas incompleta")
                    if archivo_netsuite and not archivo_facturas:
                        st.caption("→ Tienes Netsuite Facturas pero falta Noova Facturas")
                    elif archivo_facturas and not archivo_netsuite:
                        st.caption("→ Tienes Noova Facturas pero falta Netsuite Facturas")
                else:
                    st.info("ℹ️ **Pareja 1:** Facturas (opcional)")
                    st.caption("→ Si cargas facturas, debes cargar ambos archivos")

                # Pareja 2: Notas Crédito
                if pareja_nc_ok:
                    st.success("✅ **Pareja 2:** Notas Crédito Netsuite + Noova")
                elif pareja_nc_incompleta:
                    st.error("❌ **Pareja 2:** Notas Crédito incompleta")
                    if archivo_netsuite_nc and not archivo_notas:
                        st.caption("→ Tienes Netsuite NC pero falta Noova NC")
                    elif archivo_notas and not archivo_netsuite_nc:
                        st.caption("→ Tienes Noova NC pero falta Netsuite NC")
                else:
                    st.info("ℹ️ **Pareja 2:** Notas Crédito (opcional)")
                    st.caption("→ Si cargas NC, debes cargar ambos archivos")

            with col_btn:
                st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

                # Listo para procesar si: Al menos una pareja está completa Y ninguna pareja está incompleta
                al_menos_una_pareja_completa = pareja_facturas_ok or pareja_nc_ok
                ninguna_pareja_incompleta = not pareja_facturas_incompleta and not pareja_nc_incompleta
                listo_para_procesar = al_menos_una_pareja_completa and ninguna_pareja_incompleta

                if st.button(
                    "🚀 Procesar Archivos",
                    use_container_width=True,
                    disabled=not listo_para_procesar,
                    key="btn_procesar_archivos"
                ):
                    # Validaciones con mensajes claros
                    if not al_menos_una_pareja_completa:
                        st.error("❌ **Error: No hay archivos para procesar**")
                        st.warning("📋 Debes cargar **al menos una pareja completa**:\n- **Opción 1:** Netsuite Facturas + Noova Facturas\n- **Opción 2:** Netsuite NC + Noova NC\n- **Opción 3:** Ambas parejas")
                    elif pareja_facturas_incompleta:
                        st.error("❌ **Error: Pareja de Facturas incompleta**")
                        st.warning("📋 Si cargas facturas, debes cargar **ambos archivos**:\n- Netsuite Facturas (.xls/.xlsx)\n- Noova Facturas (.xlsx)")
                    elif pareja_nc_incompleta:
                        st.error("❌ **Error: Pareja de Notas Crédito incompleta**")
                        st.warning("📋 Si cargas Notas Crédito, debes cargar **ambos archivos**:\n- Netsuite NC (.xls/.xlsx)\n- Noova NC (.xlsx)")
                    else:
                        with st.spinner("⏳ Procesando archivos... Esto puede tomar unos segundos."):
                            try:
                                # Crear directorio temporal
                                with tempfile.TemporaryDirectory() as tmpdir:
                                    # Guardar archivos temporalmente (opcional)
                                    netsuite_path = None
                                    if archivo_netsuite:
                                        netsuite_path = os.path.join(tmpdir, archivo_netsuite.name)
                                        with open(netsuite_path, 'wb') as f:
                                            f.write(archivo_netsuite.getbuffer())

                                    facturas_path = None
                                    if archivo_facturas:
                                        facturas_path = os.path.join(tmpdir, archivo_facturas.name)
                                        with open(facturas_path, 'wb') as f:
                                            f.write(archivo_facturas.getbuffer())

                                    notas_path = None
                                    if archivo_notas:
                                        notas_path = os.path.join(tmpdir, archivo_notas.name)
                                        with open(notas_path, 'wb') as f:
                                            f.write(archivo_notas.getbuffer())

                                    netsuite_nc_path = None
                                    if archivo_netsuite_nc:
                                        netsuite_nc_path = os.path.join(tmpdir, archivo_netsuite_nc.name)
                                        with open(netsuite_nc_path, 'wb') as f:
                                            f.write(archivo_netsuite_nc.getbuffer())

                                    # Inicializar procesador
                                    processor = FileProcessor(
                                        column_mapping_path='config/column_mapping.json',
                                        classification_rules_path='config/classification_rules.json',
                                        product_classification_path='config/product_classification.json'
                                    )

                                    # Leer archivos Netsuite Facturas (opcional)
                                    df_netsuite = None
                                    if netsuite_path:
                                        df_netsuite = processor.read_netsuite_file(netsuite_path)

                                    # Leer archivos Noova Facturas (opcional)
                                    df_facturas = None
                                    if facturas_path:
                                        df_facturas = processor.read_noova_file(facturas_path, 'facturas')

                                    # Leer Noova Notas Crédito (opcional)
                                    df_notas = None
                                    if notas_path:
                                        df_notas = processor.read_noova_file(notas_path, 'notas_credito')

                                    # Leer Netsuite Notas Crédito (opcional)
                                    df_netsuite_nc = None
                                    if netsuite_nc_path:
                                        df_netsuite_nc = processor.read_netsuite_nc_file(netsuite_nc_path)

                                    # Consolidar (incluye los 4 archivos)
                                    df_consolidated = processor.consolidate_data(
                                        df_netsuite,
                                        df_facturas,
                                        df_notas,
                                        df_netsuite_nc
                                    )

                                    # Preparar para archivo maestro
                                    datos_por_hoja = processor.prepare_for_master_sheet(df_consolidated)

                                    # Obtener estadísticas
                                    stats = processor.get_statistics(df_consolidated)

                                    # Crear metadata del procesamiento
                                    metadata = {
                                        'fecha_procesamiento': datetime.now().isoformat(),
                                        'archivos_procesados': {
                                            'netsuite_facturas': archivo_netsuite.name,
                                            'netsuite_nc': archivo_netsuite_nc.name if archivo_netsuite_nc else None,
                                            'noova_facturas': archivo_facturas.name,
                                            'noova_nc': archivo_notas.name if archivo_notas else None
                                        },
                                        'usuario': 'Alejandro',
                                        'total_facturas': stats.get('total_facturas', 0),
                                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    }

                                    # Guardar en session_state
                                    st.session_state.consolidated_data = df_consolidated
                                    st.session_state.datos_por_hoja = datos_por_hoja
                                    st.session_state.stats = stats
                                    st.session_state.metadata = metadata
                                    st.session_state.processed = True

                                st.balloons()
                                st.success("✅ ¡Archivos procesados exitosamente!")

                                # Mostrar resumen
                                st.markdown("---")
                                st.markdown("### 📊 Resumen del Procesamiento")

                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Total Facturas", stats.get('total_facturas', 0))
                                with col2:
                                    st.metric("Facturas Sin Valor", stats.get('sin_valor', 0))
                                with col3:
                                    st.metric("Sin Clasificar", stats.get('sin_clasificar', 0))

                            except Exception as e:
                                st.error(f"❌ Error al procesar archivos: {str(e)}")
                                with st.expander("Ver detalles del error"):
                                    st.exception(e)

    st.markdown("<div style='margin-top: 3rem;'></div>", unsafe_allow_html=True)

    # ==================== GENERAR REPORTE ====================
    # Header mejorado
    st.markdown("""
        <div style='margin-bottom: 2rem;'>
            <h2 style='font-size: 24px; font-weight: 600; color: #0C147B; margin-bottom: 0.5rem;'>
                📋 Generación de Reportes
            </h2>
            <p style='font-size: 14px; color: #6B7280;'>
                Genera y descarga reportes consolidados o personalizados
            </p>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.processed:
        st.markdown("""
            <div class='info-banner'>
                <div style='font-size: 16px; font-weight: 600; color: #0C147B; margin-bottom: 8px;'>
                    ℹ️ No hay datos procesados
                </div>
                <div style='font-size: 14px; color: #6B7280;'>
                    Ve a la pestaña "Carga de Archivos" y procesa los archivos primero para generar reportes
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        datos_por_hoja = st.session_state.datos_por_hoja

        # REPORTE DE FACTURACIÓN AUTOMATIZADO - DISEÑO MEJORADO
        st.markdown("""
            <div class='card-info' style='padding: 24px; margin-bottom: 24px;'>
                <h3 style='font-size: 20px; font-weight: 600; color: #0C147B; margin-bottom: 8px;'>
                    📁 Reporte de Facturación Automatizado
                </h3>
                <p style='font-size: 14px; color: #6B7280; margin-bottom: 0;'>
                    Genera archivo Excel completo con todas las facturas en 2 hojas (Costos Fijos y Mandato)
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Generar archivo Excel
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        file_name = f"Reporte_Facturacion_Automatizado_{timestamp}.xlsx"

        buffer_maestro = BytesIO()
        with pd.ExcelWriter(buffer_maestro, engine='openpyxl') as writer:
            for hoja_nombre, hoja_df in datos_por_hoja.items():
                # Excel tiene límite de 31 caracteres para nombres de hoja
                sheet_name = hoja_nombre[:31] if len(hoja_nombre) > 31 else hoja_nombre
                hoja_df.to_excel(writer, sheet_name=sheet_name, index=False)

        file_bytes = buffer_maestro.getvalue()

        # Botón de descarga
        st.markdown("""
            <div style='background: #F9FAFB; border: 1px solid #D1D5DB; border-radius: 8px; padding: 16px; margin-bottom: 12px;'>
                <div style='font-size: 16px; font-weight: 600; color: #0C147B; margin-bottom: 4px;'>
                    💾 Descargar Reporte
                </div>
                <div style='font-size: 13px; color: #6B7280;'>
                    Descarga el archivo Excel a tu computadora
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.download_button(
            label="💾 Descargar Reporte",
            data=file_bytes,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="btn_descargar_local_master"
        )

        # VISTA PREVIA DEL REPORTE
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
            <div class='card-info' style='padding: 24px; margin-top: 32px; margin-bottom: 24px;'>
                <h3 style='font-size: 20px; font-weight: 600; color: #0C147B; margin-bottom: 8px;'>
                    👀 Vista Previa del Reporte Generado
                </h3>
                <p style='font-size: 14px; color: #6B7280; margin-bottom: 0;'>
                    Revisa las primeras filas del reporte antes de descargarlo
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Mostrar vista previa de cada hoja
        for nombre_hoja, df_hoja in datos_por_hoja.items():
            with st.expander(f"📋 {nombre_hoja} ({len(df_hoja):,} registros)", expanded=False):
                st.dataframe(df_hoja.head(20), use_container_width=True)
                st.caption(f"Mostrando las primeras 20 filas de {len(df_hoja):,} registros totales")

st.markdown("<div style='margin-top: 4rem;'></div>", unsafe_allow_html=True)

# ==================== SELECTOR DE SECCIÓN (Mantiene estado después de rerun) ====================
# Selector visual con radio buttons (Streamlit guarda automáticamente el estado con el key)
opciones = ["📁 Generar Reportes", "📊 Reportes desde Master"]
seleccion = st.radio(
    "Selecciona una opción:",
    options=opciones,
    index=0,  # Por defecto: Generar Reportes
    horizontal=True,
    key="seccion_activa",
    label_visibility="collapsed"
)

st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

# ==================== SECCIÓN 1: GENERAR REPORTES ====================
if seleccion == "📁 Generar Reportes":
    render_file_upload_section()

# ==================== SECCIÓN 2: REPORTES DESDE MASTER ====================
elif seleccion == "📊 Reportes desde Master":
    # Header mejorado
    st.markdown("""
        <div style='margin-bottom: 2rem;'>
            <h2 style='font-size: 24px; font-weight: 600; color: #0C147B; margin-bottom: 0.5rem;'>
                📊 Reportes desde Archivo Master
            </h2>
            <p style='font-size: 14px; color: #6B7280;'>
                Consulta el archivo Master histórico con filtros avanzados
            </p>
        </div>
    """, unsafe_allow_html=True)

    drive_manager = get_drive_manager()

    if not drive_manager or not drive_manager.is_authenticated():
        # Banner de autenticación requerida (sin botón)
        st.markdown("""
            <div style='background: #FEF3C7; border-left: 4px solid #F59E0B; border-radius: 8px; padding: 20px; margin-bottom: 24px;'>
                <div style='font-size: 18px; font-weight: 600; color: #92400E; margin-bottom: 8px;'>
                    🔐 Conexión con Google Drive Requerida
                </div>
                <div style='font-size: 14px; color: #92400E; margin-bottom: 12px;'>
                    Para acceder al archivo Master histórico, necesitas conectarte con tu cuenta de Google Drive.
                </div>
                <div style='font-size: 13px; color: #92400E;'>
                    👈 Usa el botón <strong>"🔑 Conectar con Google Drive"</strong> en la barra lateral izquierda
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Conectar y cargar archivo Master
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
            <div class='card-info' style='padding: 20px; margin-bottom: 16px;'>
                <h3 style='font-size: 18px; font-weight: 600; color: #0C147B; margin-bottom: 8px;'>
                    📁 Archivo Master
                </h3>
            </div>
        """, unsafe_allow_html=True)

        # Usar caché para evitar búsquedas repetidas del Master
        if 'master_metadata' not in st.session_state:
            with st.spinner("🔍 Buscando archivo Master en Drive..."):
                try:
                    st.session_state.master_metadata = drive_manager.get_master_file_metadata()
                except Exception as e:
                    st.error(f"❌ Error al buscar archivo Master: {str(e)}")
                    st.session_state.master_metadata = None

        master_metadata = st.session_state.get('master_metadata')

        if not master_metadata:
            st.error("❌ No se encontró el archivo Master en la carpeta 'Facturación'")
            st.info(f"📂 Archivo esperado: **{drive_manager.MASTER_FILE_NAME}**")
            st.caption(f"Ubicación: finkargo/{drive_manager.FOLDER_FACTURACION}")

            if st.button("🔄 Reintentar buscar Master", key="retry_master"):
                if 'master_metadata' in st.session_state:
                    del st.session_state.master_metadata
                st.rerun()
        else:
            # Botón para refrescar Master
            if st.button("🔄 Refrescar archivo Master", key="refresh_master"):
                if 'master_metadata' in st.session_state:
                    del st.session_state.master_metadata
                st.rerun()
            # Mostrar información del archivo Master con diseño mejorado
            st.markdown(f"""
                <div style='background: white; border: 1px solid #D1D5DB; border-radius: 12px; padding: 20px; margin-bottom: 16px;'>
                    <div style='display: flex; align-items: center; gap: 16px; margin-bottom: 16px;'>
                        <div style='font-size: 48px;'>📄</div>
                        <div style='flex: 1;'>
                            <div style='font-size: 16px; font-weight: 600; color: #0C147B; margin-bottom: 4px;'>
                                {master_metadata['nombre'][:50]}{'...' if len(master_metadata['nombre']) > 50 else ''}
                            </div>
                            <div style='font-size: 13px; color: #6B7280;'>
                                📦 Tamaño: {master_metadata['tamano']} | 📅 Última modificación: {master_metadata['ultima_modificacion'][:10] if master_metadata['ultima_modificacion'] else 'N/A'}
                            </div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Link para ver el archivo
            if master_metadata.get('link'):
                st.link_button(
                    "🔗 Ver Archivo Master en Drive",
                    master_metadata['link'],
                    use_container_width=True
                )

            # Botón para cargar datos
            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

            # Verificar si ya hay datos cargados
            if st.session_state.get('master_loaded') and st.session_state.get('master_data'):
                st.success("✅ Datos del Master ya cargados en memoria")
                col1, col2 = st.columns(2)
                with col1:
                    total_registros = sum(len(df) for df in st.session_state.master_data.values())
                    st.metric("Registros en memoria", f"{total_registros:,}")
                with col2:
                    if st.button("🔄 Recargar Datos", use_container_width=True, key="btn_recargar_master"):
                        st.session_state.master_loaded = False
                        st.session_state.master_data = None
                        st.rerun()
            else:
                if st.button("📥 Cargar Datos del Master", use_container_width=True, key="btn_cargar_master"):
                    with st.spinner("⏳ Descargando y procesando archivo Master... Esto puede tomar unos segundos."):
                        dataframes_master = drive_manager.read_master_file()

                        if dataframes_master:
                            # Guardar en session_state
                            st.session_state.master_data = dataframes_master
                            st.session_state.master_loaded = True

                            st.balloons()
                            st.success("✅ ¡Archivo Master cargado exitosamente!")
                        else:
                            st.error("❌ Error al cargar el archivo Master")

            # Filtros y generación de reportes (solo si hay datos cargados)
            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
            if st.session_state.get('master_loaded') and st.session_state.get('master_data'):
                st.markdown("""
                    <div style='background: #F5F8FE; border: 1px solid #77A1E2; border-radius: 12px; padding: 20px; margin-bottom: 24px;'>
                        <h3 style='font-size: 18px; font-weight: 600; color: #0C147B; margin-bottom: 8px;'>
                            🎯 Filtros para Generar Reporte
                        </h3>
                        <p style='font-size: 13px; color: #6B7280; margin-bottom: 0;'>
                            Filtra por tipo de factura, NIT y código de desembolso
                        </p>
                    </div>
                """, unsafe_allow_html=True)

                dataframes_master = st.session_state.master_data

                # Selector de tipo de factura (con opción Consolidado)
                hojas_disponibles = list(dataframes_master.keys())
                opciones_tipo = ["📊 Consolidado (Todas)"] + hojas_disponibles

                tipo_seleccionado = st.selectbox(
                    "📋 Tipo de factura:",
                    opciones_tipo,
                    help="Selecciona qué tipo de facturas quieres consultar"
                )

                # Determinar DataFrame según selección
                if tipo_seleccionado == "📊 Consolidado (Todas)":
                    # Consolidar todas las hojas
                    dfs_a_consolidar = []
                    for nombre_hoja, df_hoja in dataframes_master.items():
                        if df_hoja is not None and not df_hoja.empty:
                            df_temp = df_hoja.copy()
                            df_temp['Tipo Factura'] = nombre_hoja  # Agregar columna de tipo
                            dfs_a_consolidar.append(df_temp)

                    if not dfs_a_consolidar:
                        st.error("❌ No hay datos para consolidar")
                        df_seleccionado = pd.DataFrame()
                        nombre_seleccion = "Consolidado"
                    else:
                        try:
                            # Concatenar con axis=0 para unir filas
                            df_seleccionado = pd.concat(dfs_a_consolidar, axis=0, ignore_index=True, sort=False)
                            nombre_seleccion = "Consolidado"
                        except Exception as e:
                            st.error(f"❌ Error al consolidar: {str(e)}")
                            # Debug info
                            with st.expander("🔍 Ver detalles para debug"):
                                st.write(f"Número de DataFrames a consolidar: {len(dfs_a_consolidar)}")
                                for i, df in enumerate(dfs_a_consolidar):
                                    st.write(f"DataFrame {i}: {df.shape} - Columnas: {len(df.columns)}")
                                    st.write(f"Tipos de datos: {df.dtypes.to_dict()}")
                            df_seleccionado = pd.DataFrame()
                            nombre_seleccion = "Consolidado"
                else:
                    df_seleccionado = dataframes_master[tipo_seleccionado].copy()
                    nombre_seleccion = tipo_seleccionado

                # Mostrar estadística
                st.caption(f"📊 {len(df_seleccionado):,} registros disponibles")

                st.markdown("---")

                # Filtros: NIT, Código y Fecha
                col_filtro1, col_filtro2, col_filtro3 = st.columns(3)

                # Función helper para normalizar strings (quitar tildes y convertir a minúsculas)
                def normalizar_texto(texto):
                    """Normaliza texto eliminando tildes y convirtiendo a minúsculas"""
                    if texto is None:
                        return ""
                    texto = str(texto)
                    # Reemplazar tildes
                    reemplazos = {
                        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
                        'Á': 'a', 'É': 'e', 'Í': 'i', 'Ó': 'o', 'Ú': 'u',
                        'ñ': 'n', 'Ñ': 'n'
                    }
                    for acento, sin_acento in reemplazos.items():
                        texto = texto.replace(acento, sin_acento)
                    return texto.lower().strip()

                # Función helper para normalizar NITs (maneja float y string)
                def normalizar_nit(valor):
                    """Convierte NIT a string limpio, manejando floats y strings"""
                    if pd.isna(valor):
                        return None
                    try:
                        # Si es float, convertir a int primero para quitar decimales
                        if isinstance(valor, float):
                            valor = int(valor)
                        # Convertir a string y limpiar
                        return str(valor).strip()
                    except:
                        return str(valor).strip() if str(valor).strip() else None

                # Detectar columna NIT de forma flexible
                columna_nit = None
                for col in df_seleccionado.columns:
                    col_normalizado = normalizar_texto(col)
                    # Buscar variaciones de "nit"
                    if 'nit' in col_normalizado:
                        columna_nit = col
                        break

                # Detectar columna de Código de desembolso de forma flexible
                columnas_codigo_encontradas = []
                for col in df_seleccionado.columns:
                    col_normalizado = normalizar_texto(col)
                    # Buscar si contiene "codigo" y "desembolso"
                    if 'codigo' in col_normalizado and 'desembolso' in col_normalizado:
                        columnas_codigo_encontradas.append(col)
                    # O solo "codigo" si no hay otra opción
                    elif col_normalizado == 'codigo':
                        columnas_codigo_encontradas.append(col)

                # Usar la primera encontrada como referencia
                columna_codigo = columnas_codigo_encontradas[0] if columnas_codigo_encontradas else None

                # Detectar TODAS las columnas de fecha disponibles
                columnas_fecha_disponibles = []
                for col in df_seleccionado.columns:
                    col_normalizado = normalizar_texto(col)
                    # Buscar cualquier columna que tenga "fecha"
                    if 'fecha' in col_normalizado:
                        columnas_fecha_disponibles.append(col)

                # Normalizar columna NIT para filtrado consistente
                if columna_nit:
                    df_seleccionado['_NIT_normalizado'] = df_seleccionado[columna_nit].apply(normalizar_nit)

                # IMPORTANTE: Unificar TODAS las columnas de código en una sola columna temporal
                # Esto resuelve el problema cuando diferentes hojas tienen nombres ligeramente diferentes
                if columnas_codigo_encontradas:
                    # Crear columna unificada combinando todos los valores de código
                    df_seleccionado['_Codigo_unificado'] = None
                    for col_codigo in columnas_codigo_encontradas:
                        df_seleccionado['_Codigo_unificado'] = df_seleccionado['_Codigo_unificado'].fillna(df_seleccionado[col_codigo])

                    # Convertir a string y limpiar
                    df_seleccionado['_Codigo_unificado'] = df_seleccionado['_Codigo_unificado'].astype(str).str.strip()
                    df_seleccionado.loc[df_seleccionado['_Codigo_unificado'] == 'nan', '_Codigo_unificado'] = None

                with col_filtro1:
                    # Filtro por NIT
                    st.markdown("**👤 Filtro por NIT del Cliente**")

                    if columna_nit:
                        nits_disponibles = [nit for nit in df_seleccionado['_NIT_normalizado'].dropna().unique() if nit]
                        nits_disponibles = sorted(nits_disponibles)

                        filtro_nit = st.multiselect(
                            "Seleccionar NIT(s)",
                            options=nits_disponibles,
                            default=[],
                            help="Selecciona uno o más NITs para ver sus códigos de desembolso",
                            key="filtro_nit_master"
                        )

                        st.caption(f"💡 {len(nits_disponibles)} NITs disponibles")
                    else:
                        st.warning("⚠️ No se encontró columna de NIT")
                        filtro_nit = []

                with col_filtro2:
                    # Filtro por Código de Desembolso (REACTIVO al filtro de NIT)
                    st.markdown("**💼 Filtro por Código de Desembolso**")

                    if columnas_codigo_encontradas:
                        # Si hay NITs seleccionados, filtrar los códigos por esos NITs
                        if filtro_nit and columna_nit:
                            df_para_codigos = df_seleccionado[
                                df_seleccionado['_NIT_normalizado'].isin(filtro_nit)
                            ]
                            help_text = f"Códigos asociados a los {len(filtro_nit)} NIT(s) seleccionado(s)"
                        else:
                            df_para_codigos = df_seleccionado
                            help_text = "Selecciona primero un NIT para ver solo sus códigos, o deja vacío para todos"

                        # Usar columna unificada que combina todas las variaciones de código
                        codigos_disponibles = [c for c in df_para_codigos['_Codigo_unificado'].dropna().unique() if c and str(c).strip() and str(c) != 'nan']
                        codigos_disponibles = sorted(codigos_disponibles)

                        filtro_codigo = st.multiselect(
                            "Seleccionar Código(s)",
                            options=codigos_disponibles,
                            default=[],
                            help=help_text,
                            key="filtro_codigo_master"
                        )

                        if filtro_nit:
                            st.caption(f"💡 {len(codigos_disponibles)} códigos disponibles para el(los) NIT(s) seleccionado(s)")
                        else:
                            st.caption(f"💡 {len(codigos_disponibles)} códigos disponibles en total")
                    else:
                        st.warning("⚠️ No se encontró columna de código de desembolso")
                        filtro_codigo = []

                with col_filtro3:
                    # Filtro por Fecha
                    st.markdown("**📅 Filtro por Fecha**")

                    if columnas_fecha_disponibles:
                        # Permitir seleccionar qué columna de fecha usar
                        columna_fecha_seleccionada = st.selectbox(
                            "Columna de fecha:",
                            options=columnas_fecha_disponibles,
                            index=0,
                            key="columna_fecha_selector",
                            help="Selecciona qué columna de fecha usar para filtrar"
                        )

                        # Convertir la columna seleccionada a datetime
                        try:
                            df_seleccionado['_Fecha_normalizada'] = pd.to_datetime(
                                df_seleccionado[columna_fecha_seleccionada],
                                errors='coerce'
                            )
                            columna_fecha = columna_fecha_seleccionada
                        except:
                            columna_fecha = None
                            st.error("❌ No se pudo convertir la columna a fecha")
                    else:
                        columna_fecha = None

                    if columna_fecha and '_Fecha_normalizada' in df_seleccionado.columns:

                        # Obtener rango de fechas disponibles
                        fechas_validas = df_seleccionado['_Fecha_normalizada'].dropna()

                        if len(fechas_validas) > 0:
                            fecha_min = fechas_validas.min().date()
                            fecha_max = fechas_validas.max().date()

                            # Selector de rango de fechas
                            usar_filtro_fecha = st.checkbox(
                                "Activar filtro de fecha",
                                value=False,
                                help="Filtra registros por rango de fechas",
                                key="usar_filtro_fecha"
                            )

                            if usar_filtro_fecha:
                                fecha_desde = st.date_input(
                                    "Desde:",
                                    value=fecha_min,
                                    min_value=fecha_min,
                                    max_value=fecha_max,
                                    key="fecha_desde_master"
                                )

                                fecha_hasta = st.date_input(
                                    "Hasta:",
                                    value=fecha_max,
                                    min_value=fecha_min,
                                    max_value=fecha_max,
                                    key="fecha_hasta_master"
                                )

                                st.caption(f"💡 Rango disponible: {fecha_min.year} - {fecha_max.year}")
                            else:
                                fecha_desde = None
                                fecha_hasta = None
                        else:
                            st.warning("⚠️ No hay fechas válidas")
                            fecha_desde = None
                            fecha_hasta = None
                            usar_filtro_fecha = False
                    else:
                        st.warning("⚠️ No se encontró columna de fecha")
                        fecha_desde = None
                        fecha_hasta = None
                        usar_filtro_fecha = False

                st.markdown("---")

                # Aplicar filtros
                df_filtrado = df_seleccionado.copy()
                registros_inicial = len(df_filtrado)

                # Aplicar filtro de NIT (usando columna normalizada Y buscando en código de desembolso)
                if filtro_nit and columna_nit:
                    # Filtro 1: Coincidencia directa en columna NIT
                    filtro_por_columna_nit = df_filtrado['_NIT_normalizado'].isin(filtro_nit)

                    # Filtro 2: Buscar NIT en código de desembolso (formato CO:nit:NUM:NUM:LETRAS)
                    if columnas_codigo_encontradas and '_Codigo_unificado' in df_filtrado.columns:
                        filtro_por_codigo = pd.Series([False] * len(df_filtrado), index=df_filtrado.index)

                        for nit in filtro_nit:
                            # Buscar el patrón "CO:nit:" en el código de desembolso
                            filtro_por_codigo = filtro_por_codigo | df_filtrado['_Codigo_unificado'].str.contains(
                                f'CO:{nit}:',
                                na=False,
                                case=False,
                                regex=False
                            )

                        # Combinar ambos filtros con OR (incluir si cumple cualquiera de los dos)
                        df_filtrado = df_filtrado[filtro_por_columna_nit | filtro_por_codigo]
                    else:
                        # Si no hay columna de código, solo usar filtro de NIT directo
                        df_filtrado = df_filtrado[filtro_por_columna_nit]

                # Aplicar filtro de Código (usando columna unificada)
                registros_despues_nit = len(df_filtrado)
                if filtro_codigo and columnas_codigo_encontradas:
                    df_filtrado = df_filtrado[df_filtrado['_Codigo_unificado'].isin(filtro_codigo)]

                # Aplicar filtro de Fecha (si está activado)
                registros_despues_codigo = len(df_filtrado)
                if usar_filtro_fecha and columna_fecha and fecha_desde and fecha_hasta:
                    # Convertir fechas a datetime para comparación
                    fecha_desde_dt = pd.to_datetime(fecha_desde)
                    fecha_hasta_dt = pd.to_datetime(fecha_hasta) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)  # Incluir todo el día

                    df_filtrado = df_filtrado[
                        (df_filtrado['_Fecha_normalizada'] >= fecha_desde_dt) &
                        (df_filtrado['_Fecha_normalizada'] <= fecha_hasta_dt)
                    ]

                # Mostrar información de filtros aplicados
                registros_final = len(df_filtrado)

                with st.expander("🔍 Debug de Filtros", expanded=False):
                    st.caption(f"📊 Registros iniciales: {registros_inicial:,}")

                    # Mostrar distribución por tipo si es consolidado
                    if nombre_seleccion == "Consolidado" and 'Tipo Factura' in df_seleccionado.columns:
                        st.markdown("**Distribución inicial por tipo:**")
                        dist_inicial = df_seleccionado['Tipo Factura'].value_counts()
                        for tipo, count in dist_inicial.items():
                            st.caption(f"  • {tipo}: {count:,} registros")

                    if filtro_nit:
                        st.caption(f"📊 Después de filtrar por NIT: {registros_despues_nit:,}")
                        if nombre_seleccion == "Consolidado" and 'Tipo Factura' in df_filtrado.columns and registros_despues_nit > 0:
                            dist_nit = df_filtrado['Tipo Factura'].value_counts()
                            for tipo, count in dist_nit.items():
                                st.caption(f"    → {tipo}: {count:,}")

                    if filtro_codigo:
                        st.caption(f"📊 Después de filtrar por Código: {registros_despues_codigo:,}")
                        if nombre_seleccion == "Consolidado" and 'Tipo Factura' in df_filtrado.columns and registros_despues_codigo > 0:
                            dist_codigo = df_filtrado['Tipo Factura'].value_counts()
                            for tipo, count in dist_codigo.items():
                                st.caption(f"    → {tipo}: {count:,}")

                    if usar_filtro_fecha:
                        st.caption(f"📊 Después de filtrar por Fecha ({fecha_desde} a {fecha_hasta}): {registros_final:,}")
                        if nombre_seleccion == "Consolidado" and 'Tipo Factura' in df_filtrado.columns and registros_final > 0:
                            dist_fecha = df_filtrado['Tipo Factura'].value_counts()
                            for tipo, count in dist_fecha.items():
                                st.caption(f"    → {tipo}: {count:,}")

                    st.caption(f"✅ **Total final: {registros_final:,} registros**")

                # Limpiar columnas temporales del resultado final
                columnas_temporales = ['_NIT_normalizado', '_Codigo_unificado', '_Fecha_normalizada']
                for col_temp in columnas_temporales:
                    if col_temp in df_filtrado.columns:
                        df_filtrado = df_filtrado.drop(columns=[col_temp])

                # ========== LIMPIEZA Y CONSOLIDACIÓN DE COLUMNAS ==========
                def limpiar_columnas_reporte(df):
                    """Limpia, consolida y reorganiza columnas del reporte"""
                    df_clean = df.copy()

                    # 1. Eliminar columnas Unnamed
                    unnamed_cols = [col for col in df_clean.columns if 'Unnamed' in str(col) or col.startswith('Unnamed')]
                    df_clean = df_clean.drop(columns=unnamed_cols, errors='ignore')

                    # 2. Eliminar columnas innecesarias
                    columnas_eliminar = [
                        'Validacion Consecutivo', 'Revision', 'Estado', 'Envio',
                        'Fac de la nota Crédito', 'Fecha Nota Credito', '# Nota Credito'
                    ]
                    df_clean = df_clean.drop(columns=columnas_eliminar, errors='ignore')

                    # 3. Unificar columnas de Código de desembolso
                    if 'Código del desembolso' in df_clean.columns and 'Codigo del desembolso' in df_clean.columns:
                        # Combinar ambas columnas
                        df_clean['Codigo del desembolso'] = df_clean['Codigo del desembolso'].fillna(df_clean['Código del desembolso'])
                        df_clean = df_clean.drop(columns=['Código del desembolso'], errors='ignore')
                    elif 'Código del desembolso' in df_clean.columns:
                        df_clean = df_clean.rename(columns={'Código del desembolso': 'Codigo del desembolso'})

                    # 4. Unificar columnas de Fecha (consolidar en "Fecha Factura")
                    columnas_fecha = ['Fecha Factura', 'Fecha Facturacion', 'Fecha de desembolso']
                    fecha_principal = None
                    for col_fecha in columnas_fecha:
                        if col_fecha in df_clean.columns:
                            if fecha_principal is None:
                                fecha_principal = col_fecha
                                df_clean = df_clean.rename(columns={col_fecha: 'Fecha Factura'})
                            else:
                                # Rellenar valores faltantes con otras columnas de fecha
                                df_clean['Fecha Factura'] = df_clean['Fecha Factura'].fillna(df_clean[col_fecha])
                                df_clean = df_clean.drop(columns=[col_fecha], errors='ignore')

                    # 5. Eliminar todas las columnas de "Mes Facturacion" (preferimos usar "Fecha Factura")
                    mes_facturacion_cols = [col for col in df_clean.columns if 'Mes facturacion' in col or 'Mes Facturacion' in col or 'Mes facturación' in col]
                    df_clean = df_clean.drop(columns=mes_facturacion_cols, errors='ignore')

                    # 6. Unificar columnas de Moneda (eliminar duplicados)
                    moneda_cols = [col for col in df_clean.columns if col == 'Moneda' or col.endswith('.1') and 'Moneda' in col]
                    if len(moneda_cols) > 1:
                        # Mantener solo la primera columna de Moneda
                        for col in moneda_cols[1:]:
                            df_clean = df_clean.drop(columns=[col], errors='ignore')

                    # 7. Reorganizar columnas (las más importantes al principio)
                    columnas_prioritarias = [
                        'Tipo Factura',
                        'Codigo del desembolso',
                        'NIT',
                        'Cliente',
                        'Fecha Factura',
                        '# Factura',
                        'Numero de factura',
                        'Moneda'
                    ]

                    # Columnas que existen y están en la lista prioritaria
                    cols_ordenadas = [col for col in columnas_prioritarias if col in df_clean.columns]

                    # Resto de columnas (que no están en prioritarias)
                    cols_restantes = [col for col in df_clean.columns if col not in cols_ordenadas]

                    # Reordenar
                    df_clean = df_clean[cols_ordenadas + cols_restantes]

                    return df_clean

                # Aplicar limpieza de columnas
                df_filtrado = limpiar_columnas_reporte(df_filtrado)

                # Guardar en session_state para búsqueda de PDFs
                st.session_state.df_filtrado_master = df_filtrado

                if len(df_filtrado) == 0:
                    st.warning("⚠️ No hay registros que cumplan con los filtros seleccionados")
                else:
                    # Vista previa del reporte
                    st.markdown("---")
                    st.markdown("""
                        <div style='background: white; border: 2px solid #3C47D3; border-radius: 12px; padding: 20px; margin-bottom: 24px;'>
                            <h3 style='font-size: 18px; font-weight: 600; color: #0C147B; margin-bottom: 8px;'>
                                👀 Vista Previa del Reporte
                            </h3>
                            <p style='font-size: 14px; color: #6B7280; margin-bottom: 0;'>
                                Revisa los datos antes de descargar o subir a Drive
                            </p>
                        </div>
                    """, unsafe_allow_html=True)

                    # Mostrar estadísticas básicas
                    col_stat1, col_stat2, col_stat3 = st.columns(3)

                    with col_stat1:
                        st.markdown(f"""
                            <div style='background: white; border: 1px solid #D1D5DB; border-radius: 8px; padding: 16px; text-align: center;'>
                                <div style='font-size: 28px; font-weight: 700; color: #3C47D3;'>{len(df_filtrado):,}</div>
                                <div style='font-size: 13px; color: #6B7280;'>Registros</div>
                            </div>
                        """, unsafe_allow_html=True)

                    with col_stat2:
                        st.markdown(f"""
                            <div style='background: white; border: 1px solid #D1D5DB; border-radius: 8px; padding: 16px; text-align: center;'>
                                <div style='font-size: 28px; font-weight: 700; color: #3C47D3;'>{len(df_filtrado.columns)}</div>
                                <div style='font-size: 13px; color: #6B7280;'>Columnas</div>
                            </div>
                        """, unsafe_allow_html=True)

                    with col_stat3:
                        # Calcular suma de valores si hay columna numérica de valor
                        columnas_valor = [col for col in df_filtrado.columns if any(x in str(col).lower() for x in ['valor', 'monto', 'total', 'importe'])]
                        if columnas_valor:
                            try:
                                total_valor = df_filtrado[columnas_valor[0]].sum()
                                st.markdown(f"""
                                    <div style='background: white; border: 1px solid #D1D5DB; border-radius: 8px; padding: 16px; text-align: center;'>
                                        <div style='font-size: 28px; font-weight: 700; color: #10B981;'>${total_valor:,.0f}</div>
                                        <div style='font-size: 13px; color: #6B7280;'>Total</div>
                                    </div>
                                """, unsafe_allow_html=True)
                            except:
                                st.markdown(f"""
                                    <div style='background: white; border: 1px solid #D1D5DB; border-radius: 8px; padding: 16px; text-align: center;'>
                                        <div style='font-size: 28px; font-weight: 700; color: #6B7280;'>-</div>
                                        <div style='font-size: 13px; color: #6B7280;'>Total</div>
                                    </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                                <div style='background: white; border: 1px solid #D1D5DB; border-radius: 8px; padding: 16px; text-align: center;'>
                                    <div style='font-size: 28px; font-weight: 700; color: #6B7280;'>-</div>
                                    <div style='font-size: 13px; color: #6B7280;'>Total</div>
                                </div>
                            """, unsafe_allow_html=True)

                    # DataFrame interactivo
                    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
                    st.dataframe(
                        df_filtrado,
                        use_container_width=True,
                        height=400
                    )

                    st.caption(f"📊 Mostrando {len(df_filtrado):,} registros filtrados")

                    st.markdown("---")

                    # Opción de descarga
                    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
                    nombre_archivo = f"Reporte_Master_{nombre_seleccion.replace(' ', '_')}_{timestamp}"

                    st.markdown("### 📥 Descargar Reporte")

                    # Generar Excel
                    buffer_excel = BytesIO()
                    with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
                        df_filtrado.to_excel(writer, sheet_name=nombre_seleccion[:31], index=False)

                    st.download_button(
                        label="📥 Descargar Excel",
                        data=buffer_excel.getvalue(),
                        file_name=f"{nombre_archivo}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )

        # ========== BUSCAR PDFs EN DRIVE ==========
        st.markdown("<div style='margin-top: 2.5rem;'></div>", unsafe_allow_html=True)
        try:
            drive_manager_pdf = get_drive_manager()

            if not drive_manager_pdf or not drive_manager_pdf.is_authenticated():
                st.warning("⚠️ Conecta con Google Drive primero")
                st.caption("👈 Usa el botón en la barra lateral izquierda")
            else:
                # Opción 1: Búsqueda automática desde el reporte filtrado (PRINCIPAL)
                st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
                st.markdown("""
                    <div style='background: #F5F8FE; border: 1px solid #3C47D3; border-radius: 12px; padding: 20px; margin-bottom: 16px;'>
                        <h3 style='font-size: 18px; font-weight: 600; color: #0C147B; margin-bottom: 8px;'>
                            🎯 Opción 1: Buscar PDFs desde Reporte Filtrado
                        </h3>
                        <p style='font-size: 13px; color: #6B7280; margin-bottom: 0;'>
                            Genera primero un reporte filtrado para buscar sus PDFs automáticamente
                        </p>
                    </div>
                """, unsafe_allow_html=True)

                if st.session_state.get('master_loaded') and st.session_state.get('df_filtrado_master') is not None and not st.session_state.df_filtrado_master.empty:
                    df_filtrado = st.session_state.df_filtrado_master

                    if st.button("🔍 Buscar PDFs del Reporte", use_container_width=True, key="btn_search_from_report_master"):
                        # Detectar columna de número de factura
                        columnas_factura_posibles = [
                            '# Factura',
                            'Numero de factura',
                            'Número de factura',
                            'N° Factura',
                            'Factura',
                            'No. Factura'
                        ]

                        columna_factura = None
                        for col in columnas_factura_posibles:
                            if col in df_filtrado.columns:
                                columna_factura = col
                                break

                        if columna_factura:
                            # Extraer números de factura del reporte
                            invoice_numbers = [
                                str(num).strip()
                                for num in df_filtrado[columna_factura].dropna().unique()
                                if str(num).strip() and str(num) != 'nan'
                            ]

                            if invoice_numbers:
                                with st.spinner("🔍 Buscando PDFs..."):
                                    invoices_found = drive_manager_pdf.search_pdfs_in_facturas_folder(invoice_numbers)

                                    found = [inv for inv in invoices_found if inv.get('encontrado')]
                                    not_found = [inv for inv in invoices_found if not inv.get('encontrado')]

                                    if found:
                                        st.success(f"✅ {len(found)} de {len(invoice_numbers)} PDFs encontrados")

                                        # Botón de descarga masiva
                                        st.markdown("### 📦 Descarga Masiva")

                                        # Crear barra de progreso
                                        progress_zip = st.progress(0)
                                        status_zip = st.empty()

                                        # Descargar directamente con progreso
                                        zip_content = drive_manager_pdf.download_multiple_files(
                                            found,
                                            progress_bar=progress_zip,
                                            status_text=status_zip
                                        )

                                        # Limpiar progreso
                                        progress_zip.empty()
                                        status_zip.empty()

                                        if zip_content:
                                            st.success(f"✅ ZIP listo con {len(found)} archivos")
                                            st.download_button(
                                                label=f"📥 Descargar ZIP ({len(found)} archivos)",
                                                data=zip_content,
                                                file_name=f"Facturas_Reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                                mime="application/zip",
                                                use_container_width=True,
                                                key="btn_final_download_zip_auto"
                                            )
                                        else:
                                            st.error("❌ No se pudo generar el ZIP")

                                        st.markdown("---")
                                        st.markdown("### 📄 PDFs Encontrados")

                                        # Mostrar cada PDF
                                        for idx, inv in enumerate(found):
                                            col1, col2, col3, col4 = st.columns([3, 1, 0.8, 0.8])

                                            with col1:
                                                st.write(f"📄 {inv['nombre']}")
                                            with col2:
                                                st.write(inv.get('tamano', 'N/A'))
                                            with col3:
                                                if inv.get('link_ver'):
                                                    st.link_button("👁️", inv['link_ver'], use_container_width=True)
                                            with col4:
                                                file_content = drive_manager_pdf.download_file(inv['id'], inv['nombre'])
                                                if file_content:
                                                    st.download_button(
                                                        "⬇️",
                                                        file_content,
                                                        inv['nombre'],
                                                        mime="application/pdf",
                                                        key=f"dl_{idx}_auto",
                                                        use_container_width=True
                                                    )

                                    if not_found:
                                        st.markdown("---")
                                        st.warning(f"⚠️ {len(not_found)} facturas no encontradas:")
                                        for nf in not_found:
                                            st.write(f"❌ {nf['numero_factura']}")
                            else:
                                st.warning("⚠️ No se encontraron números de factura en el reporte")
                        else:
                            st.error(f"❌ No se encontró columna de número de factura. Columnas disponibles: {', '.join(df_filtrado.columns[:10])}")
                else:
                    st.info("📊 Genera primero un reporte filtrado para buscar sus PDFs automáticamente")

                # Opción 2: Búsqueda manual (SECUNDARIA)
                st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
                st.markdown("""
                    <div style='background: #F9FAFB; border: 1px solid #D1D5DB; border-radius: 12px; padding: 20px; margin-bottom: 16px;'>
                        <h3 style='font-size: 18px; font-weight: 600; color: #0C147B; margin-bottom: 8px;'>
                            ✏️ Opción 2: Buscar PDFs Manualmente
                        </h3>
                        <p style='font-size: 13px; color: #6B7280; margin-bottom: 0;'>
                            Busca PDFs específicos ingresando el número de factura o NIT
                        </p>
                    </div>
                """, unsafe_allow_html=True)

                invoice_numbers_input = st.text_area(
                    "📋 Números de factura (uno por línea)",
                    placeholder="FE9133\nFE9134\nITPA5678",
                    height=100,
                    key="invoice_numbers_input_master_v2",
                    help="Ingresa uno o más números de factura, cada uno en una línea diferente"
                )

                if st.button("🔍 Buscar PDFs Manualmente", use_container_width=True, key="btn_search_invoices_manual"):
                    if invoice_numbers_input:
                        invoice_numbers = [
                            num.strip()
                            for num in invoice_numbers_input.split('\n')
                            if num.strip()
                        ]

                        with st.spinner("🔍 Buscando PDFs..."):
                            invoices_found = drive_manager_pdf.search_pdfs_in_facturas_folder(invoice_numbers)

                            found = [inv for inv in invoices_found if inv.get('encontrado')]
                            not_found = [inv for inv in invoices_found if not inv.get('encontrado')]

                            if found:
                                st.success(f"✅ {len(found)} PDFs encontrados")

                                # Botón de descarga masiva
                                st.markdown("### 📦 Descarga Masiva")

                                # Crear barra de progreso
                                progress_zip_m = st.progress(0)
                                status_zip_m = st.empty()

                                # Descargar directamente con progreso
                                zip_content = drive_manager_pdf.download_multiple_files(
                                    found,
                                    progress_bar=progress_zip_m,
                                    status_text=status_zip_m
                                )

                                # Limpiar progreso
                                progress_zip_m.empty()
                                status_zip_m.empty()

                                if zip_content:
                                    st.success(f"✅ ZIP listo con {len(found)} archivos")
                                    st.download_button(
                                        label=f"📥 Descargar ZIP ({len(found)} archivos)",
                                        data=zip_content,
                                        file_name=f"Facturas_Manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                        mime="application/zip",
                                        use_container_width=True,
                                        key="btn_final_download_zip_manual"
                                    )
                                else:
                                    st.error("❌ No se pudo generar el ZIP")

                                st.markdown("---")
                                st.markdown("### 📄 PDFs Encontrados")

                                # Mostrar cada PDF
                                for idx, inv in enumerate(found):
                                    col1, col2, col3, col4 = st.columns([3, 1, 0.8, 0.8])

                                    with col1:
                                        st.write(f"📄 {inv['nombre']}")
                                    with col2:
                                        st.write(inv.get('tamano', 'N/A'))
                                    with col3:
                                        if inv.get('link_ver'):
                                            st.link_button("👁️", inv['link_ver'], use_container_width=True)
                                    with col4:
                                        file_content = drive_manager_pdf.download_file(inv['id'], inv['nombre'])
                                        if file_content:
                                            st.download_button(
                                                "⬇️",
                                                file_content,
                                                inv['nombre'],
                                                mime="application/pdf",
                                                key=f"dl_{idx}_manual",
                                                use_container_width=True
                                            )

                            if not_found:
                                st.markdown("---")
                                st.warning(f"⚠️ {len(not_found)} facturas no encontradas:")
                                for nf in not_found:
                                    st.write(f"❌ {nf['numero_factura']}")
                    else:
                        st.warning("⚠️ Ingresa al menos un número de factura")

        except Exception as e:
            st.error(f"❌ Error al buscar PDFs: {str(e)}")
            with st.expander("Ver detalles del error"):
                st.exception(e)

# Footer compacto
st.markdown("""
<div style='text-align: center; color: #9CA3AF; font-size: 12px; margin-top: 3rem; padding: 1rem 0; border-top: 1px solid #E5E7EB;'>
    Sistema de Facturación Finkargo v1.0 - Fase 1 MVP | Octubre 2025
</div>
""", unsafe_allow_html=True)