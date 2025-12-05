import streamlit as st 
import pandas as pd 
import requests # Importiert Requests für HTTP-Anfragen an die FastAPI-API.

API_URL = "http://api:8000"  # Docker-Compose Service Name # Definiert die URL der API unter Verwendung des Docker Service Namens "api".

st.set_page_config(layout="wide", page_title="Flight Dashboard") 
st.title("✈️ Flights Dashboard") 

# Funktionen 
def search_flights(payload): # Definiert die Funktion zum Suchen von Flügen (POST-Anfrage).
    try: 
        r = requests.post(f"{API_URL}/flights/search", json=payload) # Sendet POST-Anfrage an den Such-Endpunkt der API.
        r.raise_for_status() # Löst bei HTTP-Fehlern (z.B. 404, 500) eine Exception aus.
        return r.json() # Gibt die JSON-Antwort (Liste der Flüge) zurück.
    except: # Fängt alle Fehler ab. --> ohne würde das Dashboard abstürzen. --> Daher try und except!
        return [] # Gibt eine leere Liste bei Fehler zurück.

def get_flight(flight_id): # Definiert die Funktion zum Abrufen eines einzelnen Fluges (GET-Anfrage).
    try: 
        r = requests.get(f"{API_URL}/flights/{flight_id}") # Sendet GET-Anfrage an den /flights/{id} Endpunkt.
        r.raise_for_status() # Überprüft auf HTTP-Fehler.
        return r.json() # Gibt die JSON-Antwort (den Flug) zurück.
    except: # Fängt alle Fehler ab.
        return None # Gibt None bei Fehler zurück.

def add_flight(payload): # Definiert die Funktion zum Hinzufügen eines Fluges (POST-Anfrage).
    try: # Beginnt den Fehlerbehandlungsblock.
        r = requests.post(f"{API_URL}/flights/add", json=payload) # Sendet POST-Anfrage zum Hinzufügen.
        r.raise_for_status() # Überprüft auf HTTP-Fehler.
        return r.json() # Gibt die JSON-Antwort (den hinzugefügten Flug) zurück.
    except: # Fängt alle Fehler ab.
        return None # Gibt None bei Fehler zurück.

def delete_flight(flight_id): # Definiert die Funktion zum Löschen eines Fluges (DELETE-Anfrage).
    try: # Beginnt den Fehlerbehandlungsblock.
        r = requests.delete(f"{API_URL}/flights/{flight_id}") # Sendet DELETE-Anfrage zum Löschen.
        r.raise_for_status() # Überprüft auf HTTP-Fehler.
        return r.json() # Gibt die JSON-Antwort (Bestätigung) zurück.
    except: # Fängt alle Fehler ab.
        return None # Gibt None bei Fehler zurück.

# Suche 
st.header("1️⃣ Flüge suchen") # Überschrift Suche
cols = st.columns(4) # Erstellt vier Spalten für die Eingabefelder.
airline = cols[0].text_input("Airline") # Erstellt ein Textfeld in Spalte 1 für die Airline-Eingabe.
origin = cols[1].text_input("Origin") # Erstellt ein Textfeld in Spalte 2 für die Origin-Eingabe.
destination = cols[2].text_input("Destination") # Erstellt ein Textfeld in Spalte 3 für die Destination-Eingabe.
weekday = cols[3].text_input("Weekday") # Erstellt ein Textfeld in Spalte 4 für die Wochentags-Eingabe.

if st.button("Suchen"): # Prüft, ob der "Suchen"-Button geklickt wurde.
    payload = {k:v if v else None for k,v in {"airline":airline,"origin":origin,"destination":destination,"weekday":weekday}.items()} # Erstellt das Such-Payload-Dictionary und setzt leere Strings auf None.
    results = search_flights(payload) # Ruft die Suchfunktion auf, um Ergebnisse von der API zu holen.
    if results: # Prüft, ob Ergebnisse zurückgegeben wurden.
        df = pd.DataFrame(results) # Erstellt ein Pandas DataFrame aus den JSON-Ergebnissen.
        st.dataframe(df) # Zeigt das DataFrame als interaktive Tabelle im Dashboard an.
        avg_delay = df['departure_delay'].dropna().mean() if 'departure_delay' in df else 0 # Berechnet die durchschnittliche Abflugverspätung (Ignoriert fehlende Werte).
        cancelled_pct = df['cancelled'].mean() if 'cancelled' in df else 0 # Berechnet den Anteil ausgefallener Flüge.
        st.write(f"Durchschnittliche Verspätung: {avg_delay:.2f} Minuten") # Zeigt die berechnete Durchschnittsverspätung an.
        st.write(f"Anteil ausgefallene Flüge: {cancelled_pct*100:.1f}%") # Zeigt den Prozentsatz der ausgefallenen Flüge an.
    else: # Falls keine Ergebnisse gefunden wurden.
        st.warning("Keine Ergebnisse") 

# Flug anzeigen 
st.header("2️⃣ Explizite Flugsuche") # Überschrift.
fid = st.text_input("Flight ID anzeigen") # Textfeld zur Eingabe der Flight ID.
if st.button("Anzeigen"): # Prüft, ob der "Anzeigen"-Button geklickt wurde.
    flight = get_flight(fid) # Ruft die Funktion zum Abrufen des Fluges auf.
    if flight: st.json(flight) # Zeigt den Flug als formatiertes JSON an, wenn er gefunden wurde.
    else: st.error("Flight nicht gefunden") # Zeigt eine Fehlermeldung an.


# Flug hinzufügen 
st.header("3️⃣ Flug hinzufügen")
new_id = st.text_input("Flight ID hinzufügen") # Erstellt das Textfeld für die Flight ID
cols_add = st.columns(2) # Definiert zwei Spalten 
airline_input = cols_add[0].text_input("Airline ID (optional)") # Textfeld in Spalte 1 (links).
scheduled_dep = cols_add[1].text_input("Scheduled Departure (YYYY-MM-DD HH:MM)") # Textfeld in Spalte 2 (rechts).
cancelled = st.checkbox("Cancelled") # Erstellt checkbox 

if st.button("Hinzufügen"): # Prüft, ob der "Hinzufügen"-Button geklickt wurde.
    # Payload-Dictionary erstellen: Sammelt alle eingegebenen Werte.
    # Setzt leere Strings von Streamlit-Inputs auf None für die API/Datenbank.
    payload = {
        "flight_id": new_id, 
        "cancelled": cancelled,
        "airline_id": airline_input if airline_input else None, 
        "scheduled_departure": scheduled_dep if scheduled_dep else None,
    } 
    res = add_flight(payload) # Ruft die Funktion zum Hinzufügen des Fluges auf (API-POST).
    if res: 
        st.success(f"Flug {new_id} erfolgreich hinzugefügt.") # Erfolgsmeldung.
    else: 
        st.error("Fehler beim Hinzufügen. (ID existiert oder Datumsformat falsch?)") # Fehlermeldung.

# Flug löschen 
st.header("4️⃣ Flug löschen") # Zeigt die Überschrift an.
del_id = st.text_input("Flight ID löschen") # Erstellt ein Textfeld zur Eingabe der zu löschenden Flight ID.
if st.button("Löschen"): # Prüft, ob der "Löschen"-Button geklickt wurde.
    res = delete_flight(del_id) # Ruft die Funktion zum Löschen des Fluges auf.
    if res: st.success(res.get("detail")) 
    else: st.error("Fehler beim Löschen") 

