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
import openai
from openai import OpenAI
from dotenv import load_dotenv
import os
import httpx
import asyncio

dotenv_path = os.path.join('/config/config.env')
load_dotenv(dotenv_path)

#OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

#if not OPENAI_API_KEY:
    #raise ValueError("No se encontró OPENAI_API_KEY. Asegúrate de que esté en tu archivo .env.")

#openai.api_key = OPENAI_API_KEY
#client = OpenAI()

st.set_page_config(
    page_title="Kaax Analytics",
    page_icon="../kaax_logo.png",
    layout="wide"
)

warnings.filterwarnings('ignore')


# Configuration and download data
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


@st.cache_data
def download_data():
    ssl._create_default_https_context = ssl._create_unverified_context
    
    csv_urls = []
    df_list = []

    url = 'https://catalogo.senacyt.gob.gt:80/en_GB/dataset/precios-al-mayorista-de-productos-agropecuarios-e-hidrobiologicos/resource/5554f0d7-1049-4020-9475-75d61b6956c7?inner_span=True'

    try:
        response = requests.get(url, verify=False, timeout=10)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            aside = soup.find('aside', class_='secondary col-md-3')
            nav_list = aside.find('ul', class_='list-unstyled nav nav-simple')
            nav_items = nav_list.find_all('li', class_='nav-item')

            for nav_item in nav_items:
                a_tag = nav_item.find('a')
                if a_tag and a_tag.has_attr('href'):
                    temp_url = "https://catalogo.senacyt.gob.gt:80" + a_tag['href']
                    try:
                        temp_response = requests.get(temp_url, verify=False, timeout=10)
                        if temp_response.status_code == 200:
                            temp_soup = BeautifulSoup(temp_response.text, 'html.parser')
                            a = temp_soup.find('a', class_='resource-url-analytics')
                            if a and a.has_attr('href') and ".csv" in a['href']:
                                csv_urls.append(a['href'])
                    except RequestException as e:
                        print(f"Error al procesar la URL {temp_url}: {e}")
    except RequestException as e:
        print(f"Error al obtener la página: {e}")

    for url in csv_urls:
        try:
            df = pd.read_csv(url, encoding='ISO-8859-1', on_bad_lines='skip')
            if len(df.columns) < 7:
                df = pd.read_csv(url, encoding='ISO-8859-1', delimiter=';', on_bad_lines='skip')
            df.columns = df.columns.str.replace('ï»¿', '').str.strip()
            df.columns = df.columns.str.replace('Periodicidad', 'Peridiocidad').str.strip()
            df.columns = df.columns.str.replace('Perodiocidad', 'Peridiocidad').str.strip()
            df.columns = df.columns.str.replace('Mes', 'Fecha').str.strip()
            df.columns = df.columns.str.replace('Año', 'Fecha').str.strip()
            df.columns = df.columns.str.replace('Mondeda', 'Moneda').str.strip()

            if len(df.columns) == 8:
                df_list.append(df)
        except pd.errors.ParserError:
            df = pd.read_csv(url, encoding='ISO-8859-1', delimiter=';', on_bad_lines='skip')
            df.columns = df.columns.str.replace('ï»¿', '').str.strip()
            df.columns = df.columns.str.replace('Periodicidad', 'Peridiocidad').str.strip()
            df.columns = df.columns.str.replace('Perodiocidad', 'Peridiocidad').str.strip()
            df.columns = df.columns.str.replace('Mes', 'Fecha').str.strip()
            df.columns = df.columns.str.replace('Año', 'Fecha').str.strip()
            df.columns = df.columns.str.replace('Mondeda', 'Moneda').str.strip()

            if len(df.columns) == 8:
                df_list.append(df)

    df_list = [df.reset_index(drop=True) for df in df_list]

    expected_columns = {'Actor', 'Peridiocidad', 'Mercado', 'Producto', 'Medida', 'Fecha', 'Moneda', 'Precio'}

    for i in range(len(df_list) - 1, -1, -1):
        if set(df_list[i].columns) != expected_columns:
            print(f"Inconsistencia encontrada en DataFrame {i}:")
            print(f"Columnas esperadas: {expected_columns}")
            print(f"Columnas actuales: {set(df_list[i].columns)}")
            del df_list[i]

    normalized_data = []

    try:
        normalized_data = pd.concat(df_list, ignore_index=True)
    except Exception as e:
        print(f"Ocurrió un error al concatenar los DataFrames: {e}")

    return normalized_data


