"""
Sistema de Consolidación de Facturas - Finkargo
Aplicación Streamlit para procesar y consolidar datos de facturación
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from modules.drive_manager import DriveManager

# Configuración de la página
st.set_page_config(
    page_title="Facturación Finkargo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar session state
if 'consolidated_data' not in st.session_state:
    st.session_state.consolidated_data = None
if 'drive_manager' not in st.session_state:
    st.session_state.drive_manager = None

# Título principal
st.title("📊 Sistema de Consolidación de Facturas")
st.markdown("---")

# Sidebar con información y autenticación
with st.sidebar:
    st.header("ℹ️ Información")
    st.info("Sistema para consolidar facturas de NUVA y Netsuite")
    st.markdown("**Usuario:** Alejandro")
    st.markdown("**Fecha:** " + datetime.now().strftime("%Y-%m-%d"))

    st.markdown("---")

    # Estado de Google Drive
    st.header("🔐 Google Drive")
    
    # Verificar si hay credenciales configuradas
    try:
        client_id = st.secrets.get("client_id", "")
        client_secret = st.secrets.get("client_secret", "")
        
        if client_id and client_secret:
            st.success("✅ Credenciales configuradas")
            
            # Verificar si está autenticado
            if 'google_drive_creds' in st.session_state:
                st.success("🔗 Conectado a Drive")
                
                # Botón para desconectar
                if st.button("🔓 Desconectar", use_container_width=True):
                    if 'google_drive_creds' in st.session_state:
                        del st.session_state.google_drive_creds
                    if 'drive_manager' in st.session_state:
                        del st.session_state.drive_manager
                    st.rerun()
            else:
                st.warning("⚠️ No autorizado")
                st.caption("👉 Ve a 'Buscar en Drive' para conectar")
        else:
            st.error("❌ Faltan credenciales")
            with st.expander("📖 ¿Cómo configurar?"):
                st.code("""
