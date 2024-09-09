import os
import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import pandas as pd
from main import main
from airline_codes import load_airline_codes
from models import get_db_engine

excel_path = "../data/Aerolineas.xlsx"
airline_codes = load_airline_codes(excel_path)

def handle_file(uploaded_file):
    file_path = os.path.join("data", uploaded_file.name)
    
    if uploaded_file.type == "application/pdf":
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Archivo PDF guardado en: {file_path}")
    
    elif uploaded_file.type.startswith("image/"):
        image = Image.open(uploaded_file)
        file_path = file_path.rsplit('.', 1)[0] + '.png'  
        image.save(file_path, format='PNG') 
        st.success(f"Imagen guardada en: {file_path}")
    
    return file_path

def load_flight_data():
    engine = get_db_engine()
    query = "SELECT * FROM flight_info"
    df = pd.read_sql(query, engine)
    return df

def plot_flight_data(df):
    st.subheader("Cantidad de vuelos por día")
    daily_flights = df['fecha_salida'].value_counts().sort_index()
    st.bar_chart(daily_flights)

    st.subheader("Distribución de aerolíneas")
    airline_distribution = df['airline_code'].value_counts()
    airline_names = {v: k for k, v in airline_codes.items()}
    airline_distribution.index = airline_distribution.index.map(airline_names)
    
    fig, ax = plt.subplots()
    ax.pie(airline_distribution, labels=airline_distribution.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

if not os.path.exists("data"):
    os.makedirs("data")

st.title("Carga y Procesa Vuelos")

uploaded_file = st.file_uploader("Elige un archivo PDF o imagen", type=["pdf", "jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.write("Archivo cargado:")
    st.write(uploaded_file.name)
    
    result = handle_file(uploaded_file)
    
    if uploaded_file.type.startswith('image/'):
        image = Image.open(uploaded_file)
        st.image(image, caption='Imagen cargada', use_column_width=True)
        fligth_info = main(result, "image")
        st.write(fligth_info)
    
    if uploaded_file.type == "application/pdf":
        flight_type = st.radio("Seleccione el tipo de vuelo", ("Directo", "Con escala"))
        fligth_info = main(result, "pdf", flight_type)
        st.write(fligth_info)
        
        
    if st.button("Mostrar Dashboards"):
        flight_data = load_flight_data()
        if not flight_data.empty:
            plot_flight_data(flight_data)
        else:
            st.write("No hay datos disponibles.")
