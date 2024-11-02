import streamlit as st
import plotly.express as px
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import pandas as pd
import ssl
from datetime import datetime, timedelta
import calendar
import geopandas as gpd
import pyproj
import json

ssl._create_default_https_context = ssl._create_unverified_context

st.set_page_config(
    page_title="Kaax Analytics",
    page_icon="../kaax_logo.png",
    layout="wide"
)

warnings.filterwarnings('ignore')

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


@st.cache_data
def download_coverage():
    url = "https://catalogo.senacyt.gob.gt:80/dataset/df68b1e1-18f9-4e9c-bfee-3f4ee342328d/resource/2545ac18-2a5a-4e22-9ad3-daa072569edc/download/cobertura-vegetal-y-uso-de-la-tierra_2020.csv"
    data_downloaded = pd.read_csv(url, encoding='ISO-8859-1', delimiter=';', on_bad_lines='skip')

    return data_downloaded


#@st.cache_resource
#def load_geojson():
    #gdf = gpd.read_file('/geoBoundaries-GTM-ADM1.geojson')
    #return gdf


#geojson = load_geojson()
#geojson.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)

with st.spinner('Cargando datos SENACYT...'):
    df_coverage = download_coverage()
    df_coverage.dropna(subset=['DEPARTAMENTO', 'Nivel_1'], inplace=True)

st.sidebar.header("Filtros:")
departamento = st.sidebar.multiselect("Seleccione el Departamento:", options=df_coverage['DEPARTAMENTO'].unique())
nivel_uso = st.sidebar.multiselect("Seleccione el Nivel de Uso de la Tierra:", options=df_coverage['Nivel_1'].unique())

if departamento:
    df_coverage = df_coverage[df_coverage['DEPARTAMENTO'].isin(departamento)]
if nivel_uso:
    df_coverage = df_coverage[df_coverage['Nivel_1'].isin(nivel_uso)]

st.sidebar.divider()
st.sidebar.title("Kaax Analytics")
st.sidebar.markdown(
    'Fuente: [SENACYT](https://catalogo.senacyt.gob.gt:80/en_GB/dataset/cobertura-vegetal-y-uso-de-la-tierra/resource/2545ac18-2a5a-4e22-9ad3-daa072569edc?inner_span=True)')

st.title("Cobertura vegetal y uso de tierra")

hectareas_por_nivel = df_coverage.groupby('Nivel_1')['SUPERFICIE (hectáreas)'].sum()
total_hectareas = hectareas_por_nivel.sum()

porcentaje_por_nivel = df_coverage.groupby('Nivel_1')['PORCENTAJE NACIONAL (%)'].sum()

col1, col2, col3 = st.columns(3)
with col1:
    try:
        pct = porcentaje_por_nivel['2. Territorios agrícolas']
        st.metric("Territorios agrícolas", f"{hectareas_por_nivel['2. Territorios agrícolas']:,.0f} ha", f"{pct:.2f}% del total")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
with col2:
    try:
        pct = porcentaje_por_nivel['3. Bosques y medios seminaturales']
        st.metric("Bosques y medios seminaturales",
                  f"{hectareas_por_nivel['3. Bosques y medios seminaturales']:,.0f} ha", f"{pct:.2f}% del total")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
with col3:
    try:
        pct = porcentaje_por_nivel['1. Territorios artificializados']
        st.metric("Territorios artificializados", f"{hectareas_por_nivel['1. Territorios artificializados']:,.0f} ha",
                  f"{pct:.2f}% del total")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

col4, col5, col6 = st.columns(3)
with col4:
    try:
        pct = porcentaje_por_nivel['5. Cuerpos de agua']
        st.metric("Cuerpos de agua", f"{hectareas_por_nivel['5. Cuerpos de agua']:,.0f} ha", f"{pct:.2f}% del total")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
with col5:
    try:
        pct = porcentaje_por_nivel['4. Zonas húmedas']
        st.metric("Zonas húmedas", f"{hectareas_por_nivel['4. Zonas húmedas']:,.0f} ha", f"{pct:.2f}% del total")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


st.dataframe(df_coverage)

