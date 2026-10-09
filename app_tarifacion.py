import streamlit as st
import pandas as pd

# Configuración inicial de la página
st.set_page_config(page_title="Simulador de Tarifación - Comfaboy", layout="wide")
st.title("⚙️ Simulador Maestro de Tarifación para Nuevos Servicios")
st.markdown("Metodología de Costeo por Absorción, Análisis de Mercado y Asignación de Subsidios (Categorías A, B, C y D).")

# --- PASO 1: DEFINICIÓN Y CAPACIDAD ---
st.header("1. Definición del Servicio y Capacidad Instalada")
col1, col2, col3 = st.columns(3)

with col1:
    nombre_servicio = st.text_input("Nombre del Servicio / Producto", value="Ej. Curso de Natación")
with col2:
    capacidad_maxima = st.number_input("Capacidad Máxima Instalada (Unidades/Cupos por mes o año)", min_value=1, value=1000, step=10)
with col3:
    ocupacion_proyectada_pct = st.number_input("Ocupación Proyectada (%)", min_value=0.0, max_value=100.0, value=60.0, step=1.0)
    ocupacion_proyectada = ocupacion_proyectada_pct / 100.0

unidades_proyectadas = int(capacidad_maxima * ocupacion_proyectada)

st.info(f"📌 **Demanda Proyectada a Costear:** {unidades_proyectadas} unidades/cupos (basado en el {ocupacion_proyectada_pct}% de la capacidad máxima).")

# --- PASO 2: ESTRUCTURA DE COSTOS (ABSORCIÓN) ---
st.markdown("---")
st.header("2. Estudio Técnico de Costos")
st.write("Ingresa los costos asociados para calcular el Costo Técnico Unitario mediante costeo por absorción.")

col_cf, col_cv = st.columns(2)

with col_cf:
    st.subheader("Costos Fijos (Independientes de la venta)")
    cf_directos = st.number_input("Costos Fijos DIRECTOS (Ej. Nómina instructores, licencias) [$]", value=20000000.0, step=500000.0)
    cf_indirectos = st.number_input("Costos Fijos INDIRECTOS (Ej. Arriendo, servicios, aseo, admón) [$]", value=10000000.0, step=500000.0)
    cf_total = cf_directos + cf_indirectos

with col_cv:
    st.subheader("Costos Variables Unitarios (Por cada usuario)")
    cv_directos_u = st.number_input("Costo Variable DIRECTO Unitario (Ej. Materiales, refrigerio) [$]", value=15000.0, step=500.0)
    cv_indirectos_u = st.number_input("Costo Variable INDIRECTO Unitario (Ej. Mantenimiento por uso) [$]", value=5000.0, step=500.0)
    cv_unitario_total = cv_directos_u + cv_indirectos_u

# Cálculos de Costeo
if unidades_proyectadas > 0:
    costo_fijo_unitario = cf_total / unidades_proyectadas
    costo_tecnico_unitario = costo_fijo_unitario + cv_unitario_total
    costo_total_operacion = cf_total + (cv_unitario_total * unidades_proyectadas)
else:
    costo_fijo_unitario = 0
    costo_tecnico_unitario = 0
    costo_total_operacion = cf_total

df_costos = pd.DataFrame({
    "Rubro": ["Costos Fijos Totales", "Costo Variable Total (Proyectado)", "COSTO TOTAL DE OPERACIÓN", "Costo Técnico UNITARIO (Punto de Equilibrio)"],
    "Valor": [f"${cf_total:,.2f}", f"${(cv_unitario_total * unidades_proyectadas):,.2f}", f"${costo_total_operacion:,.2f}", f"${costo_tecnico_unitario:,.2f}"]
}).set_index("Rubro")
st.table(df_costos)


# --- PASO 3: TARIFA PLENA Y MERCADO ---
st.markdown("---")
st.header("3. Indicadores de Mercado y Fijación de Tarifa Plena (Categoría C)")
st.write("Compara el costo técnico con el mercado y define la tarifa plena.")

col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric("Costo Técnico Unitario", f"${costo_tecnico_unitario:,.2f}")
with col_m2:
    tarifa_mercado = st.number_input("Tarifa Promedio del Mercado [$]", value=float(costo_tecnico_unitario * 1.2), step=1000.0)
with col_m3:
    # La tarifa C por defecto es igual al costo técnico, pero el usuario puede subirla para hacer margen cruzado o igualarla al mercado
    tarifa_c = st.number_input("TARIFA PLENA (Cat. C) a fijar [$]", value=float(costo_tecnico_unitario), step=1000.0)

diferencia_mercado = tarifa_c - tarifa_mercado
st.caption(f"💡 *Nota: Tu tarifa plena está {'por encima' if diferencia_mercado > 0 else 'por debajo'} del mercado en ${abs(diferencia_mercado):,.2f}.*")

