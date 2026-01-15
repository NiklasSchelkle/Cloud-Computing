import pandas as pd
import os
import time
from sqlalchemy import create_engine
from dotenv import load_dotenv

# .env laden
load_dotenv()

# Datenbank-Verbindung (Hostname 'db' wie im Docker-Netzwerk)
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
# Hier 'db' statt 'localhost' nutzen, wegen docker Netzwerk
DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:5432/flights"

def run_ingestion():
    print("Starte Daten-Ingestion...")
    
    # CSV laden
    df = pd.read_csv("flights_clean.csv")
    
    # Eindeutige flight_id generieren
    df["flight_id"] = df["flight"].astype(str) + (df.index + 1).astype(str)
    
    # Engine erstellen
    engine = create_engine(DATABASE_URL)
    
    # Daten in DB schreiben
    # "replace" sorgt dafür, dass die Tabelle bei jedem Neustart frisch befüllt wird. Die Daten sind also nicht doppelt vorhanden.
    df.to_sql("flights", engine, if_exists="replace", index=False)
    
    print(f"Erfolgreich {len(df)} Zeilen in die Datenbank geladen!")

if __name__ == "__main__":
    # Kleiner Delay, damit die DB sicher bereit ist
    time.sleep(5) 
    run_ingestion()