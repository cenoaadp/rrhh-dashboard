import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard RRHH CENOA", layout="wide")

# URL directa de exportación de tus pestañas
SHEET_ID = "1XnsUZUZGH9itPCDf6jPpOIqfMIbX5s8nEe9JkF6ccqU"
URL_DOTACION = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=DOTACIÓN"
URL_ROTACION = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=ROTACIÓN"

@st.cache_data
def get_data(url, valor_name):
    # Leer datos
    df = pd.read_csv(url)
    # Limpiar columnas vacías
    df = df.dropna(axis=1, how='all')
    # Identificar columnas de meses (las que no son Empresa ni Provincia)
    id_vars = ['EMPRESA', 'PROVINCIA']
    value_vars = [col for col in df.columns if col not in id_vars]
    
    # Transformar de horizontal a vertical
    df_melted = df.melt(id_vars=id_vars, value_vars=value_vars, 
                        var_name='Mes', value_name=valor_name)
    return df_melted

# Cargar bases
try:
    df_dot = get_data(URL_DOTACION, "Dotación")
    df_rot = get_data(URL_ROTACION, "Rotación %")
    
    # Unir ambas tablas
    df_final = pd.merge(df_dot, df_rot, on=['EMPRESA', 'PROVINCIA', 'Mes'])
except Exception as e:
    st.error(f"Error al conectar con Google Sheets: {e}")
    st.stop()

# --- INTERFAZ ---
st.title("📊 Control de Gestión RRHH - CENOA")

# Filtros
col_f1, col_f2 = st.columns(2)
with col_f1:
    empresas = df_final['EMPRESA'].unique()
    sel_empresa = st.multiselect("Filtrar por Empresa", empresas, default=empresas)
with col_f2:
    provincias = df_final['PROVINCIA'].unique()
    sel_provincia = st.selectbox("Filtrar por Provincia", provincias)

# Filtrado de datos
mask = (df_final['EMPRESA'].isin(sel_empresa)) & (df_final['PROVINCIA'] == sel_provincia)
df_filtrado = df_final[mask]

# --- VISUALIZACIONES ---
c1, c2 = st.columns(2)

with c1:
    st.subheader(f"Evolución de Dotación - {sel_provincia}")
    fig_dot = px.line(df_filtrado, x='Mes', y='Dotación', color='EMPRESA', 
                      markers=True, text='Dotación')
    fig_dot.update_traces(textposition="top center")
    st.plotly_chart(fig_dot, use_container_width=True)

with c2:
    st.subheader(f"Índice de Rotación - {sel_provincia}")
    fig_rot = px.bar(df_filtrado, x='Mes', y='Rotación %', color='EMPRESA', 
                     barmode='group', text_auto='.2f')
    st.plotly_chart(fig_rot, use_container_width=True)

# --- TABLA DE DETALLE ---
st.divider()
st.subheader("Datos Detallados")
st.dataframe(df_filtrado.style.highlight_max(axis=0, subset=['Rotación %'], color='#ffaaaa'), use_container_width=True)
