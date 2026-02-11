import streamlit as st
import pandas as pd
import plotly.express as px
import io
import requests

st.set_page_config(page_title="Dashboard RRHH CENOA", layout="wide")

SHEET_ID = "1XnsUZUZGH9itPCDf6jPpOIqfMIbX5s8nEe9JkF6ccqU"

@st.cache_data
def get_data(sheet_name, valor_name):
    # Construcción de URL y forzado de UTF-8 para evitar errores de tildes
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    response = requests.get(url)
    response.encoding = 'utf-8'
    
    df = pd.read_csv(io.StringIO(response.text))
    df = df.dropna(axis=1, how='all')
    df.columns = [c.strip().upper() for c in df.columns]
    
    # Identificar columnas de ID (Empresa y Provincia) y Meses
    id_vars = [col for col in df.columns if 'EMPRESA' in col or 'PROVINCIA' in col]
    value_vars = [col for col in df.columns if col not in id_vars]
    
    # Transformar a formato largo
    df_melted = df.melt(id_vars=id_vars, value_vars=value_vars, 
                        var_name='Mes', value_name=valor_name)
    return df_melted

# --- PROCESAMIENTO DE DATOS ---
try:
    df_dot = get_data("DOTACIÓN", "Dotación")
    df_rot = get_data("ROTACIÓN", "Rotación %")
    
    # Unificar nombres de columnas para el cruce
    df_dot.columns = ['EMPRESA', 'PROVINCIA', 'Mes', 'Dotación']
    df_rot.columns = ['EMPRESA', 'PROVINCIA', 'Mes', 'Rotación %']
    
    # Combinar ambas tablas en una sola base maestra
    df_final = pd.merge(df_dot, df_rot, on=['EMPRESA', 'PROVINCIA', 'Mes'])
except Exception as e:
    st.error(f"Error al procesar los datos: {e}")
    st.stop()

# --- INTERFAZ DEL DASHBOARD ---
st.title("📊 Control de Gestión RRHH - CENOA")
st.markdown("Analítico de Dotación y Rotación por Empresa y Provincia")

# Filtros en la barra lateral
with st.sidebar:
    st.header("Configuración")
    provincias = sorted(df_final['PROVINCIA'].unique())
    sel_provincia = st.selectbox("Seleccione Provincia", provincias)
    
    empresas = sorted(df_final[df_final['PROVINCIA'] == sel_provincia]['EMPRESA'].unique())
    sel_empresas = st.multiselect("Filtrar Empresas", empresas, default=empresas)

# Filtrado dinámico
mask = (df_final['PROVINCIA'] == sel_provincia) & (df_final['EMPRESA'].isin(sel_empresas))
df_filtrado = df_final[mask]

# --- BLOQUE DE INDICADORES (KPIs) ---
kpi1, kpi2, kpi3 = st.columns(3)
ultima_dot = df_filtrado[df_filtrado['Mes'] == df_filtrado['Mes'].iloc[-1]]['Dotación'].sum()
avg_rot = df_filtrado['Rotación %'].mean()

kpi1.metric("Dotación Total Actual", int(ultima_dot))
kpi2.metric("Promedio Rotación", f"{avg_rot:.2f}%")
kpi3.metric("Provincia Seleccionada", sel_provincia)

st.divider()

# --- GRÁFICOS ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("Evolución Mensual de Dotación")
    fig_dot = px.line(df_filtrado, x='Mes', y='Dotación', color='EMPRESA', 
                      markers=True, line_shape="spline", template="plotly_white")
    st.plotly_chart(fig_dot, use_container_width=True)

with col_graf2:
    st.subheader("Índice de Rotación por Empresa")
    fig_rot = px.bar(df_filtrado, x='Mes', y='Rotación %', color='EMPRESA', 
                     barmode='group', template="plotly_white", text_auto='.1f')
    st.plotly_chart(fig_rot, use_container_width=True)

# --- TABLA DE DATOS ---
with st.expander("Ver detalle de datos mensuales (Tabla)"):
    st.dataframe(df_filtrado.sort_values(by=['EMPRESA', 'Mes']), use_container_width=True)

st.info("💡 Consejo de analista: Compara el crecimiento de la dotación con los picos de rotación para identificar si las nuevas contrataciones se están reteniendo adecuadamente.")