# En .streamlit/secrets.toml
client_id = "tu-client-id"
client_secret = "tu-client-secret"
                """)
    except Exception as e:
        st.error("❌ Error en configuración")
        st.caption(str(e))
    
    # Mostrar info de datos cargados
    st.markdown("---")
    if 'consolidated_data' in st.session_state and st.session_state.consolidated_data is not None:
        st.success(f"📊 {len(st.session_state.consolidated_data)} facturas cargadas")
    else:
        st.info("📂 No hay datos cargados")

# Crear tabs principales
tab1, tab2, tab3, tab4 = st.tabs(["📁 Carga de Archivos", "📈 Dashboard", "📋 Generar Reporte", "🔍 Buscar en Drive"])

# Tab 1: Carga de Archivos
with tab1:
    st.header("📁 Carga de Archivos Excel")
    st.markdown("Sube los tres archivos necesarios para el procesamiento:")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("📄 NUVA - Archivo 1")
        archivo_nuva_1 = st.file_uploader(
            "Selecciona el primer archivo de NUVA",
            type=["xlsx", "xls"],
            key="nuva1"
        )
        if archivo_nuva_1:
            st.success(f"✅ Cargado: {archivo_nuva_1.name}")

    with col2:
        st.subheader("📄 NUVA - Archivo 2")
        archivo_nuva_2 = st.file_uploader(
            "Selecciona el segundo archivo de NUVA",
            type=["xlsx", "xls"],
            key="nuva2"
        )
        if archivo_nuva_2:
            st.success(f"✅ Cargado: {archivo_nuva_2.name}")

    with col3:
        st.subheader("📄 Netsuite")
        archivo_netsuite = st.file_uploader(
            "Selecciona el archivo de Netsuite",
            type=["xlsx", "xls"],
            key="netsuite"
        )
        if archivo_netsuite:
            st.success(f"✅ Cargado: {archivo_netsuite.name}")

    st.markdown("---")

    # Botón de procesamiento
    if archivo_nuva_1 and archivo_nuva_2 and archivo_netsuite:
        if st.button("🚀 Procesar Archivos", type="primary", use_container_width=True):
            with st.spinner("Procesando archivos..."):
                # TODO: Implementar lógica de procesamiento
                st.success("✅ Archivos procesados correctamente")
    else:
        st.warning("⚠️ Por favor, carga los tres archivos para continuar")

# Tab 2: Dashboard
with tab2:
    st.header("📈 Dashboard de Facturación")

    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="💰 Total Facturado",
            value="$0",
            delta="0%"
        )

    with col2:
        st.metric(
            label="📄 Facturas Procesadas",
            value="0",
            delta="0"
        )

    with col3:
        st.metric(
            label="✅ Validadas",
            value="0",
            delta="0"
        )

    with col4:
        st.metric(
            label="⚠️ Con Observaciones",
            value="0",
            delta="0"
        )

    st.markdown("---")

    # Placeholder para gráficos
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Distribución por Tipo de Factura")
        st.info("Los datos aparecerán después de procesar los archivos")

    with col2:
        st.subheader("📈 Evolución Mensual")
        st.info("Los datos aparecerán después de procesar los archivos")

# Tab 3: Generar Reporte
with tab3:
    st.header("📋 Generación de Reportes")

    # Filtros
    st.subheader("🔍 Filtros")

    col1, col2 = st.columns(2)

    with col1:
        codigo_desembolso = st.text_input("Código de Desembolso", placeholder="Ej: DES-2024-001")
        nit = st.text_input("NIT", placeholder="Ej: 900123456-1")

    with col2:
        fecha_inicio = st.date_input(
            "Fecha Inicio",
            value=datetime.now() - timedelta(days=30)
        )
        fecha_fin = st.date_input(
            "Fecha Fin",
            value=datetime.now()
        )

    tipo_factura = st.multiselect(
        "Tipo de Factura",
        ["Nacional", "Internacional", "Servicios", "Productos"],
        default=[]
    )

    st.markdown("---")

    # Opciones de exportación
    st.subheader("📤 Opciones de Exportación")

    col1, col2 = st.columns(2)

    with col1:
        formato_export = st.radio(
            "Formato de Exportación",
            ["Excel (.xlsx)", "CSV (.csv)", "Google Sheets"],
            horizontal=True
        )

    with col2:
        incluir_graficos = st.checkbox("Incluir gráficos en reporte", value=True)
        incluir_detalle = st.checkbox("Incluir detalle completo", value=True)

    st.markdown("---")

    # Botón de generación
    if st.button("📥 Generar Reporte", type="primary", use_container_width=True):
        with st.spinner("Generando reporte..."):
            # TODO: Implementar lógica de generación de reportes
            st.success("✅ Reporte generado correctamente")
            st.download_button(
                label="⬇️ Descargar Reporte",
                data="",  # TODO: datos del reporte
                file_name=f"reporte_facturacion_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # Búsqueda automática de PDFs en Drive
            drive_manager = get_drive_manager()
            if drive_manager:
                st.markdown("---")
                st.subheader("📎 PDFs Asociados en Google Drive")

                with st.spinner("Buscando PDFs asociados..."):
                    # TODO: Obtener números de documento del reporte generado
                    # Por ahora mostramos un placeholder
                    st.info("Los PDFs asociados aparecerán aquí una vez que se implemente la lógica de procesamiento de archivos")
                    st.markdown("**Próximos pasos:**")
                    st.markdown("- Extraer números de documento del reporte")
                    st.markdown("- Buscar PDFs en Google Drive")
                    st.markdown("- Mostrar resultados y opciones de descarga")
            else:
                st.info("💡 Conecta con Google Drive en la barra lateral para buscar PDFs automáticamente")

# Tab 4: Buscar en Drive
with tab4:
    st.header("🔍 Búsqueda de Facturas en Google Drive")
    
    try:
        # Inicializar drive manager si no existe
        if 'drive_manager' not in st.session_state or st.session_state.drive_manager is None:
            st.session_state.drive_manager = DriveManager()
        
        drive_manager = st.session_state.drive_manager
        
        # Verificar si está autenticado
        if not drive_manager.is_authenticated():
            # Mostrar proceso de autenticación
            drive_manager.authenticate()
        else:
            # Ya está autenticado, mostrar funcionalidad de búsqueda
            st.success("✅ Conectado a Google Drive")
            
            st.markdown("---")
            st.subheader("🔍 Buscar Facturas")
            
            # Opciones de búsqueda
            search_type = st.radio(
                "Tipo de búsqueda:",
                ["Búsqueda por texto", "Números de factura específicos"],
                horizontal=True
            )
            
            invoices_found = []
            
            if search_type == "Búsqueda por texto":
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    search_query = st.text_input(
                        "🔍 Buscar por nombre",
                        placeholder="Ej: FE9133, Cliente XYZ"
                    )
                
                with col2:
                    date_from = st.date_input("📅 Desde", value=None, key="date_from_search")
                
                with col3:
                    date_to = st.date_input("📅 Hasta", value=None, key="date_to_search")
                
                if st.button("🔍 Buscar", type="primary", key="btn_search_text"):
                    if search_query:
                        with st.spinner("Buscando en Google Drive..."):
                            invoices_found = drive_manager.search_invoices(
                                query=search_query,
                                date_from=date_from.strftime('%Y-%m-%d') if date_from else None,
                                date_to=date_to.strftime('%Y-%m-%d') if date_to else None
                            )
                    else:
                        st.warning("⚠️ Ingresa un término de búsqueda")
            
            else:  # Búsqueda por números específicos
                invoice_numbers_input = st.text_area(
                    "📋 Números de factura (uno por línea)",
                    placeholder="FE9133\nFE9134\nITPA5678",
                    height=150,
                    key="invoice_numbers_input"
                )
                
                if st.button("🔍 Buscar Facturas", type="primary", key="btn_search_invoices"):
                    if invoice_numbers_input:
                        invoice_numbers = [
                            num.strip() 
                            for num in invoice_numbers_input.split('\n') 
                            if num.strip()
                        ]
                        
                        with st.spinner(f"Buscando {len(invoice_numbers)} facturas..."):
                            invoices_found = drive_manager.search_invoices_by_numbers(invoice_numbers)
                    else:
                        st.warning("⚠️ Ingresa al menos un número de factura")
            
            # Mostrar resultados
            if invoices_found:
                found = [inv for inv in invoices_found if inv.get('encontrado')]
                not_found = [inv for inv in invoices_found if not inv.get('encontrado')]
                
                if found:
                    st.success(f"✅ {len(found)} facturas encontradas")
                    
                    # Botón de descarga masiva
                    st.markdown("### 📦 Descarga Masiva")
                    if st.button(
                        f"⬇️ Descargar todas ({len(found)} facturas) en ZIP",
                        type="primary",
                        use_container_width=True,
                        key="btn_download_zip"
                    ):
                        with st.spinner("Preparando descarga..."):
                            zip_content = drive_manager.download_multiple_files(found)
                            if zip_content:
                                st.download_button(
                                    label=f"📥 Descargar ZIP ({len(found)} archivos)",
                                    data=zip_content,
                                    file_name=f"Facturas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                    mime="application/zip",
                                    use_container_width=True,
                                    key="btn_final_download_zip"
                                )
                    
                    st.markdown("---")
                    st.markdown("### 📄 Facturas Individuales")
                    
                    # Mostrar cada factura
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
                            file_content = drive_manager.download_file(inv['id'], inv['nombre'])
                            if file_content:
                                st.download_button(
                                    "⬇️",
                                    file_content,
                                    inv['nombre'],
                                    mime="application/pdf",
                                    key=f"dl_{idx}",
                                    use_container_width=True
                                )
                
                if not_found:
                    st.markdown("---")
                    st.warning(f"⚠️ {len(not_found)} facturas no encontradas:")
                    for nf in not_found:
                        st.write(f"❌ {nf['numero_factura']}")
            
    except ImportError as e:
        st.error("❌ Error: No se pudo importar DriveManager")
        st.info("Verifica que el archivo modules/drive_manager.py existe")
        st.code(str(e))
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("💡 Verifica que el archivo .streamlit/secrets.toml esté configurado correctamente")
        st.code(str(e))

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 12px;'>
        Sistema de Facturación Finkargo v1.0 | 2024
    </div>
    """,
    unsafe_allow_html=True
)
