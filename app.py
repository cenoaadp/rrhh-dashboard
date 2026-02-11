import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard RRHH - CENOA", layout="wide")

st.title("📊 Dashboard de Gestión de Talento - CENOA")
st.markdown("Análisis de Dotación y Rotación 2025 - 2026")

# URL de tu Sheet (formato export para pandas)
sheet_id = "1XnsUZUZGH9itPCDf6jPpOIqfMIbX5s8nEe9JkF6ccqU"
# Nota: Se asume que los datos están limpios en el CSV. 
# Para este ejemplo, usaremos una estructura simplificada basada en tu archivo.

@st.cache_data
def load_data():
    # En una app real, aquí conectarías con st.connection o cargarías el CSV
    # Por ahora, simulamos la carga de la estructura que vi en tu archivo
    url_dotacion = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=DOTACIÓN"
    url_rotacion = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=ROTACIÓN"
    
    # Aquí deberías cargar y limpiar tus datos según las pestañas
    # df_dot = pd.read_csv(url_dotacion)
    # df_rot = pd.read_csv(url_rotacion)
    return url_dotacion, url_rotacion

# --- SIDEBAR: FILTROS ---
st.sidebar.header("Filtros de Análisis")
empresa = st.sidebar.multiselect("Seleccionar Empresa", ["Autolux", "Autosol", "Ciel", "La Luz", "CENOA"], default="CENOA")
provincia = st.sidebar.selectbox("Seleccionar Provincia/Región", ["Cenoa", "Jujuy", "Salta"])

# --- CUERPO PRINCIPAL ---
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"📈 Evolución de Dotación en {provincia}")
    # Aquí iría el gráfico de líneas (px.line) con los meses en el eje X
    st.info("Gráfico de tendencia de dotación mensual")

with col2:
    st.subheader(f"🔄 Índice de Rotación Mensual (%)")
    # Aquí iría el gráfico de barras (px.bar)
    st.warning("Gráfico de barras con picos de rotación")

st.divider()

# --- DETALLE TABULAR ---
st.subheader("📋 Detalle de Datos Mensuales")
st.write("Selecciona los filtros para ver el desglose detallado mes a mes.")
# st.dataframe(df_filtrado)

st.success("💡 Tip de Experto: El pico de rotación en Salta (Dic-25) sugiere revisar los procesos de salida o clima laboral en ese período.")
