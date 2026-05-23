import streamlit as st
import pandas as pd
import plotly.express as px
import json
import urllib.request
import os
import glob
import numpy as np

# Configuración de página
st.set_page_config(page_title="Mortalidad en Colombia 2019", layout="wide", page_icon="🇨🇴")

st.title("Análisis de Mortalidad en Colombia 2019")
st.markdown("""
Esta aplicación permite explorar y visualizar los datos de mortalidad no fetal en Colombia correspondientes al año 2019, 
utilizando datos oficiales del DANE.
""")

@st.cache_data
def load_data():
    """Carga los datos desde los archivos de Excel de forma dinámica usando comodines en el nombre de archivo."""
    
    path_nofetal = glob.glob("datos/*NoFetal2019*.xlsx")
    path_codigos = glob.glob("datos/*CodigosDeMuerte*.xlsx")
    path_divipola = glob.glob("datos/*Divipola*.xlsx")
    
    if not (path_nofetal and path_codigos and path_divipola):
        st.error("⚠️ Faltan archivos en la carpeta 'datos/'. Asegúrate de incluir los tres archivos: NoFetal2019, CodigosDeMuerte y Divipola en formato Excel.")
        st.stop()
        
    try:
        # Carga del Excel principal
        df_nofetal = pd.read_excel(path_nofetal[0])
        # CodigosDeMuerte tiene un encabezado en la fila 8 (index 8 si empezamos a contar desde 0 con header=8)
        df_codigos = pd.read_excel(path_codigos[0], header=8)
        # Diccionario de la División Político-Administrativa
        df_divipola = pd.read_excel(path_divipola[0])
        
        return df_nofetal, df_codigos, df_divipola
    except Exception as e:
        st.error(f"Error crítico al leer los archivos de Excel: {e}")
        st.stop()

df_nofetal, df_codigos, df_divipola = load_data()

# ==========================================
# 1. PREPARACIÓN DE DATOS (ETL Básico)
# ==========================================

# Mapeo de Sexo
if 'SEXO' in df_nofetal.columns:
    df_nofetal['SEXO_NOM'] = df_nofetal['SEXO'].map({1: 'Hombre', 2: 'Mujer', 3: 'Indeterminado'})
else:
    df_nofetal['SEXO_NOM'] = 'Desconocido'

# Mapeo de Grupo de Edad según códigos DANE
def clasificar_edad(codigo):
    try:
        codigo = int(codigo)
        if 0 <= codigo <= 4: return "Mortalidad neonatal"
        elif 5 <= codigo <= 6: return "Mortalidad infantil"
        elif 7 <= codigo <= 8: return "Primera infancia"
        elif 9 <= codigo <= 10: return "Niñez"
        elif codigo == 11: return "Adolescencia"
        elif 12 <= codigo <= 13: return "Juventud"
        elif 14 <= codigo <= 16: return "Adultez temprana"
        elif 17 <= codigo <= 19: return "Adultez intermedia"
        elif 20 <= codigo <= 24: return "Vejez"
        elif 25 <= codigo <= 28: return "Longevidad / Centenarios"
        elif codigo == 29: return "Edad desconocida"
        else: return "Otro"
    except:
        return "Otro"

if 'GRUPO_EDAD1' in df_nofetal.columns:
    df_nofetal['CATEGORIA_EDAD'] = df_nofetal['GRUPO_EDAD1'].apply(clasificar_edad)

# Mapeo de Códigos de Causa de Muerte
# Columnas reales en el Excel (3 y 4 caracteres CIE-10)
col_codigo_3 = df_codigos.columns[2]
col_nombre_3 = df_codigos.columns[3]
col_codigo_4 = df_codigos.columns[4]
col_nombre_4 = df_codigos.columns[5]

