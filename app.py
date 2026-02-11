import streamlit as st
import pandas as pd
import plotly.express as px
import io
import requests

st.set_page_config(page_title="Dashboard RRHH CENOA", layout="wide")

SHEET_ID = "1XnsUZUZGH9itPCDf6jPpOIqfMIbX5s8nEe9JkF6ccqU"

@st.cache_data
def get_data(sheet_name, valor_name):
    # Construimos la URL
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    
    # Descargamos el contenido con requests para asegurar UTF-8
    response = requests.get(url)
    response.encoding = 'utf-8' # Forzamos la codificación correcta
    
    # Leemos el CSV desde el texto de la respuesta
    df = pd.read_csv(io.StringIO(response.text))
    
    # Limpieza: quitamos columnas vacías y normalizamos nombres de columnas
    df = df.dropna(axis=1, how='all')
    df.columns = [c.strip().upper() for c in df.columns]
    
    # Identificar columnas fijas (sin tildes para evitar errores de mapeo)
    # Buscamos las columnas que NO son meses
    id_vars = [col for col in df.columns if 'EMPRESA' in col or 'PROVINCIA' in col]
    value_vars = [col for col in df.columns if col not in id_vars]
    
    # Transformar de formato ancho a largo
    df_melted = df.melt(id_vars=id_vars, value_vars=value_vars, 
                        var_name='Mes', value_name=valor_name)
    
    # Aseguramos que la columna Mes sea tratada como texto
    df_melted['Mes'] = df_melted['Mes'].astype(str)
    
    return df_melted

# Intentar cargar las pestañas usando el nombre exacto o codificado
try:
    # Usamos los nombres de las pestañas tal cual están en tu Excel
    df_dot = get_data("DOTACIÓN", "Dotación")
    df_rot = get_data("ROTACIÓN", "Rotación %")
    
    # Estandarizamos los nombres de las columnas clave para el merge
    df_dot.columns = ['EMPRESA', 'PROVINCIA', 'Mes', 'Dotación']
    df_rot.columns = ['EMPRESA', 'PROVINCIA', 'Mes', 'Rotación %']
    
    df_final = pd.merge(df_dot, df_rot, on=['EMPRESA', 'PROVINCIA', 'Mes'])
    
    st.success("✅ Datos cargados correctamente")
except Exception as e:
    st.error(f"Error detallado: {e}")
    st.stop()

# --- De aquí en adelante sigue igual que el código anterior ---
# (Filtros, gráficos y tablas...)