with st.spinner('Cargando datos SENACYT...'):
    combined_df = download_data()


st.title('Análisis de ventas en productos agropecuarios')

st.write("""
En esta sección de Kaax Analytics, ofrecemos un desglose detallado de las ventas de productos agropecuarios a lo largo de los últimos años. Nuestro objetivo es proporcionar a agricultores, investigadores y profesionales 
del sector agrícola, herramientas y análisis que les permitan comprender mejor las tendencias del mercado y tomar decisiones informadas.
""")

st.header("Visualización de Datos")

combined_df['Fecha'] = pd.to_datetime(combined_df['Fecha'], errors='coerce')

current_date = datetime.now()
date_12_months_ago = current_date - timedelta(days=365)

last_12_months_df = combined_df[(combined_df['Fecha'] >= date_12_months_ago) & (combined_df['Fecha'] <= current_date)]

market_sales = last_12_months_df.groupby('Mercado')['Precio'].sum().sort_values(ascending=False)

col1, col2 = st.columns((2))

with col1:
    fig_bar = px.bar(x=market_sales.index, y=market_sales.values, labels={'x': 'Mercado', 'y': 'Total de Ventas'},
                     title='Total de Ventas por Mercado (Últimos 12 Meses)')
    fig_bar.update_traces(marker_color='#FCC165')
    st.plotly_chart(fig_bar, use_container_width=True)
with col2:
    fig_pie = px.pie(values=market_sales.values, names=market_sales.index,
                     title='Distribución de las Ventas por Mercado')
    fig_pie.update_traces(marker=dict(colors=['#FCC165', '#06977C', '#434B64', '#FF4500', '#FF6347']))
    st.plotly_chart(fig_pie, use_container_width=True)

st.subheader("Selección de Fecha y Filtros")
st.write("Para una exploración más dirigida, puedes seleccionar rangos de fechas específicos y aplicar filtros por mercado, producto y unidad de medida. Esto te permite personalizar los análisis para concentrarte en la información más relevante para tus necesidades.")

with col1:
    start_date = st.date_input("Fecha de inicio", value=pd.to_datetime(combined_df["Fecha"]).min().date())
with col2:
    end_date = st.date_input("Fecha final", value=pd.to_datetime(combined_df["Fecha"]).max().date())

combined_df = combined_df[
    (combined_df["Fecha"] >= pd.to_datetime(start_date)) & (combined_df["Fecha"] <= pd.to_datetime(end_date))]

st.sidebar.header("Filtros:")
st.sidebar.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

market = st.sidebar.multiselect("Filtra por mercado:", options=combined_df["Mercado"].unique())
product = st.sidebar.multiselect("Filtra por producto:", options=combined_df["Producto"].unique())
measure = st.sidebar.multiselect("Filtra por unidad de medida:", options=combined_df["Medida"].unique())

st.sidebar.divider()
st.sidebar.title("Kaax Analytics")
st.sidebar.markdown(
    'Fuente: [SENACYT](https://catalogo.senacyt.gob.gt:80/en_GB/dataset/precios-al-mayorista-de-productos-agropecuarios-e-hidrobiologicos)')

if market:
    combined_df = combined_df[combined_df["Mercado"].isin(market)]
if product:
    combined_df = combined_df[combined_df["Producto"].isin(product)]
if measure:
    combined_df = combined_df[combined_df["Medida"].isin(measure)]

st.dataframe(combined_df)

st.title('Precio de venta')

combined_df['Fecha'] = pd.to_datetime(combined_df['Fecha'])

available_years = combined_df['Fecha'].dt.year.dropna().unique()
available_years = sorted(available_years.astype(int), reverse=True)
selected_year = st.selectbox("Seleccione un Año", options=available_years)

filtered_data = combined_df[combined_df['Fecha'].dt.year == selected_year]
selected_product = st.selectbox("Seleccione un Producto", options=filtered_data["Producto"].unique())

product_data = filtered_data[filtered_data['Producto'] == selected_product]

product_data = product_data.dropna(subset=['Medida'])
available_measures = product_data['Medida'].unique()
selected_measure = st.selectbox("Seleccione una Unidad de Medida", options=available_measures)

product_data = product_data[product_data['Medida'] == selected_measure]

product_data['Precio'] = pd.to_numeric(product_data['Precio'], errors='coerce')