# --- PASO 4: MATRIZ DE SUBSIDIOS Y RENTABILIDAD ---
st.markdown("---")
st.header("4. Matriz de Subsidios y Rentabilidad (Cat D)")

col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    sub_a_pct = st.number_input("Subsidio Categoría A (%)", min_value=0.0, max_value=100.0, value=80.0, step=1.0) / 100.0
with col_s2:
    sub_b_pct = st.number_input("Subsidio Categoría B (%)", min_value=0.0, max_value=100.0, value=70.0, step=1.0) / 100.0
with col_s3:
    margen_d_pct = st.number_input("Margen de Rentabilidad Cat D (%)", min_value=0.0, max_value=200.0, value=15.0, step=1.0) / 100.0

tarifa_a = tarifa_c * (1 - sub_a_pct)
tarifa_b = tarifa_c * (1 - sub_b_pct)
tarifa_d = tarifa_c * (1 + margen_d_pct)

v_sub_a = tarifa_c * sub_a_pct
v_sub_b = tarifa_c * sub_b_pct

st.markdown("### 📌 Cuadro Tarifario Autorizado")
df_tarifas = pd.DataFrame({
    "Categoría": ["Categoría A", "Categoría B", "Categoría C (Plena)", "Categoría D (No Afiliado)"],
    "Política Aplicada": [f"Subsidio {sub_a_pct*100:.0f}%", f"Subsidio {sub_b_pct*100:.0f}%", "Punto Base", f"Margen +{margen_d_pct*100:.0f}%"],
    "Tarifa Usuario": [f"${tarifa_a:,.2f}", f"${tarifa_b:,.2f}", f"${tarifa_c:,.2f}", f"${tarifa_d:,.2f}"],
    "Esfuerzo Caja (Subsidio)": [f"${v_sub_a:,.2f}", f"${v_sub_b:,.2f}", "$0.00", "$0.00"]
}).set_index("Categoría")
st.table(df_tarifas)

# --- PASO 5: PROYECCIÓN FINANCIERA ---
st.markdown("---")
st.header("5. Simulación de Mezcla (Mix de Demanda) y P&G del Servicio")
st.write(f"Distribuye las **{unidades_proyectadas}** unidades proyectadas entre las 4 categorías para evaluar la viabilidad.")

col_p1, col_p2, col_p3, col_p4 = st.columns(4)
with col_p1:
    q_a = st.number_input("Unidades Cat A", min_value=0, value=int(unidades_proyectadas * 0.60), step=5)
with col_p2:
    q_b = st.number_input("Unidades Cat B", min_value=0, value=int(unidades_proyectadas * 0.20), step=5)
with col_p3:
    q_c = st.number_input("Unidades Cat C", min_value=0, value=int(unidades_proyectadas * 0.15), step=5)
with col_p4:
    q_d = st.number_input("Unidades Cat D", min_value=0, value=int(unidades_proyectadas * 0.05), step=5)

total_mezcla = q_a + q_b + q_c + q_d
if total_mezcla != unidades_proyectadas:
    st.warning(f"⚠️ Atención: La suma de la mezcla ({total_mezcla}) es diferente a las unidades proyectadas ({unidades_proyectadas}). El P&G se calculará sobre la mezcla actual ({total_mezcla}).")

# Recalculamos costos sobre la mezcla real si difiere levemente
ct_real_mezcla = cf_total + (cv_unitario_total * total_mezcla)

ingresos_tarifas = (q_a * tarifa_a) + (q_b * tarifa_b) + (q_c * tarifa_c) + (q_d * tarifa_d)
subsidios_otorgados = (q_a * v_sub_a) + (q_b * v_sub_b)
ingresos_totales = ingresos_tarifas + subsidios_otorgados

resultado_operativo = ingresos_tarifas - ct_real_mezcla
sub_demanda = subsidios_otorgados
sub_oferta = -(resultado_operativo + sub_demanda)

df_pg = pd.DataFrame({
    "Indicador Financiero": [
        "Ingresos Recaudados (Tarifas)", 
        "Subsidio a la Demanda (Otorgado)", 
        "INGRESOS TOTALES DEL SERVICIO", 
        "Costos Totales de Operación", 
        "RESULTADO NETO (Déficit / Superávit)",
        "Subsidio a la Oferta (Asumido por la Caja)"
    ],
    "Valor Proyectado": [
        ingresos_tarifas, 
        sub_demanda, 
        ingresos_totales, 
        ct_real_mezcla, 
        resultado_operativo, 
        sub_oferta if sub_oferta > 0 else 0.0
    ]
}).set_index("Indicador Financiero")

st.dataframe(df_pg.style.format({"Valor Proyectado": "${:,.2f}"}).map(
    lambda x: 'color: red' if isinstance(x, float) and x < 0 else ('color: green' if isinstance(x, float) and x > 0 else ''),
    subset=["Valor Proyectado"]
), use_container_width=True)
