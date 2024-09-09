import os
import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import pandas as pd
from main import main
from airline_codes import load_airline_codes
from models import get_db_engine, FlightInfo
from sqlalchemy.orm import sessionmaker

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

def get_flights_by_airline(airline_name):
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    flights = session.query(FlightInfo).filter_by(operado_por=airline_name).all()
    
    session.close()
    return flights

def get_airline_names():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    airline_names = session.query(FlightInfo.operado_por).distinct().all()
    
    session.close()
    return [name[0] for name in airline_names]

def plot_flight_data(df):
    st.title("Dashboard de Vuelos")
    
    st.subheader("Información de Vuelos por Aerolínea")
    airline_names = get_airline_names()
    selected_airline = st.selectbox("Selecciona una aerolínea", airline_names)

    if selected_airline:
        flights = get_flights_by_airline(selected_airline)
        
        if flights:
            st.write(f"Vuelos operados por {selected_airline}:")
            
            flight_data = [{
                "Fecha de Salida": flight.fecha_salida,
                "Pasajero": flight.pasajero,
                "Vuelo": flight.vuelo,
                "Reserva": flight.reserva,
                "Origen": flight.origen,
                "Destino": flight.destino,
                "Hora de Sala": flight.hora_sala
            } for flight in flights]
            
            st.dataframe(flight_data) 
        else:
            st.write(f"No se encontraron vuelos para {selected_airline}.")
    
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

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "show_dashboards" not in st.session_state:
    st.session_state.show_dashboards = False 

uploaded_file = st.file_uploader("Elige un archivo PDF o imagen", type=["pdf", "jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file  

if st.session_state.uploaded_file is not None:
    st.write("Archivo cargado:")
    st.write(st.session_state.uploaded_file.name)
    
    result = handle_file(st.session_state.uploaded_file)
    
    if st.session_state.uploaded_file.type.startswith('image/'):
        image = Image.open(st.session_state.uploaded_file)
        st.image(image, caption='Imagen cargada', use_column_width=True)
        flight_info = main(result, "image")
        st.write(flight_info)
    
    if st.session_state.uploaded_file.type == "application/pdf":
        flight_type = st.radio("Seleccione el tipo de vuelo", ("Directo", "Con escala"))
        
        if st.button("Procesar vuelo PDF"):
            flight_info = main(result, "pdf", flight_type)
            st.write(flight_info)

if st.button("Mostrar Dashboards"):
    st.session_state.show_dashboards = True  

if st.session_state.show_dashboards:
    flight_data = load_flight_data()
    if not flight_data.empty:
        plot_flight_data(flight_data)
    else:
        st.write("No hay datos disponibles.")
