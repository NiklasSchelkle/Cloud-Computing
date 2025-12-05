"""
Haupt-Anwendung der Flights API (FastAPI).

Diese Datei ist der zentral für die FastAPI-Instanz.
Sie ist verantwortlich für:
1. Das Herstellen der Datenbankverbindung und die Erstellung des Datenbank-Schemas (falls nötig).
2. Das Definieren von Pydantic-Schemas für die Datenvalidierung und Dokumentation.
3. Das Implementieren aller CRUD-Operationen (Create, Read, Update, Delete) für die Flugdatensätze (hier kommt db.commit()ins Spiel).
"""

from fastapi import FastAPI, Depends, HTTPException # Importiert FastAPI für die API-Erstellung und Komponenten zur Abhängigkeitsinjektion (Depends) und Fehlerbehandlung (HTTPException).
from sqlalchemy.orm import Session # Importiert die Session-Klasse von SQLAlchemy für Datenbank-Interaktionen.
from pydantic import BaseModel # Importiert die Basisklasse für die Datenmodelle (Schemas) zur Validierung.
from typing import List, Optional # Importiert Typ-Annotationen, um Listen und optionale Felder zu definieren.
from datetime import datetime # Importiert datetime für die Behandlung von Zeitstempel-Feldern.
from database import SessionLocal, engine # Importiert die Session Factory und die Datenbank Engine aus database.py.
from models import Flight, Base # Importiert das Flight-Datenbankmodell und die Base-Klasse aus models.py.

Base.metadata.create_all(bind=engine) #  Weist die Base-Klasse an, das Modell (Flight) zu nehmen und die entsprechende Tabelle in der Datenbank zu erstellen.
app = FastAPI(title="Flights API") # Erstellt die zentrale FastAPI-Anwendung mit dem Titel "Flights API".

def get_db():
    db = SessionLocal() # Erstellt eine neue SQLAlchemy-Session
    try: yield db # Gibt die Session an den API-Endpunkt weiter, der sie benötigt.
    finally: db.close() # Schließt die Sesssion am Ende.

class FlightBase(BaseModel): # Pydantic-Schema für die Datenstruktur der Flugdaten. Wird für GET-Antworten verwendet. Erbt von Basemodel!
                             # stellt sicher, dass alle die in die API eingehen den richtigen Datentyp haben (Validierung)
                             # generiert automatisch die Dokumentation (Swagger/OpenAPI) und legt fest welche Felder bei einer Abfrage zurückgegeben werden!
    flight_id: str   # Darf nicht leer sein! 
    airline_id: Optional[str] = None # --> kann leerer Wert sein und ist optional für die Eingabe!
    airline: Optional[str] = None
    aircraft_id: Optional[str] = None
    scheduled_departure: Optional[datetime] = None
    departure: Optional[datetime] = None
    departure_delay: Optional[float] = None
    scheduled_arrival: Optional[datetime] = None
    arrival: Optional[datetime] = None
    arrival_delay: Optional[float] = None
    air_time: Optional[float] = None
    distance: Optional[float] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    year: Optional[float] = None
    engines: Optional[float] = None
    seats: Optional[float] = None
    max_weight_pounds: Optional[str] = None
    origin: Optional[str] = None
    name_origin: Optional[str] = None
    latitude_origin: Optional[float] = None
    longitude_origin: Optional[float] = None
    destination: Optional[str] = None
    name_destination: Optional[str] = None
    latitude_destination: Optional[float] = None
    longitude_destination: Optional[float] = None
    weekday: Optional[str] = None
    hour: Optional[int] = None
    cancelled: Optional[bool] = None

    class Config:
        from_attributes = True  # Erlaubt Pydantic, Daten direkt aus SQLAlchemy-Modellen (Objekt-Attributen) zu lesen.

class FlightSearch(BaseModel): # Pydantic-Schema für die Suchkriterien im POST /flights/search Endpunkt. --> Erbt von Basemodel!
    airline: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    weekday: Optional[str] = None

