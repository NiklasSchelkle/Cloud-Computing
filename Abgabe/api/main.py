"""
Haupt-Anwendung der Flights API (FastAPI).

Diese Datei ist der zentral für die FastAPI-Instanz.
Sie ist verantwortlich für:
1. Das Herstellen der Datenbankverbindung und die Erstellung des Datenbank-Schemas (falls nötig).
2. Das Definieren von Pydantic-Schemas für die Datenvalidierung und Dokumentation.
3. Das Implementieren aller CRUD-Operationen (Create, Read, Update, Delete) für die Flugdatensätze (hier kommt db.commit()ins Spiel).
4. Implementierung von OAuth2-Authentifizierung, Passwort-Hashing (Bcrypt) und MFA (Duo Mobile). --> Sicherheitsfeature

"""

from fastapi import FastAPI, Depends, HTTPException # Importiert FastAPI für die API-Erstellung und Komponenten zur Abhängigkeitsinjektion (Depends) und Fehlerbehandlung (HTTPException).
from sqlalchemy.orm import Session # Importiert die Session-Klasse von SQLAlchemy für Datenbank-Interaktionen.
from pydantic import BaseModel # Importiert die Basisklasse für die Datenmodelle (Schemas) zur Validierung.
from typing import List, Optional # Importiert Typ-Annotationen, um Listen und optionale Felder zu definieren.
from datetime import datetime, timedelta # Importiert datetime für die Behandlung von Zeitstempel-Feldern.
from database import SessionLocal, engine # Importiert die Session Factory und die Datenbank Engine aus database.py.
from models import Flight, Base, User # Importiert das Flight-Datenbankmodell und die Base-Klasse aus models.py.
from passlib.context import CryptContext # Importiert CryptContext für das sichere Hashing von Passwörtern.
from jose import JWTError, jwt # Importiert JWT für die Token-Erstellung (OAuth2).
from fastapi.security import OAuth2PasswordBearer # Importiert OAuth2 Standard für die Token-Abfrage.
import pyotp # Importiert pyotp für die Zwei-Faktor-Authentifizierung (für Duo Mobile).

Base.metadata.create_all(bind=engine) #  Weist die Base-Klasse an, das Modell (Flight) zu nehmen und die entsprechende Tabelle in der Datenbank zu erstellen.
app = FastAPI(title="Flights API")    # Erstellt die zentrale FastAPI-Anwendung mit dem Titel "Flights API".

# OAUTH2 & SICHERHEIT
SECRET_KEY = "FlughafenABC_Super_Secret_Key_2025" # Geheimschlüssel für JWT Tokens.
ALGORITHM = "HS256" # Algorithmus für die Token-Verschlüsselung. # Habe HS256 gewählt, da es weit verbreitet und sicher ist. --> Habe mich hier auf gemini verlassen :)
ACCESS_TOKEN_EXPIRE_MINUTES = 300 # Token-Gültigkeitsdauer. Wenn das abgelaufen ist, muss der USer sich neu einloggen um z.B. Flüge löschen zu können
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") # Definiert den Token-Endpunkt.

# Passwort-Sicherheit 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# 'deprecated="auto"' sorgt dafür, dass die Bibliothek veraltete (unsichere) Hashes erkennt 
# und diese bei einem Login automatisch auf den neuesten Stand (Bcrypt) aktualisiert.

def get_db():
    db = SessionLocal()              # Erstellt eine neue SQLAlchemy-Session
    try: yield db                    # Gibt die Session an den API-Endpunkt weiter, der sie benötigt.
    finally: db.close()              # Schließt die Sesssion am Ende.

# AUTH
def create_access_token(data: dict): # Erstellt einen zeitlich befristeten JWT-Ausweis.
    to_encode = data.copy() # Kopiert die übergebenen Daten.
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # Berechnet das "Ablaufdatum". also + 300 Minuten
    to_encode.update({"exp": expire}) # Fügt das Ablaufdatum zu den zu codierenden Daten hinzu.
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # Erstellt und gibt den JWT-Token zurück.

# User Schemas
class UserCreate(BaseModel): # Pydantic-Schema für die Registrierung
    username: str
    email: str
    password: str

class UserLogin(BaseModel): # Spezielles Schema für Login inklusive Duo-Code (2FA).
    username: str
    password: str
    otp_code: Optional[str] = None # Der 6-stellige Code aus der Duo App.