superficie = df_coverage.groupby(['DEPARTAMENTO', 'USO DE LA TIERRA'])['SUPERFICIE (hectáreas)'].sum().reset_index()

df_plot = df_coverage.groupby(['DEPARTAMENTO', 'Nivel_1'])['SUPERFICIE (hectáreas)'].sum().unstack(fill_value=0)

fig = px.bar(
    df_plot,
    x=df_plot.index,
    y=df_plot.columns,
    labels={"value": "Área (hectáreas)", "variable": "Nivel de Uso del Suelo"},
    title="Área por Departamento y Nivel de Uso del Suelo"
)

fig.update_layout(
    xaxis_title="Departamento y Nivel de Uso de la Tierra",
    yaxis_title="Área (hectáreas)",
    barmode='stack'
)

st.plotly_chart(fig, use_container_width=True)

st.info("Este gráfico muestra cómo se distribuye la superficie según los diferentes niveles de uso de la tierra en cada departamento seleccionado.")

#df_coverage['DEPARTAMENTO'] = df_coverage['DEPARTAMENTO'].str.strip()
#geojson['shapeName'] = geojson['shapeName'].str.strip()

#df_filtered = df_coverage[df_coverage['Nivel_1'] == '2. Territorios agrícolas']
#superficie_por_departamento = df_coverage.groupby('DEPARTAMENTO')['SUPERFICIE (hectáreas)'].sum().reset_index()

#merged_data = geojson.merge(superficie_por_departamento, left_on='shapeName', right_on='DEPARTAMENTO')

#geojson_json = json.loads(geojson.to_json())

#fig = px.choropleth(
#    merged_data,
#    geojson=geojson_json,
#    locations='shapeName',
#    color='SUPERFICIE (hectáreas)',
#    hover_name='DEPARTAMENTO',
#    color_continuous_scale=px.colors.sequential.Plasma
#)

#fig.update_geos(fitbounds="locations", visible=False)
#fig.update_layout(margin={"r":0, "t":0, "l":0, "b":0})

#st.plotly_chart(fig, use_container_width=True)

st.subheader("Porcentaje nacional por tipo de uso de la tierra")
df_percentage = df_coverage.groupby('Nivel_1')['PORCENTAJE NACIONAL (%)'].sum().reset_index()
fig2 = px.pie(df_percentage, values='PORCENTAJE NACIONAL (%)', names='Nivel_1',
             title="Distribución porcentual del uso de tierra a nivel nacional")
st.plotly_chart(fig2, use_container_width=True)
st.info("Esta gráfica de pastel muestra el porcentaje medio nacional de cada tipo de uso de la tierra, ayudando a entender la importancia relativa de cada uso en el contexto nacional.")

df_coverage.dropna(subset=['Nivel_4'], inplace=True)

nivel_4 = st.multiselect("Seleccione el filtro:", options=df_coverage['Nivel_4'].unique())

if nivel_4:
    df_filtered = df_coverage[df_coverage['Nivel_4'].isin(nivel_4)]
else:
    df_filtered = df_coverage

st.dataframe(df_filtered)

superficie_por_departamento = df_filtered.groupby(['DEPARTAMENTO', 'Nivel_4'])['SUPERFICIE (hectáreas)'].sum().reset_index()

fig = px.bar(
    superficie_por_departamento,
    x='DEPARTAMENTO',
    y='SUPERFICIE (hectáreas)',
    color='Nivel_4',
    title="Superficie por Departamento y Nivel 4",
    labels={"SUPERFICIE (hectáreas)": "Superficie (hectáreas)", "DEPARTAMENTO": "Departamento"},
    barmode='group'
)

st.plotly_chart(fig, use_container_width=True)

st.info(f"Esta gráfica muestra la distribución de la superficie por departamento, segmentada por los tipos de uso definidos en Nivel 4: {nivel_4}. Permite identificar cómo se utilizan las tierras en cada departamento bajo los criterios seleccionados.")

nivel_3 = st.multiselect("Seleccione el filtro:", options=df_coverage['Nivel_3'].unique())

if nivel_3:
    df_filtered_n3 = df_coverage[df_coverage['Nivel_3'].isin(nivel_3)]
