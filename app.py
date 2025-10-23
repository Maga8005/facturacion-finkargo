"""
Sistema de Consolidación de Facturas - Finkargo
Aplicación Streamlit para procesar y consolidar datos de facturación
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from modules.drive_manager import DriveManager
from modules.file_processor import FileProcessor
import tempfile
import os
from io import BytesIO

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
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'stats' not in st.session_state:
    st.session_state.stats = None
if 'datos_por_hoja' not in st.session_state:
    st.session_state.datos_por_hoja = None

# Función helper para Drive Manager
def get_drive_manager():
    """Obtener o crear instancia de DriveManager"""
    try:
        if st.session_state.drive_manager is None:
            st.session_state.drive_manager = DriveManager()
        return st.session_state.drive_manager
    except:
        return None

# Título principal
st.title("📊 Sistema de Consolidación de Facturas")
st.markdown("---")

# Sidebar con información y autenticación
with st.sidebar:
    st.header("ℹ️ Información")
    st.info("Sistema para consolidar facturas de Noova y Netsuite")
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
                    # Eliminar credenciales del session state
                    if 'google_drive_creds' in st.session_state:
                        del st.session_state.google_drive_creds
                    if 'drive_manager' in st.session_state:
                        del st.session_state.drive_manager

                    # Eliminar archivo de token persistente
                    import os
                    if os.path.exists('token.json'):
                        os.remove('token.json')

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
    
    # Mostrar info de datos procesados
    st.markdown("---")
    st.header("📊 Estado de Datos")
    
    if st.session_state.processed and st.session_state.stats:
        st.success(f"✅ Datos procesados")
        st.metric("Total Facturas", st.session_state.stats.get('total_facturas', 0))
        st.metric("Facturas sin valor", st.session_state.stats.get('sin_valor', 0))
    else:
        st.info("📂 No hay datos procesados")

# Crear tabs principales
tab1, tab2, tab3, tab4 = st.tabs(["📁 Carga de Archivos", "📈 Dashboard", "📋 Generar Reporte", "🔍 Buscar en Drive"])

# ==================== TAB 1: CARGA DE ARCHIVOS ====================
with tab1:
    st.header("📁 Carga de Archivos Excel")

    # Instrucciones claras
    st.info("""
    ### 📋 Archivos requeridos para la consolidación:

    1. **💰 Informe Netsuite (.xls)** - Obligatorio
       - Sistema: Netsuite (contable)
       - Contenido: Números de factura, monedas y valores
       - Formato: Archivo Excel antiguo (.xls)

    2. **📑 Facturas Noova (.xlsx)** - Obligatorio
       - Sistema: Noova (facturación)
       - Contenido: Facturas emitidas (FE, ITPA, GL, etc.)
       - Formato: Archivo Excel moderno (.xlsx)

    3. **🔄 Notas Crédito Noova (.xlsx)** - Opcional
       - Sistema: Noova (facturación)
       - Contenido: Notas de crédito emitidas (NCFE, etc.)
       - Formato: Archivo Excel moderno (.xlsx)
    """)

    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("💰 Informe Netsuite")
        st.caption("📊 Sistema contable - Valores y monedas")
        st.markdown("**Formato:** `.xls` o `.xlsx`")
        archivo_netsuite = st.file_uploader(
            "📂 Sube informe consolidado de Netsuite",
            type=["xls", "xlsx"],
            key="netsuite",
            help="Archivo: VistapredeterminadaTransacción.xls o .xlsx\nHoja: VistapredeterminadaTransaccin\nContiene: Números de factura, monedas y valores"
        )
        if archivo_netsuite:
            st.success(f"✅ {archivo_netsuite.name}")
            st.info(f"📦 Tamaño: {archivo_netsuite.size / 1024:.1f} KB")

    with col2:
        st.subheader("📑 Facturas Noova")
        st.caption("🧾 Sistema de facturación - Facturas emitidas")
        st.markdown("**Formato:** `.xlsx` (Excel moderno)")
        archivo_facturas = st.file_uploader(
            "📂 Sube archivo de Facturas Noova",
            type=["xlsx"],
            key="facturas",
            help="Archivo: Documentos_YYYYMMDD.xlsx\nHoja: Documentos\nContiene: Facturas emitidas por Noova"
        )
        if archivo_facturas:
            st.success(f"✅ {archivo_facturas.name}")
            st.info(f"📦 Tamaño: {archivo_facturas.size / 1024:.1f} KB")

    with col3:
        st.subheader("🔄 Notas Crédito Noova")
        st.caption("📝 Sistema de facturación - Notas de crédito")
        st.markdown("**Formato:** `.xlsx` **| Opcional**")
        archivo_notas = st.file_uploader(
            "📂 Sube archivo de Notas de Crédito (opcional)",
            type=["xlsx"],
            key="notas_credito",
            help="Archivo: Documentos_YYYYMMDD.xlsx\nHoja: Documentos\nContiene: Notas de crédito emitidas por Noova"
        )
        if archivo_notas:
            st.success(f"✅ {archivo_notas.name}")
            st.info(f"📦 Tamaño: {archivo_notas.size / 1024:.1f} KB")

    st.markdown("---")

    # Mostrar resumen de archivos cargados
    archivos_cargados = []
    if archivo_netsuite:
        archivos_cargados.append("✅ Netsuite")
    else:
        archivos_cargados.append("❌ Netsuite (obligatorio)")

    if archivo_facturas:
        archivos_cargados.append("✅ Facturas Noova")
    else:
        archivos_cargados.append("❌ Facturas Noova (obligatorio)")

    if archivo_notas:
        archivos_cargados.append("✅ Notas Crédito Noova")
    else:
        archivos_cargados.append("⚪ Notas Crédito (opcional)")

    col_status, col_btn = st.columns([1, 1])

    with col_status:
        st.markdown("### 📊 Estado de archivos:")
        for estado in archivos_cargados:
            st.markdown(f"- {estado}")

    with col_btn:
        st.markdown("### 🚀 Acción:")
        listo_para_procesar = archivo_netsuite and archivo_facturas

        if st.button(
            "🚀 Procesar Archivos",
            type="primary",
            use_container_width=True,
            disabled=not listo_para_procesar
        ):
            if not archivo_netsuite:
                st.error("❌ Falta el archivo Netsuite (.xls)")
                st.warning("💡 El informe de Netsuite es obligatorio para la consolidación")
            elif not archivo_facturas:
                st.error("❌ Falta el archivo de Facturas Noova (.xlsx)")
                st.warning("💡 El archivo de Facturas es obligatorio para la consolidación")
            else:
                with st.spinner("⏳ Procesando archivos... Esto puede tomar unos segundos."):
                    try:
                        # Crear directorio temporal
                        with tempfile.TemporaryDirectory() as tmpdir:
                            # Guardar archivos temporalmente
                            netsuite_path = os.path.join(tmpdir, archivo_netsuite.name)
                            with open(netsuite_path, 'wb') as f:
                                f.write(archivo_netsuite.getbuffer())
                            
                            facturas_path = os.path.join(tmpdir, archivo_facturas.name)
                            with open(facturas_path, 'wb') as f:
                                f.write(archivo_facturas.getbuffer())
                            
                            notas_path = None
                            if archivo_notas:
                                notas_path = os.path.join(tmpdir, archivo_notas.name)
                                with open(notas_path, 'wb') as f:
                                    f.write(archivo_notas.getbuffer())
                            
                            # Inicializar procesador
                            processor = FileProcessor(
                                column_mapping_path='config/column_mapping.json',
                                classification_rules_path='config/classification_rules.json'
                            )
                            
                            # Leer archivos
                            df_netsuite = processor.read_netsuite_file(netsuite_path)
                            df_facturas = processor.read_noova_file(facturas_path, 'facturas')
                            df_notas = None
                            if notas_path:
                                df_notas = processor.read_noova_file(notas_path, 'notas_credito')
                            
                            # Consolidar
                            df_consolidated = processor.consolidate_data(df_netsuite, df_facturas, df_notas)
                            
                            # Preparar para archivo maestro
                            datos_por_hoja = processor.prepare_for_master_sheet(df_consolidated)
                            
                            # Obtener estadísticas
                            stats = processor.get_statistics(df_consolidated)
                            
                            # Guardar en session_state
                            st.session_state.consolidated_data = df_consolidated
                            st.session_state.datos_por_hoja = datos_por_hoja
                            st.session_state.stats = stats
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
                            
                            st.info("👉 Ve al Dashboard para ver análisis detallado o a 'Generar Reporte' para descargar los datos")
                            
                    except Exception as e:
                        st.error(f"❌ Error al procesar archivos: {str(e)}")
                        with st.expander("Ver detalles del error"):
                            st.exception(e)

# ==================== TAB 2: DASHBOARD ====================
with tab2:
    st.header("📈 Dashboard de Facturación")

    if not st.session_state.processed:
        st.info("ℹ️ Procesa los archivos en la pestaña 'Carga de Archivos' para ver el dashboard.")
        st.markdown("---")
        # Mostrar métricas vacías
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Total Facturado", "$0")
        with col2:
            st.metric("📄 Facturas Procesadas", "0")
        with col3:
            st.metric("✅ Clasificadas", "0")
        with col4:
            st.metric("⚠️ Sin Clasificar", "0")
    else:
        stats = st.session_state.stats
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_cop = stats.get('total_valor_cop', 0)
            st.metric(
                label="💰 Total COP",
                value=f"${total_cop:,.0f}"
            )

        with col2:
            total_usd = stats.get('total_valor_usd', 0)
            st.metric(
                label="💵 Total USD",
                value=f"${total_usd:,.2f}"
            )

        with col3:
            total = stats.get('total_facturas', 0)
            st.metric(
                label="📄 Total Facturas",
                value=f"{total:,}"
            )

        with col4:
            sin_valor = stats.get('sin_valor', 0)
            st.metric(
                label="⚠️ Sin Valor",
                value=sin_valor,
                delta=f"-{sin_valor}" if sin_valor > 0 else None
            )

        st.markdown("---")

        # Gráficos
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Distribución por Tipo de Factura")
            if 'por_tipo' in stats and stats['por_tipo']:
                df_tipo = pd.DataFrame(
                    list(stats['por_tipo'].items()),
                    columns=['Tipo', 'Cantidad']
                )
                st.bar_chart(df_tipo.set_index('Tipo'))
            else:
                st.info("No hay datos de tipos disponibles")

        with col2:
            st.subheader("🏷️ Distribución por Categoría")
            if 'por_categoria' in stats and stats['por_categoria']:
                df_cat = pd.DataFrame(
                    list(stats['por_categoria'].items()),
                    columns=['Categoría', 'Cantidad']
                )
                st.bar_chart(df_cat.set_index('Categoría'))
            else:
                st.info("No hay datos de categorías disponibles")
        
        st.markdown("---")
        
        # Distribución por hoja
        st.subheader("📄 Facturas por Hoja de Destino")
        if 'facturas_por_hoja' in stats and stats['facturas_por_hoja']:
            col1, col2 = st.columns([3, 2])
            
            with col1:
                df_hoja = pd.DataFrame(
                    list(stats['facturas_por_hoja'].items()),
                    columns=['Hoja', 'Cantidad']
                )
                st.bar_chart(df_hoja.set_index('Hoja'))
            
            with col2:
                st.dataframe(df_hoja, use_container_width=True, hide_index=True)
        
        # Advertencias
        sin_clasificar = stats.get('sin_clasificar', 0)
        if sin_clasificar > 0 or sin_valor > 0:
            st.markdown("---")
            st.warning("### ⚠️ Advertencias")
            
            if sin_valor > 0:
                st.markdown(f"- **{sin_valor} facturas sin valor** en Netsuite")
            
            if sin_clasificar > 0:
                st.markdown(f"- **{sin_clasificar} conceptos sin clasificar** automáticamente")

# ==================== TAB 3: GENERAR REPORTE ====================
with tab3:
    st.header("📋 Generación de Reportes")

    if not st.session_state.processed:
        st.info("ℹ️ Procesa los archivos primero para generar reportes.")
    else:
        datos_por_hoja = st.session_state.datos_por_hoja

        # ARCHIVO MAESTRO COMPLETO - OPCIÓN HÍBRIDA
        st.subheader("📥 Archivo Maestro de Facturación")
        st.info(f"📊 El archivo maestro contiene **{len(datos_por_hoja)}** hojas con todos los datos consolidados")

        # Resumen de hojas
        col_info1, col_info2 = st.columns(2)

        with col_info1:
            st.markdown("**Hojas incluidas:**")
            for hoja_nombre, hoja_df in datos_por_hoja.items():
                st.markdown(f"✅ {hoja_nombre} ({len(hoja_df)} registros)")

        with col_info2:
            st.markdown("**Información:**")
            total_registros = sum(len(df) for df in datos_por_hoja.values())
            st.metric("Total de registros", total_registros)

        st.markdown("---")

        # Generar archivo Excel
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        file_name = f"Maestro_Facturacion_{timestamp}.xlsx"

        buffer_maestro = BytesIO()
        with pd.ExcelWriter(buffer_maestro, engine='openpyxl') as writer:
            for hoja_nombre, hoja_df in datos_por_hoja.items():
                # Excel tiene límite de 31 caracteres para nombres de hoja
                sheet_name = hoja_nombre[:31] if len(hoja_nombre) > 31 else hoja_nombre
                hoja_df.to_excel(writer, sheet_name=sheet_name, index=False)

        file_bytes = buffer_maestro.getvalue()

        # Botones de acción
        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            st.markdown("### 🚀 Generar y Subir a Drive")
            st.caption("Sube automáticamente a Google Drive (recomendado)")

            if st.button("🚀 Generar y Subir a Google Drive", type="primary", use_container_width=True):
                drive_manager = get_drive_manager()

                if drive_manager and drive_manager.is_authenticated():
                    with st.spinner("📤 Subiendo archivo a Google Drive..."):
                        # Crear carpeta si no existe
                        folder_id = drive_manager.create_folder_if_not_exists("Reportes Facturación")

                        if folder_id:
                            # Subir archivo
                            result = drive_manager.upload_file(file_bytes, file_name, folder_id)

                            if result:
                                st.success("✅ ¡Archivo subido exitosamente a Google Drive!")
                                st.markdown("---")

                                st.markdown(f"**📄 Archivo:** {result['nombre']}")
                                st.markdown(f"**📦 Tamaño:** {result['tamano']}")
                                st.markdown(f"**📅 Fecha:** {timestamp}")

                                st.link_button(
                                    "🔗 Abrir en Google Drive",
                                    result['link'],
                                    use_container_width=True
                                )

                                st.info("💡 El archivo está en modo SOLO LECTURA. Para trabajar, descarga una copia o duplícalo en Drive.")
                            else:
                                st.error("❌ Error al subir el archivo")
                        else:
                            st.error("❌ Error al crear/obtener carpeta en Drive")
                else:
                    st.warning("⚠️ Conecta con Google Drive primero")
                    st.caption("Ve a la pestaña 'Buscar en Drive' para autenticarte")

        with col_btn2:
            st.markdown("### 📥 Descargar Copia Local")
            st.caption("Descarga el archivo a tu computadora")

            st.download_button(
                label="📥 Descargar Copia Local",
                data=file_bytes,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

            st.caption("⚠️ Al descargar creas una copia local que puede quedar desactualizada")

        st.markdown("---")

        # Historial de archivos maestros
        st.subheader("📚 Historial de Archivos Generados")

        drive_manager = get_drive_manager()
        if drive_manager and drive_manager.is_authenticated():
            with st.expander("Ver archivos anteriores en Google Drive", expanded=False):
                with st.spinner("Cargando historial..."):
                    folder_id = drive_manager.create_folder_if_not_exists("Reportes Facturación")
                    archivos_anteriores = drive_manager.list_master_files(folder_id, limit=10)

                    if archivos_anteriores:
                        st.info(f"📊 Se encontraron {len(archivos_anteriores)} archivos anteriores")

                        for archivo in archivos_anteriores:
                            col_a, col_b, col_c = st.columns([3, 1, 1])

                            with col_a:
                                st.markdown(f"📄 **{archivo['nombre']}**")
                                st.caption(f"Creado: {archivo['fecha_creacion'][:10]} | Tamaño: {archivo['tamano']}")

                            with col_b:
                                # Solo mostrar botón si hay link válido
                                link = archivo.get('link', '').strip()
                                if link and link.startswith('http') and len(link) > 10:
                                    try:
                                        st.link_button(
                                            "👁️ Ver",
                                            link,
                                            key=f"ver_{archivo['id']}"
                                        )
                                    except:
                                        st.caption("-")
                                else:
                                    st.caption("-")

                            with col_c:
                                file_content = drive_manager.download_file(archivo['id'], archivo['nombre'])
                                if file_content:
                                    st.download_button(
                                        "⬇️",
                                        file_content,
                                        archivo['nombre'],
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        key=f"dl_{archivo['id']}"
                                    )

                            st.markdown("---")
                    else:
                        st.info("No hay archivos anteriores")
        else:
            st.info("💡 Conecta con Google Drive para ver el historial de archivos")

        st.markdown("---")

        # DESCARGA POR HOJAS INDIVIDUALES
        st.subheader("📄 Filtrar y Descargar Facturas")
        st.caption("Puedes ver todas las facturas consolidadas o filtrar por hoja específica")

        # Selector de hoja con opción "Todas"
        st.subheader("📄 Seleccionar Vista")

        # Agregar opción "Todas las Facturas"
        opciones_hojas = ["📊 Todas las Facturas (Consolidado)"] + list(datos_por_hoja.keys())

        hoja_seleccionada = st.selectbox(
            "Vista de datos:",
            opciones_hojas
        )

        # Determinar qué DataFrame mostrar
        if hoja_seleccionada == "📊 Todas las Facturas (Consolidado)":
            # Combinar todas las hojas
            dfs_a_combinar = []
            for nombre_hoja, df_hoja_temp in datos_por_hoja.items():
                df_temp = df_hoja_temp.copy()
                df_temp['Hoja Origen'] = nombre_hoja  # Agregar columna de origen
                dfs_a_combinar.append(df_temp)

            df_hoja = pd.concat(dfs_a_combinar, ignore_index=True)
            st.info(f"📊 Vista consolidada: **{len(df_hoja)}** facturas de **{len(datos_por_hoja)}** hojas")

        elif hoja_seleccionada in datos_por_hoja:
            df_hoja = datos_por_hoja[hoja_seleccionada]
            st.info(f"📊 Total de registros en esta hoja: **{len(df_hoja)}**")

        else:
            df_hoja = None

        if df_hoja is not None and not df_hoja.empty:
            # Mostrar preview
            st.markdown("### 👀 Vista Previa")
            st.dataframe(df_hoja.head(10), use_container_width=True)

            # DEBUG: Mostrar todos los códigos disponibles
            with st.expander("🔍 DEBUG - Ver todos los códigos de desembolso"):
                if 'Codigo del desembolso' in df_hoja.columns:
                    codigos_unicos = df_hoja['Codigo del desembolso'].unique()
                    st.write(f"Total: {len(codigos_unicos)} códigos únicos")
                    st.dataframe(pd.DataFrame({
                        'Código': [str(c) for c in codigos_unicos if pd.notna(c)]
                    }), use_container_width=True)
            
            st.markdown("---")
            
            # Filtros
            st.subheader("🔍 Filtros (Opcional)")

            # Si es vista consolidada, agregar filtro por hoja origen
            if hoja_seleccionada == "📊 Todas las Facturas (Consolidado)":
                col_hoja_filtro = st.columns(1)[0]
                with col_hoja_filtro:
                    hojas_origen = ['Todas'] + sorted(df_hoja['Hoja Origen'].unique().tolist())
                    hoja_origen_filtro = st.selectbox(
                        "🗂️ Filtrar por tipo de factura:",
                        hojas_origen,
                        help="Filtra por hoja de origen (Costos Fijos o Mandato)"
                    )
            else:
                hoja_origen_filtro = None

            col1, col2 = st.columns(2)

            with col1:
                # Filtro por código de desembolso
                if 'Codigo del desembolso' in df_hoja.columns:
                    # Limpiar y normalizar códigos
                    codigos_disponibles = [str(c).strip() for c in df_hoja['Codigo del desembolso'].unique() if pd.notna(c) and str(c).strip()]
                    codigos_disponibles = sorted(codigos_disponibles)

                    # Debug: mostrar total de códigos únicos
                    st.caption(f"💡 {len(codigos_disponibles)} códigos únicos disponibles")
                else:
                    codigos_disponibles = []

                codigo_filtro = st.multiselect(
                    "Códigos de Desembolso",
                    options=codigos_disponibles,
                    default=[],
                    help="Deja vacío para incluir todos"
                )

            with col2:
                # Filtro por moneda
                if 'Moneda' in df_hoja.columns:
                    monedas = [str(m) for m in df_hoja['Moneda'].unique() if pd.notna(m)]
                    monedas = sorted(monedas)
                else:
                    monedas = []

                moneda_filtro = st.multiselect(
                    "Moneda",
                    options=monedas,
                    default=[],
                    help="Deja vacío para incluir todas"
                )
            
            # Aplicar filtros
            df_filtrado = df_hoja.copy()

            # Filtro por hoja origen (solo en vista consolidada)
            if hoja_origen_filtro and hoja_origen_filtro != 'Todas' and 'Hoja Origen' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['Hoja Origen'] == hoja_origen_filtro]

            if codigo_filtro:
                # Normalizar la columna y el filtro (trim espacios)
                df_filtrado['_codigo_normalizado'] = df_filtrado['Codigo del desembolso'].astype(str).str.strip()
                codigo_filtro_normalizado = [str(c).strip() for c in codigo_filtro]

                df_filtrado = df_filtrado[df_filtrado['_codigo_normalizado'].isin(codigo_filtro_normalizado)]
                df_filtrado = df_filtrado.drop(columns=['_codigo_normalizado'])

                # Debug: mostrar resultados
                st.info(f"🔍 Filtrando por {len(codigo_filtro)} código(s): {', '.join(codigo_filtro[:3])}{'...' if len(codigo_filtro) > 3 else ''}")

            if moneda_filtro and 'Moneda' in df_filtrado.columns:
                # Convertir a string para comparación
                df_filtrado = df_filtrado[df_filtrado['Moneda'].astype(str).str.strip().isin(moneda_filtro)]

            if len(df_filtrado) < len(df_hoja):
                st.success(f"✅ Filtros aplicados: {len(df_filtrado)} de {len(df_hoja)} registros")
            elif codigo_filtro or moneda_filtro or (hoja_origen_filtro and hoja_origen_filtro != 'Todas'):
                st.warning(f"⚠️ No se encontraron resultados con los filtros seleccionados")
            
            st.markdown("---")
            
            # Opciones de exportación
            st.subheader("📤 Descargar Reporte")

            # Nombre de archivo según vista y filtros aplicados
            if codigo_filtro:
                # Si hay filtro de código, usar el código en el nombre del archivo
                if len(codigo_filtro) == 1:
                    # Un solo código: usar el código directamente
                    codigo_limpio = str(codigo_filtro[0]).replace(":", "_").replace("/", "_")
                    nombre_archivo = f"Factura_{codigo_limpio}"
                    nombre_hoja_excel = codigo_limpio[:31]
                else:
                    # Múltiples códigos: usar "Multiples_codigos" + cantidad
                    nombre_archivo = f"Facturas_Multiples_{len(codigo_filtro)}_codigos"
                    nombre_hoja_excel = "Multiples_Codigos"
            elif hoja_seleccionada == "📊 Todas las Facturas (Consolidado)":
                nombre_archivo = "Consolidado_Todas_Facturas"
                nombre_hoja_excel = "Consolidado"
            else:
                nombre_archivo = hoja_seleccionada.replace(" ", "_")
                nombre_hoja_excel = hoja_seleccionada[:31]  # Excel limita a 31 caracteres

            col1, col2, col3 = st.columns(3)

            with col1:
                # Descargar Excel
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_filtrado.to_excel(writer, sheet_name=nombre_hoja_excel, index=False)

                st.download_button(
                    label="📥 Descargar Excel",
                    data=buffer.getvalue(),
                    file_name=f"{nombre_archivo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            with col2:
                # Descargar CSV
                csv = df_filtrado.to_csv(index=False)
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv,
                    file_name=f"{nombre_archivo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col3:
                # Placeholder para Google Sheets
                if st.button("📤 Subir a Google Sheets", use_container_width=True):
                    st.info("🚧 Funcionalidad en desarrollo (Fase 2)")
            
            # Búsqueda de PDFs en Drive
            st.markdown("---")
            st.subheader("📎 Buscar PDFs Asociados en Google Drive")
            
            if st.button("🔍 Buscar PDFs de este reporte", type="primary", use_container_width=True):
                drive_manager = get_drive_manager()
                
                if drive_manager and drive_manager.is_authenticated():
                    # Extraer números de factura del reporte filtrado
                    if '# Factura' in df_filtrado.columns:
                        numeros_factura = df_filtrado['# Factura'].dropna().unique().tolist()
                        
                        st.info(f"🔍 Buscando {len(numeros_factura)} facturas en Google Drive...")
                        
                        with st.spinner("Buscando..."):
                            invoices_found = drive_manager.search_invoices_by_numbers(numeros_factura)
                            
                            found = [inv for inv in invoices_found if inv.get('encontrado')]
                            not_found = [inv for inv in invoices_found if not inv.get('encontrado')]
                            
                            if found:
                                st.success(f"✅ {len(found)} PDFs encontrados")
                                
                                # Botón descarga masiva
                                if st.button(f"⬇️ Descargar todos ({len(found)}) en ZIP", key="zip_reportes"):
                                    with st.spinner("Preparando descarga..."):
                                        zip_content = drive_manager.download_multiple_files(found)
                                        if zip_content:
                                            st.download_button(
                                                label=f"📥 Descargar ZIP",
                                                data=zip_content,
                                                file_name=f"Facturas_Reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                                mime="application/zip",
                                                use_container_width=True
                                            )
                            
                            if not_found:
                                st.warning(f"⚠️ {len(not_found)} facturas no encontradas en Drive")
                    else:
                        st.error("❌ La columna '# Factura' no existe en los datos")
                else:
                    st.warning("⚠️ Conecta con Google Drive en la pestaña 'Buscar en Drive' primero")

# ==================== TAB 4: BUSCAR EN DRIVE ====================
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
        with st.expander("Ver detalles del error"):
            st.exception(e)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 12px;'>
        Sistema de Facturación Finkargo v1.0 - Fase 1 MVP | Octubre 2025
    </div>
    """,
    unsafe_allow_html=True
)