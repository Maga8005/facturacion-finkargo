"""
Sistema de Consolidación de Facturas - Finkargo
Aplicación Streamlit para procesar y consolidar datos de facturación
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(
    page_title="Facturación Finkargo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📊 Sistema de Consolidación de Facturas")
st.markdown("---")

# Sidebar con información
with st.sidebar:
    st.header("ℹ️ Información")
    st.info("Sistema para consolidar facturas de NUVA y Netsuite")
    st.markdown("**Usuario:** Alejandro")
    st.markdown("**Fecha:** " + datetime.now().strftime("%Y-%m-%d"))

# Crear tabs principales
tab1, tab2, tab3 = st.tabs(["📁 Carga de Archivos", "📈 Dashboard", "📋 Generar Reporte"])

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