if not product_data.empty:
    average_price = product_data['Precio'].mean(skipna=True)
    if pd.notna(average_price):
        st.write(f"Precio Promedio: {average_price:.2f} GTQ")
        st.write(f"Unidad de Medida: {selected_measure}")

        monthly_sales = product_data.groupby(product_data['Fecha'].dt.month)['Precio'].sum().reset_index()
        monthly_sales['Fecha'] = monthly_sales['Fecha'].apply(lambda x: calendar.month_name[x])
        fig = px.line(monthly_sales, x='Fecha', y='Precio', labels={'Precio': 'Ventas Totales'},
                      title=f'Ventas Mensuales de {selected_product} en {selected_year}')
        fig.update_traces(line_color='#06977C')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No hay suficientes datos numéricos para calcular el precio promedio.")
else:
    st.write("No hay datos disponibles para el producto, año y unidad de medida seleccionados.")


def forecast_sales_sarima(product_data, selected_product, selected_measure):
    filtered_data = product_data[
        (product_data['Producto'] == selected_product) &
        (product_data['Medida'] == selected_measure)
    ]

    filtered_data['Fecha'] = pd.to_datetime(filtered_data['Fecha'], errors='coerce')
    filtered_data.dropna(subset=['Fecha', 'Precio'], inplace=True)  # Eliminar filas con NaN en 'Fecha' y 'Precio'
    filtered_data['Precio'] = pd.to_numeric(filtered_data['Precio'], errors='coerce')  # Asegurar que 'Precio' es numérico
    filtered_data['Mes'] = filtered_data['Fecha'].dt.to_period('M')

    if filtered_data.empty:
        return None

    try:
        monthly_sales = filtered_data.groupby('Mes')['Precio'].sum()
        monthly_sales.index = monthly_sales.index.to_timestamp()

        model = SARIMAX(monthly_sales, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
        model_fit = model.fit(disp=False)

        forecast = model_fit.get_forecast(steps=12)
        forecast_index = pd.date_range(monthly_sales.index[-1], periods=13, freq='M')[1:]
        forecast_df = pd.DataFrame({'Fecha': forecast_index, 'Predicción': forecast.predicted_mean})

        st.line_chart(forecast_df.set_index('Fecha'))

        return forecast_df
    except Exception as e:
        st.error(f"Error al realizar la predicción: {str(e)}")
        return None


st.subheader("Análisis de Ventas y Predicciones Futuras")
st.write("""
Utilizamos modelos avanzados de series temporales para ofrecer predicciones sobre las tendencias de ventas en los próximos meses. 
Estas predicciones están diseñadas para ayudarte a planificar mejor, considerando posibles aumentos o disminuciones en la demanda.

Basadas en nuestras predicciones, proporcionamos recomendaciones sobre cuándo podría ser ideal incrementar o reducir la producción. 
Estas sugerencias están diseñadas para ayudar a evitar el exceso de inventario y maximizar la rentabilidad.

Cada análisis y visualización en Kaax Analytics está pensado para ser no solo informativo sino también intuitivo y fácil de utilizar, 
asegurando que incluso usuarios sin un profundo conocimiento técnico puedan beneficiarse de nuestros insights.
""")

selected_product_2 = st.selectbox(
    "Seleccione un Producto",
    options=combined_df["Producto"].unique(),
    key="select_product_2"
)

filtered_measures = combined_df[combined_df['Producto'] == selected_product_2]['Medida'].unique()

selected_measure_2 = st.selectbox(
    "Seleccione una Unidad de Medida",
    options=filtered_measures,
    key="select_measure_2"
)

forecast_df = None

if st.button('Predecir ventas futuras'):
    forecast_df = forecast_sales_sarima(combined_df, selected_product_2, selected_measure_2)


def interpret_predictions(forecast_df):
    forecast_df['Fecha'] = pd.to_datetime(forecast_df['Fecha'])

    peak_months = forecast_df.sort_values(by='Predicción', ascending=False).head(3)
    low_months = forecast_df.sort_values(by='Predicción').head(3)

    peak_months['Mes'] = peak_months['Fecha'].dt.strftime('%B')
    low_months['Mes'] = low_months['Fecha'].dt.strftime('%B')

    if not peak_months.empty and not low_months.empty:
        st.success(
            f"**Meses de alta demanda (incrementar producción):** {', '.join(peak_months['Mes'])}"
        )
        st.error(
            f"**Meses de baja demanda (considerar reducir producción):** {', '.join(low_months['Mes'])}"
        )
    else:
        st.error("No hay suficientes datos para mostrar predicciones de demanda.")


if not product_data.empty:
    forecast_df = forecast_sales_sarima(product_data, selected_product_2, selected_measure_2)
if forecast_df is not None and not forecast_df.empty:
    interpret_predictions(forecast_df)
else:
    st.warning("No se generaron predicciones válidas o no hay datos disponibles.")


@st.cache_resource
async def get_response(question, chat_history):
    key_terms = ["cultivos", "agricultura", "plantaciones", "fertilizantes", "maíz", "café", "uva", "tierras", "clima"]

    if any(term in question.lower() for term in key_terms):
        try:
            response_custom = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant focused on Guatemalan agriculture."},
                    {"role": "user", "content": chat_history},
                    {"role": "user", "content": question}
                ]
            )
            return response_custom.choices[0].message.content if response_custom.choices else "No response found."
        except Exception as e:
            return f"An error occurred: {str(e)}"
    else:
        return "Lo siento, solo puedo responder preguntas relacionadas con la agricultura guatemalteca."


