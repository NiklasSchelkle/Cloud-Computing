"""database.py ist unverzichtbar für die Datenabfrage und Datenmodifikation durch die FastAPI-API.
   Ohne diese Python Datei könnte meine APi die Flugdaten nicht erreichen. 

Was macht der Code?:
    - DATABASE_URL: Erstellt den Verbindungsstring unter Verwendung des Hostnamens 'db' (gemäß Docker Compose Netzwerk).
    - engine: Stellt die eigentliche Datenbankverbindung her.
    - SessionLocal: Für die Erstellung von Datenbank-Sessions, die für CRUD-Operationen
                    (Create, Read, Update, Delete) in den FastAPI-Endpunkten benötigt werden.
    - Base: Die deklarative Basisklasse, von der alle Datenmodelle (in models.py) erben.
"""
import os # brauch man für die .env
from dotenv import load_dotenv  # .env-Unterstützung für lokale Entwicklung
from sqlalchemy import create_engine # zum erstellen der engine
from sqlalchemy.orm import sessionmaker, declarative_base # Importiert Klassen zur Session-Erstellung und Modell-Basis.

# .env-Datei laden (in Docker übernimmt Compose das automatisch)
load_dotenv()

# Werte aus .env lesen
# POSTGRES_USER und POSTGRES_PASSWORD werden aus der .env geladen (wird aber durch docker Compose eh gesetzt)
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# PostgreSQL-Verbindungsstring, wie in Docker-Compose. 
# Innerhalb des Docker-Netzwerks muss der Service-Name des Datenbank-Containers als Hostname verwendet werden --> "db"
# Durch den f-String werden Benutzername und Passwort aus der .env eingesetzt.
DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:5432/flights"  
# Wer will zugreifen? --> //{POSTGRES_USER}:{POSTGRES_PASSWORD} + Welche Datenbank? --> @db:5432/flights

# Engine erstellen.
# Stellt die Verbindung her.
engine = create_engine(DATABASE_URL)

# SessionFactory für DB-Zugriffe
SessionLocal = sessionmaker(autocommit=False, bind=engine)
# bind=engine: weist die Session an, welche Datenbankverbindung (engine) sie verwenden soll, um mit der Datenbank zu kommunizieren.
# auf Abruf werden neue, isolierte Datenbank-Sitzungen (Sessions) erstellt --> Nur in einer Session können anwender etwas an der Datenbank ändern oder abfragen
# autocommit=False: Operationen (INSERT, UPDATE, DELETE) werden nicht automatisch gespeichert — nur bei db.commit(). Das wird in main.py genutzt :) 

# Base-Klasse für Modelle
Base = declarative_base()
# schafft eine Basisklasse, von der alle Ihre Datenmodelle erben. Ist in models erklärt! :)
