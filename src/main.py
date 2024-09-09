import os
from sqlalchemy.orm import sessionmaker
from models import FlightInfo, get_db_engine
from data_processing import data_process_pdfs_direct
from data_processing_scales import data_process_pdfs_with_scales
from data_processing_images import process_images
from airline_codes import load_airline_codes


excel_path = os.path.join(os.path.dirname(__file__), '../data/Aerolineas.xlsx')
airline_codes = load_airline_codes(excel_path)

def process_pdf_direct(pdf_path):
    return data_process_pdfs_direct(pdf_path)
    
def process_pdf_with_scales(pdf_path):
    return data_process_pdfs_with_scales(pdf_path)

def process_image(image_path):
    return process_images(image_path)

def save_to_db(flight_info):
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    if isinstance(flight_info, list):
        for flight in flight_info:
            save_single_flight(session, flight)
    else:
        save_single_flight(session, flight_info)

    session.commit()
    session.close()

def save_single_flight(session, flight):
    existing_record = session.query(FlightInfo).filter_by(
        vuelo=flight.get('vuelo')
    ).first()

    airline_code = airline_codes.get(flight.get('operado_por', 'N/A'), None)

    if existing_record:
        print("El registro ya existe")
        return "El registro ya existe."

    new_flight_info = FlightInfo(
        fecha_salida=flight.get('fecha_salida', 'N/A'),
        pasajero=flight.get('pasajero', 'N/A'),
        vuelo=flight.get('vuelo', 'N/A'),
        reserva=flight.get('reserva', 'N/A'),
        operado_por=flight.get('operado_por', 'N/A'),
        origen=flight.get('origen', 'N/A'),
        destino=flight.get('destino', 'N/A'),
        hora_sala=flight.get('hora_sala', 'N/A'),
        airline_code=airline_code
    )

    session.add(new_flight_info)



def main(file_path, file_type, flight_type=None):
    
    if file_type == "pdf":
        if flight_type == "Directo":
            flight_info = process_pdf_direct(file_path)
        
        elif flight_type == "Con escala":
            flight_info = process_pdf_with_scales(file_path)
            print(flight_info)
        
    elif file_type.startswith("image"):
        flight_info = process_image(file_path)

    if flight_info:
        save_to_db(flight_info)
    
    return flight_info