class FlightCreate(BaseModel): # Pydantic-Schema für die Daten, die beim Hinzufügen eines neuen Fluges erwartet werden. 
    flight_id: str # flight_id ist hier zwingend erforderlich, alles andere ist optional!
    airline_id: Optional[str] = None
    airline: Optional[str] = None
    aircraft_id: Optional[str] = None
    scheduled_departure: Optional[datetime] = None
    departure: Optional[datetime] = None
    departure_delay: Optional[float] = None
    scheduled_arrival: Optional[datetime] = None
    arrival: Optional[datetime] = None
    arrival_delay: Optional[float] = None
    air_time: Optional[float] = None
    distance: Optional[float] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    year: Optional[float] = None
    engines: Optional[float] = None
    seats: Optional[float] = None
    max_weight_pounds: Optional[str] = None
    origin: Optional[str] = None
    name_origin: Optional[str] = None
    latitude_origin: Optional[float] = None
    longitude_origin: Optional[float] = None
    destination: Optional[str] = None
    name_destination: Optional[str] = None
    latitude_destination: Optional[float] = None
    longitude_destination: Optional[float] = None
    weekday: Optional[str] = None
    hour: Optional[int] = None
    cancelled: Optional[bool] = None

@app.get("/flights/{flight_id}", response_model=FlightBase) # Definiert einen GET-Endpunkt zum Abrufen eines einzelnen Fluges anhand seiner ID.
def get_flight(flight_id: str, db: Session = Depends(get_db)): # Nimmt flight_id aus der URL und die DB-Session über Dependency Injection entgegen.
    f = db.query(Flight).filter(Flight.flight_id == flight_id).first() # Führt die Datenbankabfrage durch (suche nach Primary Key).
    if not f: raise HTTPException(404,"Flight not found") # Falls kein Flug gefunden wird, wird der HTTP-Fehler 404 zurückgegeben.
    return f # Gibt das gefundene Flight-Objekt zurück.

@app.post("/flights/search", response_model=List[FlightBase]) # Definiert einen POST-Endpunkt für komplexe Suchanfragen. Gibt eine Liste von Flügen zurück.
def search_flights(s: FlightSearch, db: Session = Depends(get_db)): # Nimmt das FlightSearch-Schema (Suchkriterien) und die DB-Session entgegen.
    q = db.query(Flight) # Beginnt die Datenbankabfrage auf das Flight-Modell.
    if s.airline: q = q.filter(Flight.airline_id==s.airline) # Fügt einen Filter hinzu, wenn das Suchkriterium 'airline' vorhanden ist.
    if s.origin: q = q.filter(Flight.origin==s.origin) # Fügt einen Filter hinzu, wenn das Suchkriterium 'origin' vorhanden ist.
    if s.destination: q = q.filter(Flight.destination==s.destination) # Fügt einen Filter hinzu, wenn das Suchkriterium 'destination' vorhanden ist.
    if s.weekday: q = q.filter(Flight.weekday==s.weekday) # Fügt einen Filter hinzu, wenn das Suchkriterium 'weekday' vorhanden ist.
    return q.all() # Führt die endgültige Abfrage aus und gibt alle passenden Ergebnisse zurück.

@app.post("/flights/add", response_model=FlightBase) # Definiert einen POST-Endpunkt zum Hinzufügen eines neuen Flugdatensatzes.
def add_flight(f: FlightCreate, db: Session = Depends(get_db)): # Nimmt das FlightCreate-Schema (die neuen Daten) und die DB-Session entgegen.
    if db.query(Flight).filter(Flight.flight_id==f.flight_id).first(): # Prüft, ob ein Flug mit dieser flight_id bereits existiert (Duplikatprüfung).
        raise HTTPException(400,"Flight with this flight_id already exists") # Gibt Fehler 400 zurück, falls der Flug bereits existiert.
    new = Flight(**f.dict()) # Erstellt ein neues SQLAlchemy Flight-Modell-Objekt aus den empfangenen Pydantic-Daten.
    db.add(new) # Markiert das neue Objekt für das Einfügen (Insertion) in die Datenbank.
    db.commit() #  db.commit!!!!!: Schreibt die vorgemerkte Änderung (den neuen Flug) permanent in die Datenbank.
    db.refresh(new) # Aktualisiert das Objekt, um Werte abzurufen, die von der DB generiert wurden (wichtig nach dem Commit).
    return new # Gibt das neu hinzugefügte Objekt zurück.

@app.delete("/flights/{flight_id}") # Definiert einen DELETE-Endpunkt zum Löschen eines Fluges anhand seiner ID.
def delete_flight(flight_id: str, db: Session = Depends(get_db)): # Nimmt flight_id aus der URL und die DB-Session entgegen.
    f = db.query(Flight).filter(Flight.flight_id==flight_id).first() # Sucht den zu löschenden Flug.
    if not f: raise HTTPException(404,"Flight not found") # Fehler 404, wenn der Flug nicht existiert.
    db.delete(f) # Markiert das gefundene Objekt zum Löschen.
    db.commit() # db. commit!!! Führt die Löschung permanent in der Datenbank durch.
    return {"detail": f"Flight {flight_id} deleted successfully"} 