@st.cache_resource
async def get_humanized_response(raw_response):
    try:
        response_humanized = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un bot y tu unica misión es transformar el ultimo texto que te enviara el user, en una respuesta clara y humanizada para un chatbot"},
                {"role": "user", "content": raw_response}
            ]
        )
        return response_humanized.choices[0].message.content if response_humanized.choices else "No response found."
    except Exception as e:
        return f"An error occurred: {str(e)}"


def run_async_code(question, chat_history):
    if "precio promedio del" in question:
        combined_df['Precio'] = pd.to_numeric(combined_df['Precio'], errors='coerce')
        all_parameters = question.split("precio promedio del ")[1].strip()
        medida_kaax_chat = all_parameters.split("/")[0].strip()
        producto_kaax_chat = all_parameters.split("/")[1].strip()
        producto_kaax_chat = producto_kaax_chat.replace("?", "")
        filter_medida = combined_df[combined_df['Producto'] == producto_kaax_chat]
        mean_price = filter_medida[combined_df['Medida'] == medida_kaax_chat]['Precio'].mean()
        if pd.isna(mean_price):
            return "No tengo información sobre ese producto."
        else:
            raw_response = f"El precio promedio del {producto_kaax_chat} es {mean_price:.2f} GTQ en la medida {medida_kaax_chat}."
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(get_humanized_response(raw_response))
            loop.close()
            return result
    elif "Mostrar precios en el mercado" in question:
        mercado = question.split("Mostrar precios en el mercado ")[1].strip()
        precios = combined_df[combined_df['Mercado'] == mercado][['Producto', 'Precio']].drop_duplicates().to_string(
            index=False)
        raw_response = f"Los precios en el mercado {mercado} son:\n{precios}"
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(get_humanized_response(raw_response))
        loop.close()
        return result
    elif "Comparar precios entre" in question:
        fechas = question.split("Comparar precios entre ")[1].split(" y ")
        fecha1, fecha2 = pd.to_datetime(fechas[0].strip()), pd.to_datetime(fechas[1].strip())
        precios = combined_df[(combined_df['Fecha'] >= fecha1) & (combined_df['Fecha'] <= fecha2)][
            ['Producto', 'Precio']].drop_duplicates().to_string(index=False)
        raw_response = f"Precios entre {fecha1.strftime('%Y-%m-%d')} y {fecha2.strftime('%Y-%m-%d')}:\n{precios}"
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(get_humanized_response(raw_response))
        loop.close()
        return result
    elif "¿Dónde está disponible el" in question:
        producto_kaax_chat = question.split("¿Dónde está disponible el ")[1].split(" y cuánto cuesta?")[0].strip()
        disponibilidad = combined_df[combined_df['Producto'].str.contains(producto_kaax_chat, case=False, na=False)][
            ['Mercado', 'Precio']].drop_duplicates().to_string(index=False)
        raw_response = f"{producto_kaax_chat} está disponible en:\n{disponibilidad}"
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(get_humanized_response(raw_response))
        loop.close()
        return result
    elif "Listar todos los productos disponibles en el mercado" in question:
        mercado = question.split("Listar todos los productos disponibles en el mercado ")[1].strip()
        mercado = mercado.replace(".", "")
        productos = combined_df[combined_df['Mercado'] == mercado]['Producto'].unique()
        raw_response = "Claro estos son los productos disponibles en " + mercado + ":\n" + "\n".join(productos)
        return raw_response
    else:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(get_response(question, chat_history))
        loop.close()
        return result
