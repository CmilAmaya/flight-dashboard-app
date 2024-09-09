import fitz 
import re
import json 
import spacy

nlp = spacy.load("es_core_news_sm")

def extract_text_fitz(pdf_path):
    doc = fitz.open(pdf_path)
    for page in doc:
        text = page.get_text("text")
    return text

def clean_text(text):
    unwanted_phrases = [
        r'GRUPO',
        r'ASIENTO'
    ]
    for phrase in unwanted_phrases:
        text = re.sub(phrase, '', text, flags=re.IGNORECASE)
    
    text = text.replace('\n', ' ').strip() 
    text = ' '.join(text.split())
    return text  

def load_airport_codes(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_flight_info(text, airport_codes):
    flight_info = {}
   
    # Patrones 
    departure_date_patterns = [
        r'\b(\w{3},\s*\d{1,2}\s+\w+)\s*\|\s*(\d{2}:\d{2})\b',  
        r'\b(\w{3}\.\s*\d{2}\s+\w{3}\.\s*\d{4})\b',            
        r'\b(\w{3},\s*\d{2}\s+\w{3})\b',                       
        r'\b(\d{2}\s+\w{3}\s+\d{4})\b',
        r'\b\((\d{1,2}/\w{3})\)\b', 
        r'\b(\d{1,2}/\w{3})\b'                         
    ]

    flight_patterns = [
        r'VUELO\s+([A-Z]{2}\d+)',
        r'\b(AV\s*\d{1,4})\b',               
        r'\bNúmero de vuelo\s*([A-Z0-9]{2,6})\b',
        r'\bVuelo\s*([A-Z0-9]+)\b',           
        r'\bGATE\s*([A-Z0-9]+)\b',
        r'\bVUELO\s+([A-Z]{2}\s*\d{1,4}\*)\b',
        r'\bVuelo\s+([A-Z]{2})\s*(\d{3,4})\*?\b',
        r'\bVuelo\s+([A-Z]{2})\s*(\d{4})\*\b'             
    ]
    
    reservation_patterns = [
        r'\b([A-Z0-9]{6})\s+CÓDIGO\s+DE\s+RESERVA\b',  
        r'\b([A-Z0-9]{6})\s+Código\s+de\s+reserva\b',
        r'\bCódigo de reserva\s+([A-Z0-9]{6})\b',  
        r'\b(\d[A-Z][A-Z0-9]{4})\b'                                
    ]
    
    time_in_room_patterns = [
        r'\b(\d{1,2}:\d{2}\s*[apAP]\.?[mM]\.?)\s+Embarque\b',
        r'\bHora\s+en\s+sala\s+(\d{1,2}:\d{2}\s*[apAP]\.?[mM]\.?)\b',
        r'\bHora\s+en\s+sala\s+(\d{1,2}:\d{2})\b',
        r'\bEMBARQUE.*\b(\d{1,2}:\d{2}\s*[apAP]\.?[mM]\.?)\b',
        r'\bHORA\s+EN\s+SALA.*\b(\d{1,2}:\d{2}\s*[apAP]\.?[mM]\.?)\b',
        r'\bBoarding\s+\d{2}\s+\w{3}\s+\d{4}\s+(\d{1,2}:\d{2}\s*[apAP]\.?[mM]\.?)\b',
        r'\bBoarding\s+\d{4}-\d{2}-\d{2}\s+(\d{1,2}:\d{2}\s*[apAP]\.?[mM]\.?)\b',
        r'\bHORA\s+PRESENTACIÓN\s+PUERTA\s+DE\s+EMBARQUE\s+(\d{1,2}:\d{2}\s*[apAP]\.?[mM]\.?)\b',
        r'PUERTA\s+DE\s+EMBARQUE\s+(\d{1,2}:\d{2})',
        r'HORA\s+PRESENTATION\s+AEROPUERTO\s+(\d{1,2}:\d{2})'
    ]
    
    name_patterns = [
        r'NOMBRE\s+PASAJERO\s+([A-Z]+/[A-Z]+)',
        r'\bNOMBRE\s+PASAJERO:\s+([A-Z]+/[A-Z]+)\b',  
        r'\bPasajero\s+([A-Z][a-z]+\s+[A-Z][a-z]+)\b',  
        r'\bPasajero\s+([A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+)\b',  
        r'\bPasajero\s+([A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+)\b',  
        r'\b([A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+)\s+(AV)\s*\d+\b',
        r'\b([A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+)\s+(AV)\s*\d+\b',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\s*/\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+))'
    ]
    
    origin_destination_patterns = [
        r'\b([A-Za-z\s]+) International\b',
        r'\b([A-Z]{3})\b',
        r'\bBoarding\s+([A-Za-z\s]+)\s+(\d{2}:\d{2})\b',  
        r'\bDeparture\s+([A-Za-z\s]+)\s+(\d{2}:\d{2})\b',
        r'(?:DESDE|HACIA)\s([A-Z\s]+)'
    ]

    for pattern in departure_date_patterns:
        fecha_match = re.search(pattern, text)
        if fecha_match:
            flight_info['fecha_salida'] = fecha_match.group(1)
            break  

    pasajero_match = None
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            pasajero_match = match.group(1).strip()
            break
    if pasajero_match:
        flight_info['pasajero'] = pasajero_match 

    for pattern in flight_patterns:
        vuelo_match = re.search(pattern, text)
        if vuelo_match:
            flight_info['vuelo'] = vuelo_match.group(1)
            break 
 
    for pattern in reservation_patterns:
        reserva_match = re.search(pattern, text)
        if reserva_match:
            flight_info['reserva'] = reserva_match.group(1)
            break 

    for pattern in flight_patterns:
        vuelo_match = re.search(pattern, text)
        if vuelo_match:
            flight_info['vuelo'] = vuelo_match.group(1)
            break  
    
    for pattern in time_in_room_patterns:
        hora_en_sala_match = re.search(pattern, text, re.IGNORECASE)
        if hora_en_sala_match:
            flight_info['hora_en_sala'] = hora_en_sala_match.group(1)
            break
        
    for pattern in origin_destination_patterns:
        codes = re.findall(pattern, text)
        unique_codes = set(code.strip() for code in codes)
        print(unique_codes)
        if codes:
            valid_codes = [code for code in unique_codes if code in airport_codes]
            if len(valid_codes) >= 2:
                flight_info['origen'] = airport_codes.get(valid_codes[0], valid_codes[0])
                flight_info['destino'] = airport_codes.get(valid_codes[1], valid_codes[1])
                break
            elif len(valid_codes) == 1:
                flight_info['origen'] = airport_codes.get(valid_codes[0], valid_codes[0])
                flight_info['destino'] = None
                break
            else:
                flight_info['origen'] = None
                flight_info['destino'] = None

    operador_match = re.search(r'(Avianca|Aero República S.A|Air Europa|JetSMART|LATAM|Latam|KLM)', text)
    if operador_match:
        if operador_match.group(1) == "Aero República S.A": 
            flight_info['operado_por'] = "Wingo"
        elif operador_match.group(1) == "LATAM": 
            flight_info['operado_por'] = "Latam"
        else:  
            flight_info['operado_por'] = operador_match.group(1)
            
    flight_info = {
        'fecha_salida': flight_info.get('fecha_salida', 'N/A'),
        'pasajero': flight_info.get('pasajero', 'N/A'),
        'vuelo': flight_info.get('vuelo', 'N/A'),
        'reserva': flight_info.get('reserva', 'N/A'),
        'operado_por': flight_info.get('operado_por', 'N/A'),
        'origen': flight_info.get('origen', 'N/A'),
        'destino': flight_info.get('destino', 'N/A'),
        'hora_sala':flight_info.get('hora_en_sala', 'N/A')
    }

    return flight_info

def data_process_pdfs_direct(pdf_path):
    json_file_path = "../data/airport_codes.json" 
    text = extract_text_fitz(pdf_path)
    clean_text_data = clean_text(text)
    airport_codes = load_airport_codes(json_file_path)
    flight_info = extract_flight_info(clean_text_data, airport_codes)
    return flight_info