import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tarifación de Catálogo - Comfaboy", layout="wide")
st.title("⚙️ Simulador de Tarifación por Catálogo (200+ Servicios)")
st.markdown("Carga tu archivo plano, selecciona un servicio del catálogo y realiza el estudio técnico de costos e inductores de tarifa paso a paso.")

st.sidebar.header("📁 1. Carga de Catálogo")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo plano (Excel o CSV)", type=['xlsx', 'xls', 'csv'])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_catalogo = pd.read_csv(uploaded_file)
        else:
            df_catalogo = pd.read_excel(uploaded_file)
        
        st.sidebar.success(f"✅ Archivo cargado con {len(df_catalogo)} registros.")
        
        columnas = df_catalogo.columns.tolist()
        col_nombre = st.sidebar.selectbox("¿Qué columna contiene los nombres de los servicios?", columnas)
        
        lista_productos = df_catalogo[col_nombre].dropna().astype(str).unique()
        producto_seleccionado = st.sidebar.selectbox("🔍 Selecciona el servicio a tarifar:", lista_productos)
        
        st.header(f"🛠️ Tarifación y Costeo: {producto_seleccionado}")
        
        st.markdown("---")
        st.header("2. Capacidad Instalada y Demanda")
        col1, col2 = st.columns(2)
        with col1:
            capacidad_maxima = st.number_input("Capacidad Máxima Instalada", min_value=1, value=1000, step=10)
        with col2:
            ocupacion_proyectada_pct = st.number_input("Ocupación Proyectada (%)", min_value=0.0, max_value=100.0, value=60.0, step=1.0)
            ocupacion_proyectada = ocupacion_proyectada_pct / 100.0

        unidades_proyectadas = int(capacidad_maxima * ocupacion_proyectada)
        st.info(f"📌 **Demanda Proyectada a Costear:** {unidades_proyectadas} unidades.")

        st.markdown("---")
        st.header("3. Estudio Técnico de Costos (Directos e Indirectos)")
        col_cf, col_cv = st.columns(2)

        with col_cf:
            st.subheader("Costos Fijos")
            cf_directos = st.number_input("Costos Fijos DIRECTOS [\$]", value=0.0, step=500000.0)
            cf_indirectos = st.number_input("Costos Fijos INDIRECTOS [\$]", value=0.0, step=500000.0)
            cf_total = cf_directos + cf_indirectos

        with col_cv:
            st.subheader("Costos Variables Unitarios")
            cv_directos_u = st