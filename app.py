import streamlit as st
import pandas as pd
import plotly.express as px
import io
import requests

st.set_page_config(page_title="Dashboard RRHH CENOA", layout="wide")

SHEET_ID = "1XnsUZUZGH9itPCDf6jPpOIqfMIbX5s8nEe9JkF6ccqU"

@st.cache_data
def get_data(sheet_name, valor_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    response = requests.get(url)
    response.encoding = 'utf-8'
    
    df = pd.read_csv(io.StringIO(response.text))
    df = df.dropna(axis=1, how='all')
    df.columns = [c.strip().upper() for c in df.columns]
    
    id_vars = [col for col in df.columns if 'EMPRESA' in col or 'PROVINCIA' in col]
    value_vars = [col for col in df.columns if col not in id_vars]
    
    df_melted = df.melt(id_vars=id_vars, value_vars=value_vars, 
                        var_name='Mes', value_name=valor_name)
    
    # --- LIMPIEZA DE NÚMEROS (Para evitar el TypeError) ---
    if df_melted[valor_name].dtype == 'object':
        # Quitamos el símbolo % si existe, cambiamos coma por punto y convertimos a numérico
        df_melted[valor_name] = (
            df_melted[valor_name]
            .astype(str)
            .str.replace('%', '', regex=False)
            .str.replace(',', '.', regex=False)
            .str.strip()
        )
        df_melted[valor_name] = pd.to_numeric(df_melted[valor_name], errors='coerce').fillna(0)
    
    return df_melted

# --- CARGA Y MERGE ---
try:
    df_dot = get_data("DOTACIÓN", "Dotación")
    df_rot = get_data("ROTACIÓN", "Rotación %")
    
    # Asegurar nombres de columnas para el merge
    df_dot.columns = ['EMPRESA', 'PROVINCIA', 'Mes', 'Dotación']
    df_rot.columns = ['EMPRESA', 'PROVINCIA', 'Mes', 'Rotación %']
    
    df_final = pd.merge(df_dot, df_rot, on=['EMPRESA', 'PROVINCIA', 'Mes'])
except Exception as e:
    st.error(f"Error al procesar los datos: {e}")
    st.stop()

# --- EL RESTO DEL CÓDIGO (KPIs y Gráficos) ---
st.title("📊 Control de Gestión RRHH - CENOA")

with st.sidebar:
    st.header("Configuración")
    provincias = sorted(df_final['PROVINCIA'].unique())
    sel_provincia = st.selectbox("Seleccione Provincia", provincias)
    empresas = sorted(df_final[df_final['PROVINCIA'] == sel_provincia]['EMPRESA'].unique())
    sel_empresas = st.multiselect("Filtrar Empresas", empresas, default=empresas)

mask = (df_final['PROVINCIA'] == sel_provincia) & (df_final['EMPRESA'].isin(sel_empresas))
df_filtrado = df_final[mask]

# KPIs con manejo de errores por si no hay datos seleccionados
if not df_filtrado.empty:
    kpi1, kpi2, kpi3 = st.columns(3)
    # Tomamos el último mes disponible
    meses_disponibles = df_filtrado['Mes'].unique()
    ultimo_mes = meses_disponibles[-1]
    
    dot_actual = df_filtrado[df_filtrado['Mes'] == ultimo_mes]['Dotación'].sum()
    rot_promedio = df_filtrado['Rotación %'].mean()

    kpi1.metric("Dotación Total Actual", f"{int(dot_actual)}")
    kpi2.metric("Promedio Rotación Histórica", f"{rot_promedio:.2f}%")
    kpi3.metric("Provincia", sel_provincia)

    # Gráficos
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Evolución de Dotación")
        fig1 = px.line(df_filtrado, x='Mes', y='Dotación', color='EMPRESA', markers=True)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("Índice de Rotación")
        fig2 = px.bar(df_filtrado, x='Mes', y='Rotación %', color='EMPRESA', barmode='group')
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("No hay datos para la selección actual.")
