import pandas as pd

def load_airline_codes(excel_path):
    df = pd.read_excel(excel_path)
    airline_codes = pd.Series(df.Código.values, index=df.Nombre).to_dict()
    return airline_codes