# Creamos diccionarios y los unimos para abarcar ambos casos en los diagnósticos
mapa_causas_3 = dict(zip(df_codigos[col_codigo_3].astype(str), df_codigos[col_nombre_3]))
mapa_causas_4 = dict(zip(df_codigos[col_codigo_4].astype(str), df_codigos[col_nombre_4]))
mapa_causas = {**mapa_causas_3, **mapa_causas_4}

if 'COD_MUERTE' in df_nofetal.columns:
    df_nofetal['CAUSA_NOM'] = df_nofetal['COD_MUERTE'].astype(str).map(mapa_causas).fillna('Desconocido')

# Merge de Divipola para cruzar los IDs numéricos y obtener nombres de Departamento y Municipio
if 'COD_DEPARTAMENTO' in df_nofetal.columns and 'COD_MUNICIPIO' in df_nofetal.columns:
    df_nofetal = df_nofetal.merge(
        df_divipola[['COD_DEPARTAMENTO', 'COD_MUNICIPIO', 'DEPARTAMENTO', 'MUNICIPIO']].drop_duplicates(), 
        on=['COD_DEPARTAMENTO', 'COD_MUNICIPIO'], 
        how='left'
    )

# ==========================================
# 2. VISUALIZACIONES (DASHBOARD)
# ==========================================
st.header("Dashboard Interactivo de Mortalidad")

