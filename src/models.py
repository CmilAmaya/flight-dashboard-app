from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()

Base = declarative_base()

class FlightInfo(Base):
    __tablename__ = 'flight_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha_salida = Column(String, nullable=False)
    pasajero = Column(String, nullable=False)
    vuelo = Column(String, nullable=False)
    reserva = Column(String, nullable=False)
    operado_por = Column(String, nullable=False)
    origen = Column(String, nullable=False)
    destino = Column(String, nullable=False)
    hora_sala = Column(String, nullable=True)
    airline_code = Column(Integer, nullable=True)

def get_db_engine():
    user = st.secrets["db_user"]
    password = st.secrets["db_password"]
    host = st.secrets["db_host"]
    port = st.secrets["db_port"]
    database = st.secrets["db_name"]
    
    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(connection_string)
    return engine

def create_tables():
    engine = get_db_engine()
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    create_tables()