class UserOut(BaseModel): # Pydantic-Schema für die Rückgabe von Nutzerdaten (ohne Passwort). # fehlt absichtlich, damit das Passwort nicht außen gesendet wird (Security-Best-Practice).
    username: str
    email: str
    otp_secret: Optional[str] = None # Gibt das Secret für den QR-Code einmalig zurück, damit der User alles in der Duo Mobile App einrichten kann.
    class Config:   # Erlaubt Pydantic, die Daten direkt aus dem SQLAlchemy-Objekt (Datenbank) zu lesen, auch wenn es kein reines Dictionary ist.
        from_attributes = True

class Token(BaseModel): # Schema für die Rückgabe des OAuth2 Tokens.
    access_token: str # Der eigentliche JWT-String.
    token_type: str # ist immer ein bearer Token.

#  Flight Schemas
class FlightBase(BaseModel): # Pydantic-Schema für die Datenstruktur der Flugdaten. Wird für GET-Antworten verwendet. Erbt von Basemodel!
                             # stellt sicher, dass alle Daten, die in die API eingehen den richtigen Datentyp haben (Validierung)
                             # generiert automatisch die Dokumentation (Swagger/OpenAPI) und legt fest welche Felder bei einer Abfrage zurückgegeben werden!
    flight_id: str   # Darf nicht leer sein! 
    airline_id: Optional[str] = None # --> None = kann leerer Wert sein und ist optional für die Eingabe!
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

# Endpunkte
@app.post("/register", response_model=UserOut) # Endpunkt für die Registrierung neuer User.
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Domain-Prüfung für die E-Mail --> groß / klein schreibung ist egal --> .lower()
    if not user.email.lower().endswith("@flughafenabc"):
        raise HTTPException(status_code=400, detail="Registrierung nur mit @FlughafenABC E-Mail erlaubt!")  
    # Prüfen ob User bereits existiert
    if db.query(User).filter(User.username == user.username).first(): # Hier hätte man auch den Primary Key auf den Username setzen können. --> Macht man aber eigenlich nicht da es ja sein könnte, dass man den username ändern möchte... auch wenn ich das nicht implementiert habe...
        raise HTTPException(status_code=400, detail="Username bereits vergeben")
    
    # 2FA Secret generieren (Duo Mobile TOTP)
    otp_secret = pyotp.random_base32() # Dieses Secret wird später im Dashboard als QR-Code angezeigt und mit Duo Mobile gescannt.
    
    # Passwort hashen und User anlegen
    hashed_pwd = pwd_context.hash(user.password) # Hashing des Passworts mit Bcrypt. --> bedeutet nur verschlüselt gespeichert wird. --> Sicherheit
    new_user = User(
        username=user.username, 
        email=user.email, 
        hashed_password=hashed_pwd,
        otp_secret=otp_secret # Speichert das Secret für Duo Mobile.
    )
    db.add(new_user) # Das neue User-Objekt wird für die Datenbank vorgemerkt.
    db.commit() # db.commit() schreibt die Daten permanent in die PostgreSQL-Tabelle.
    db.refresh(new_user) # Lädt die von der Datenbank generierte ID (Auto-Increment) zurück in das Objekt.
    return new_user

