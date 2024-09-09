import cv2
import pytesseract
import re
import json

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def clean_text(text):
    unwanted_phrases = [
        r'GRUPO',
        r'ASIENTO',
        r'Boarding pass your bag',
        r'‘ rat ah iM ily at'
    ]
    for phrase in unwanted_phrases:
        text = re.sub(phrase, '', text, flags=re.IGNORECASE)
        
    text = re.sub(r'[^\w\s:/]', '', text) 
    text = re.sub(r'\s+', ' ', text)
    return text

def load_airport_codes(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_flight_info_images(text, airport_codes):
    flight_info = {}
    cities = [
        'Bogota', 'Ciudad de Mexico', 'Santa Marta', 'Lima', 'San Francisco', 'Nueva York', 'Cartagena', 
        'Buenos Aires', 'Bariloche', 'Medellin', 'Madrid', 'Sao Paulo', 'Rio de Janeiro', 'Ciudad de Panama', 
        'Santiago', 'Sao Paulo', 'Brasilia', 'Guadalajara', 'Belo Horizonte', 'Monterrey', 'Campinas', 
        'Rio de Janeiro (Santos Dumont)', 'Caracas', 'Quito', 'Las Palmas de Gran Canaria', 'Cancun', 
        'Punta Cana', 'Liberia', 'San Jose', 'Guayaquil', 'San Salvador', 'Asuncion', 'Montevideo', 
        'Berlin', 'Londres', 'Tokio', 'Roma', 'Sidney', 'Amsterdam', 'Estambul', 'Delhi', 'Pekin', 
        'El Cairo', 'Rio de Janeiro', 'Sao Paulo', 'Toronto', 'Chicago', 'Mumbai', 'Seul', 'Hong Kong', 
        'Singapur', 'Dublin', 'Sidney', 'Viena', 'Atenas', 'Barcelona', 'Ciudad del Cabo', 'Dubai', 
        'Helsinki', 'Lisboa', 'Moscú', 'Oslo', 'Estocolmo', 'Zurich', 'La Paz', 'Luxemburgo', 'Montreal', 
        'Quebec', 'Vancouver', 'Washington D. C.', 'Munich'
    ]

    # Patrones 
    departure_date_patterns = [
        r'\b(\w{3},\s*\d{1,2}\s+\w+)\s*\|\s*(\d{2}:\d{2})\b',  
        r'\b(\w{3}\.\s*\d{2}\s+\w{3}\.\s*\d{4})\b',            
        r'\b(\w{3},\s*\d{2}\s+\w{3})\b',                       
        r'\b(\d{2}\s+\w{3}\s+\d{4})\b',
        r'\b\((\d{1,2}/\w{3})\)\b', 
        r'\b(\d{1,2}/\w{3})\b',
        r'\bFecha\s+de\s+salida\s*:\s*(\d{2}/\d{2}/\d{4})\b',
        r'\b(\d{2}\s+[A-Z]{3})\b'                        
    ]

    flight_patterns = [
        r'\b(AV\s*\d{1,4})\b',               
        r'\bNúmero de vuelo\s*([A-Z0-9]{2,6})\b',
        r'\bVuelo\s*([A-Z0-9]+)\b',           
        r'\bGATE\s*([A-Z0-9]+)\b',
        r'\bVUELO\s+([A-Z]{2}\s*\d{1,4}\*)\b',
        r'\b([A-Z]{3}\d{3})\b'             
    ]
    
    name_patterns = [
        r'\bPasajero\s+([A-Z][a-z]+\s+[A-Z][a-z]+)\b',  
        r'\bPasajero\s+([A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+)\b',  
        r'\bPasajero\s+([A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+)\b',  
        r'\bNOMBRE\s+PASAJERO:\s+([A-Z]+/[A-Z]+)\b',  
        r'\b([A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+)\s+(AV)\s*\d+\b',
        r'\b([A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+)\s+(AV)\s*\d+\b',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\s*/\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+))',
        r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+){3})\b'
    ]
    
    origin_destination_patterns = [
        r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
        r'\b([A-Za-z\s]+) International\b',
        r'\b([A-Z]{3})\b',
        r'\bBoarding\s+([A-Za-z\s]+)\s+(\d{2}:\d{2})\b',  
        r'\bDeparture\s+([A-Za-z\s]+)\s+(\d{2}:\d{2})\b'
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
        
    for pattern in origin_destination_patterns:
        codes = re.findall(pattern, text)
        if codes: 
            found_cities = [code for code in codes[0].split() if code in cities]
            
            if found_cities:
                flight_info['origen'] = found_cities[0]
                flight_info['destino'] = found_cities[1]
                break
        
            else: 
                valid_codes = [code for code in codes if code in airport_codes]
                if len(valid_codes) >= 2:
                    flight_info['origen'] = airport_codes.get(valid_codes[0], valid_codes[0])
                    flight_info['destino'] = airport_codes.get(valid_codes[1], valid_codes[1])
                elif len(valid_codes) == 1:
                    flight_info['origen'] = airport_codes.get(valid_codes[0], valid_codes[0])
                    flight_info['destino'] = None
                else:
                    flight_info['origen'] =  None
                    flight_info['destino'] = None

    
    operador_match = re.search(r'(Avianca|Aero República S.A|Air Europa|JetSMART|LATAM|Latam|KLM)', text, re.IGNORECASE)
    if operador_match:
        if operador_match.group(1) == "Aero República S.A": 
            flight_info['operado_por'] = "Wingo"
        else:  
            flight_info['operado_por'] = operador_match.group(1)
            
    flight_info = {
        'fecha_salida': flight_info.get('fecha_salida', 'N/A'),
        'pasajero': flight_info.get('pasajero', 'N/A'),
        'vuelo': flight_info.get('vuelo', 'N/A'),
        'operado_por': flight_info.get('operado_por', 'N/A'),
        'origen': flight_info.get('origen', 'N/A'),
        'destino': flight_info.get('destino', 'N/A')
    }

    return flight_info

def process_images(image_path):
    img = cv2.imread(image_path)
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(img, config=custom_config)
    json_file_path = "../data/airport_codes.json"
    airport_codes = load_airport_codes(json_file_path)
    clean_text_data = clean_text(text)
    flight_info = extract_flight_info_images(clean_text_data, airport_codes)
    return flight_info