else:
    df_filtered_n3 = df_coverage

st.dataframe(df_filtered_n3)

superficie_por_departamento = df_filtered_n3.groupby(['DEPARTAMENTO', 'Nivel_3'])['SUPERFICIE (hectáreas)'].sum().reset_index()

fig = px.bar(
    superficie_por_departamento,
    x='DEPARTAMENTO',
    y='SUPERFICIE (hectáreas)',
    color='Nivel_3',
    title="Superficie por Departamento y Nivel 3",
    labels={"SUPERFICIE (hectáreas)": "Superficie (hectáreas)", "DEPARTAMENTO": "Departamento"},
    barmode='group'
)

st.plotly_chart(fig, use_container_width=True)

st.info(f"Esta gráfica muestra la distribución de la superficie por departamento, segmentada por los tipos de uso definidos en Nivel 3: {nivel_3}. Permite identificar cómo se utilizan las tierras en cada departamento bajo los criterios seleccionados.")

nivel_2 = st.multiselect("Seleccione el filtro:", options=df_coverage['Nivel_2'].unique())

if nivel_2:
    df_filtered_n2 = df_coverage[df_coverage['Nivel_2'].isin(nivel_2)]
else:
    df_filtered_n2 = df_coverage

st.dataframe(df_filtered_n2)

superficie_por_departamento = df_filtered_n2.groupby(['DEPARTAMENTO', 'Nivel_2'])['SUPERFICIE (hectáreas)'].sum().reset_index()

fig = px.bar(
    superficie_por_departamento,
    x='DEPARTAMENTO',
    y='SUPERFICIE (hectáreas)',
    color='Nivel_2',
    title="Superficie por Departamento y Nivel 2",
    labels={"SUPERFICIE (hectáreas)": "Superficie (hectáreas)", "DEPARTAMENTO": "Departamento"},
    barmode='group'
)

st.plotly_chart(fig, use_container_width=True)

st.info(f"Esta gráfica muestra la distribución de la superficie por departamento, segmentada por los tipos de uso definidos en Nivel 2: {nivel_2}. Permite identificar cómo se utilizan las tierras en cada departamento bajo los criterios seleccionados.")

uso_de_tierra = st.multiselect("Seleccione el filtro:", options=df_coverage['USO DE LA TIERRA'].unique())

if uso_de_tierra:
    df_filtered_uso = df_coverage[df_coverage['USO DE LA TIERRA'].isin(uso_de_tierra)]
else:
    df_filtered_uso = df_coverage

st.dataframe(df_filtered_uso)

superficie_por_departamento = df_filtered_uso.groupby(['DEPARTAMENTO', 'USO DE LA TIERRA', 'PORCENTAJE NACIONAL (%)'])['SUPERFICIE (hectáreas)'].sum().reset_index()

fig = px.bar(
    superficie_por_departamento,
    x='DEPARTAMENTO',
    y='SUPERFICIE (hectáreas)',
    color='USO DE LA TIERRA',
    title="Superficie por Departamento y uso de la tierra",
    labels={"SUPERFICIE (hectáreas)": "Superficie (hectáreas)", "DEPARTAMENTO": "Departamento"},
    barmode='group'
)

st.plotly_chart(fig, use_container_width=True)

total_de_hectareas_por_uso_de_tierra = superficie_por_departamento['SUPERFICIE (hectáreas)'].sum()
total_de_porcentage_por_uso_de_tierra = (superficie_por_departamento['PORCENTAJE NACIONAL (%)'].sum() / porcentaje_por_nivel['2. Territorios agrícolas']) * 100

st.info(f"Esta gráfica muestra la distribución de la superficie por departamento, segmentada por los tipos de uso definidos en  uso de tierra: {','.join(uso_de_tierra)}, con un total de " + f"{total_de_hectareas_por_uso_de_tierra:.0f} hectareas" + " y un porcentaje del " + f"{total_de_porcentage_por_uso_de_tierra:.2f}% del territorio agricola" + ". Permite identificar cómo se utilizan las tierras en cada departamento bajo los criterios seleccionados.")