@app.post("/login", response_model=Token) # Endpunkt für Login mit OAuth2 und Duo Mobile (TOTP).
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    # User suchen. --> # .first() gibt das User-Objekt zurück oder 'None', falls der Name nicht existiert.
    user = db.query(User).filter(User.username == user_data.username).first()
    
    # Passwort-Check --> # pwd_context.verify vergleicht das eingegebene Klartext-Passwort mit dem Bcrypt-Hash aus der DB.
    if not user or not pwd_context.verify(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Ungültiger Username oder Passwort") # generischer Fehler. Best practice, so weiß niemand ob der Username oder das Passwort falsch war.
    
    # Zwei-Faktor-Check (Duo Mobile Code wird erzwungen)
    if user.otp_secret:
        if not user_data.otp_code: # Falls Name/Passwort korrekt, aber das Feld für den Duo-Code leer ist
            raise HTTPException(status_code=401, detail="Duo Code benötigt!")
        
        totp = pyotp.TOTP(user.otp_secret)  # initialisieren des TOTP (Time-based One-Time Password) mit dem gespeicherten Secret.
        if not totp.verify(user_data.otp_code): # totp.verify prüft, ob der vom User eingegebene 6-stellige Code mit dem aktuell gültigen Code übereinstimmt.
            raise HTTPException(status_code=401, detail="  Falscher Duo-Code!") # Fehler, wenn der Code nicht stimmt.

    # 3. OAuth2 Token erstellen
    access_token = create_access_token(data={"sub": user.username}) # Wenn beide Faktoren (Passwort + Duo) korrekt sind, wird ein JWT-Token erstellt.
    return {"access_token": access_token, "token_type": "bearer"} # Gibt den Token zurück. Das Dashboard speichert diesen im "session_state". --> erkläre ich im dashboard.py-code :)

@app.get("/flights/{flight_id}", response_model=FlightBase) # Definiert einen GET-Endpunkt zum Abrufen eines einzelnen Fluges anhand seiner ID.
def get_flight(flight_id: str, db: Session = Depends(get_db)): # Nimmt flight_id aus der URL und die DB-Session über Dependency Injection entgegen.
    f = db.query(Flight).filter(Flight.flight_id == flight_id).first() # Führt die Datenbankabfrage durch (suche nach Primary Key).
    if not f: raise HTTPException(404,"Flug nicht gefunden") # Falls kein Flug gefunden wird, wird der HTTP-Fehler 404 zurückgegeben.
    return f # Gibt das gefundene Flight-Objekt zurück.

@app.post("/flights/search", response_model=List[FlightBase]) # Definiert einen POST-Endpunkt für komplexe Suchanfragen. Gibt eine Liste von Flügen zurück.
def search_flights(s: FlightSearch, db: Session = Depends(get_db)): # Nimmt das FlightSearch-Schema (Suchkriterien) und die DB-Session entgegen.
    q = db.query(Flight) # Beginnt die Datenbankabfrage auf das Flight-Modell.
    if s.airline: q = q.filter(Flight.airline_id==s.airline) # Fügt einen Filter hinzu, wenn das Suchkriterium "airline" vorhanden ist.
    if s.origin: q = q.filter(Flight.origin==s.origin) # Fügt einen Filter hinzu, wenn das Suchkriterium "origin" vorhanden ist.
    if s.destination: q = q.filter(Flight.destination==s.destination) # Fügt einen Filter hinzu, wenn das Suchkriterium "destination" vorhanden ist.
    if s.weekday: q = q.filter(Flight.weekday==s.weekday) # Fügt einen Filter hinzu, wenn das Suchkriterium "weekday" vorhanden ist.
    return q.all() # Führt die endgültige Abfrage aus und gibt alle passenden Ergebnisse zurück.

@app.post("/flights/add", response_model=FlightBase) # Definiert einen POST-Endpunkt zum Hinzufügen eines neuen Flugdatensatzes.
def add_flight(f: FlightCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)): # Geschützt durch OAuth2 Token !!!!!! --> dieses ist 300 min gültig.
    if db.get(Flight, f.flight_id): # Prüft, ob ein Flug mit dieser flight_id bereits existiert (Duplikatprüfung). --> Primary Key nutzen! Empfehlung von Max :)
        raise HTTPException(400,"Flug mit dieser flight_id existiert bereits") # Gibt Fehler 400 zurück, falls der Flug bereits existiert.
    new = Flight(**f.dict()) # Erstellt ein neues SQLAlchemy Flight-Modell-Objekt aus den empfangenen Pydantic-Daten.
    db.add(new) # Markiert das neue Objekt für das Einfügen (Insertion) in die Datenbank.
    db.commit() #  db.commit!!!!!: Schreibt die vorgemerkte Änderung (den neuen Flug) permanent in die Datenbank.
    db.refresh(new) # Aktualisiert das Objekt, um Werte abzurufen, die von der DB generiert wurden (wichtig nach dem Commit).
    return new # Gibt das neu hinzugefügte Objekt zurück.

@app.delete("/flights/{flight_id}") # Definiert einen DELETE-Endpunkt zum Löschen eines Fluges anhand seiner ID.
def delete_flight(flight_id: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)): #  Geschützt durch OAuth2 Token!!! wie zuvor --> Mehr Sicherheit
    f = db.query(Flight).filter(Flight.flight_id==flight_id).first() # Sucht den zu löschenden Flug.
    if not f: raise HTTPException(404,"Flug nicht gefunden") # Fehler 404, wenn der Flug nicht existiert.
    db.delete(f) # Markiert das gefundene Objekt zum Löschen.
    db.commit() # db. commit!!! Führt die Löschung permanent in der Datenbank durch.
    return {"detail": f"Flug {flight_id} gelöscht"}