# --- Gráfico de líneas: Total de muertes por mes ---
st.subheader("1. Variación de muertes a lo largo del año")
if 'MES' in df_nofetal.columns:
    muertes_mes = df_nofetal.groupby('MES').size().reset_index(name='Total')
    meses_dict = {1:'Enero', 2:'Febrero', 3:'Marzo', 4:'Abril', 5:'Mayo', 6:'Junio', 
                  7:'Julio', 8:'Agosto', 9:'Septiembre', 10:'Octubre', 11:'Noviembre', 12:'Diciembre'}
    muertes_mes['Nombre Mes'] = muertes_mes['MES'].map(meses_dict)
    
    fig_mes = px.line(muertes_mes, x='Nombre Mes', y='Total', markers=True, 
                      labels={'Total': 'Total de Muertes', 'Nombre Mes': 'Mes del año'},
                      color_discrete_sequence=['#FF5733'])
    st.plotly_chart(fig_mes, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    # --- Mapa: Distribución total de muertes por departamento ---
    st.subheader("2. Distribución total de muertes por departamento")
    if 'COD_DEPARTAMENTO' in df_nofetal.columns:
        url_geojson = "https://gist.githubusercontent.com/john-guerra/43c7656821069d00dcbc/raw/be6a6e239cd5b5b803c6e7c2ec405b793a9064dd/Colombia.geo.json"
        try:
            with urllib.request.urlopen(url_geojson) as response:
                colombia_geojson = json.loads(response.read().decode())
                
            df_mapa = df_nofetal.groupby(['COD_DEPARTAMENTO', 'DEPARTAMENTO']).size().reset_index(name='Total')
            # El geojson requiere que el código sea de 2 dígitos como string
            df_mapa['COD_DEPARTAMENTO_STR'] = df_mapa['COD_DEPARTAMENTO'].astype(str).str.zfill(2)
            
            fig_mapa = px.choropleth_mapbox(
                df_mapa, geojson=colombia_geojson, locations='COD_DEPARTAMENTO_STR', featureidkey="properties.DPTO",
                color='Total', color_continuous_scale="Reds", hover_name="DEPARTAMENTO",
                mapbox_style="carto-positron", zoom=4, center={"lat": 4.5709, "lon": -74.2973},
                opacity=0.7
            )
            st.plotly_chart(fig_mapa, use_container_width=True)
        except Exception as e:
            st.error(f"No se pudo cargar el mapa. Verifica la conexión a internet. Detalles: {e}")

with col2:
    # --- Gráfico de barras apiladas: Total de muertes por sexo en cada departamento ---
    st.subheader("3. Muertes por sexo en cada departamento")
    if 'DEPARTAMENTO' in df_nofetal.columns and 'SEXO_NOM' in df_nofetal.columns:
        muertes_sexo_dpto = df_nofetal.groupby(['DEPARTAMENTO', 'SEXO_NOM']).size().reset_index(name='Total')
        fig_sexo = px.bar(muertes_sexo_dpto, x='DEPARTAMENTO', y='Total', color='SEXO_NOM', barmode='stack',
                          labels={'DEPARTAMENTO': 'Departamento', 'Total': 'Número de Muertes'})
        st.plotly_chart(fig_sexo, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    # --- Gráfico de barras: 5 ciudades más violentas (Homicidios) ---
    st.subheader("4. Top 5 Ciudades Más Violentas (Homicidios)")
    # Se aíslan los códigos X95 (agresión por arma) o Y09 (no especificada)
    if 'COD_MUERTE' in df_nofetal.columns:
        violentas = df_nofetal[df_nofetal['COD_MUERTE'].astype(str).str.contains('X95|Y09', na=False, case=False)]
        if 'MUNICIPIO' in violentas.columns:
            top_violentas = violentas.groupby('MUNICIPIO').size().reset_index(name='Total').sort_values('Total', ascending=False).head(5)
            fig_violentas = px.bar(top_violentas, x='MUNICIPIO', y='Total', color='Total',
                                   color_continuous_scale='Reds', text_auto=True,
                                   labels={'MUNICIPIO': 'Ciudad / Municipio', 'Total': 'Casos'})
            st.plotly_chart(fig_violentas, use_container_width=True)

with col4:
    # --- Gráfico circular: 10 ciudades con menor índice de mortalidad ---
    st.subheader("5. Top 10 Ciudades con Menor Mortalidad")
    if 'MUNICIPIO' in df_nofetal.columns:
        menor_mortalidad = df_nofetal.groupby('MUNICIPIO').size().reset_index(name='Total').sort_values('Total', ascending=True).head(10)
        fig_menor = px.pie(menor_mortalidad, names='MUNICIPIO', values='Total', hole=0.3,
                           color_discrete_sequence=px.colors.sequential.Teal)
        st.plotly_chart(fig_menor, use_container_width=True)

# --- Histograma o gráfico de distribución por grupo de edad ---
st.subheader("6. Distribución de muertes por grupo de edad")
if 'CATEGORIA_EDAD' in df_nofetal.columns:
    orden_edades = ["Mortalidad neonatal", "Mortalidad infantil", "Primera infancia", "Niñez", "Adolescencia", 
                    "Juventud", "Adultez temprana", "Adultez intermedia", "Vejez", "Longevidad / Centenarios", "Edad desconocida"]
    edades = df_nofetal['CATEGORIA_EDAD'].value_counts().reindex(orden_edades).reset_index()
    edades.columns = ['Grupo de Edad', 'Total']
    fig_edades = px.bar(edades, x='Grupo de Edad', y='Total', text_auto=True, color='Grupo de Edad',
                        color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_edades.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_edades, use_container_width=True)

# --- Tabla: Listado de las 10 principales causas de muerte ---
st.subheader("7. Top 10 Causas de Muerte en Colombia")
if 'COD_MUERTE' in df_nofetal.columns and 'CAUSA_NOM' in df_nofetal.columns:
    top_causas = df_nofetal.groupby(['COD_MUERTE', 'CAUSA_NOM']).size().reset_index(name='Total').sort_values('Total', ascending=False).head(10)
    top_causas.columns = ['Código CIE-10', 'Descripción de la Causa', 'Total de Casos']
    
    # Resetear índice para que la tabla sea más limpia en Streamlit
    top_causas.reset_index(drop=True, inplace=True)
    top_causas.index = top_causas.index + 1
    st.table(top_causas)

st.markdown("---")
st.markdown("**Desarrollado para:** Proyecto Final - Herramientas Computacionales para la Interpretación de Resultados")
