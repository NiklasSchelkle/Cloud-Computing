"""
Streamlit Dashboard für die Flugverwaltung.

Dieser Code bildet das Frontend der Anwendung und ist verantwortlich für:
1. Benutzeroberfläche: Darstellung von Login, Registrierung und Flugdaten.
2. API-Kommunikation: Abfrage der FastAPI-Endpunkte mittels der "requests"-Bibliothek.
3. Sicherheit: Handhabung von OAuth2-Tokens und Darstellung von Duo Mobile QR-Codes (2FA).
4. Zustandsverwaltung: Nutzung von "st.session_state" zur Speicherung von Login-Status und Tokens.
"""

import streamlit as st # importiert Streamlit für die Web-App-Oberfläche.
import pandas as pd 
import requests # Importiert Requests für HTTP-Anfragen an die FastAPI-API.
import qrcode # Importiert die qrcode-Bibliothek zur Generierung von QR-Codes für die 2FA.
from io import BytesIO # Erlaubt das Speichern des QR-Bildes im Arbeitsspeicher.

API_URL = "http://api:8000"  # Docker-Compose Service Name # Definiert die URL der API unter Verwendung des Docker Service Namens "api".

# Konfiguration der Seite. --> breits layout und Titel
st.set_page_config(layout="wide", page_title="Flight Dashboard") 

# Session State für Login und Token initialisieren
if "logged_in" not in st.session_state: 
    st.session_state.logged_in = False # Setzt Standard auf "nicht eingeloggt".
    st.session_state.token = None

# Hilfsfunktion für geschützte Anfragen --> Token ist im Header
def get_auth_header():
    return {"Authorization": f"Bearer {st.session_state.token}"} # Fügt das Token als "Bearer" hinzu.

# Funktionen zur API-Kommunikation

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
        # NUTZT DEN OAUTH2 TOKEN IM HEADER!!! --> ist 300 min gültig
        r = requests.post(f"{API_URL}/flights/add", json=payload, headers=get_auth_header()) # Sendet POST-Anfrage zum Hinzufügen.
        r.raise_for_status() # Überprüft auf HTTP-Fehler.
        return r.json() # Gibt die JSON-Antwort (den hinzugefügten Flug) zurück.
    except: # Fängt alle Fehler ab.
        return None # Gibt None bei Fehler zurück.

def delete_flight(flight_id): # Definiert die Funktion zum Löschen eines Fluges (DELETE-Anfrage).
    try: # Beginnt den Fehlerbehandlungsblock.
        # NUTZT DEN OAUTH2 TOKEN IM HEADER!!! --> ist 300 min gültig
        r = requests.delete(f"{API_URL}/flights/{flight_id}", headers=get_auth_header()) # Sendet DELETE-Anfrage zum Löschen.
        r.raise_for_status() # Überprüft auf HTTP-Fehler.
        return r.json() # Gibt die JSON-Antwort (Bestätigung) zurück.
    except: # Fängt alle Fehler ab.
        return None # Gibt None bei Fehler zurück.

# Login und Registrierung
if not st.session_state.logged_in: # Falls der User nicht eingeloggt ist
    st.title("🔐 Login") # Titel der Login-Seite.
    tab1, tab2 = st.tabs(["Anmelden", "Registrieren"]) # Erstellt zwei Tabs: Anmelden und Registrieren.
    
    with tab1: # Bereich für den Login.
        u = st.text_input("Username") # Eingabefeld für den Benutzernamen.
        p = st.text_input("Passwort", type="password") # Eingabefeld für das Passwort.
        otp = st.text_input("Duo Mobile Code (6-stellig)") # Feld für den 2. Faktor hinzugefügt
        if st.button("Login"):
            # Sendet  Username, Passwort und den Duo-Code an die API
            res = requests.post(f"{API_URL}/login", json={"username":u, "password":p, "otp_code":otp})
            if res.status_code == 200: # --> Erfolgreicher Login
                st.session_state.token = res.json().get("access_token") # Speichert den OAuth2 Token
                st.session_state.logged_in = True # Status auf "eingeloggt" setzen.
               
                if "temp_secret" in st.session_state: del st.session_state.temp_secret # Entfernt temporäre QR-Daten, falls vorhanden. (QR-Code für Registrierung wird nicht mehr angezeigt)
                st.rerun() # Seite neu laden, um Dashboard anzuzeigen.
            else: st.error("Login fehlgeschlagen. Passwort oder Duo-Code falsch.")

    with tab2: # Bereich für die Registrierung.
        st.subheader("Registrierung nur möglich mit @FlughafenABC als Endung") 
        ru, re, rp = st.text_input("Wunsch-Username"), st.text_input("E-Mail"), st.text_input("Passwort ", type="password") # Feld für Username., E-Mail, Passwort
        if st.button("Konto erstellen"): # Bei Klick auf "Konto erstellen", wird alles an die API gesendet.
            res = requests.post(f"{API_URL}/register", json={"username":ru, "email":re, "password":rp})
            if res.status_code == 200: # Falls erfolgreich erstellt. 
                data = res.json()
                st.session_state.temp_secret = data.get("otp_secret") # Secret temporär für QR-Code merken. --> müsste im State sein.
                st.session_state.temp_user = ru # Usernamen merken.
                st.success("Erfolgreich! Scanne diesen QR-Code mit Duo Mobile:") 
            else: st.error("Fehler: E-Mail ungültig oder User existiert bereits.")
                

        # QR Code Logik (steht außerhalb des Buttons, damit sie beim Refresh bleibt)
        if "temp_secret" in st.session_state: # Wenn ein Secret vorhanden ist, also nach der Registrierung)
            st.divider() # Trennlinie zeichnen.
            secret = st.session_state.temp_secret # Secret aus State laden.
            user = st.session_state.temp_user # Usernamen aus State laden.
            otp_uri = f"otpauth://totp/FlughafenABC:{user}?secret={secret}&issuer=FlughafenABC" # OTP URI für Duo Mobile generieren. 
            
            img = qrcode.make(otp_uri) # Generiert das QR-Bild aus der URI.
            buf = BytesIO() # Erstellt Puffer im RAM.
            img.save(buf) # Speichert das Bild im Puffer.
            st.image(buf.getvalue(), caption=f"Duo Mobile QR-Code für {user}") # Zeigt QR-Code an.
            st.info(f"Manueller Key (falls Scannen nicht geht): {secret}") # Zeigt den manuellen Key an. 
            st.warning("Nach dem Scannen kannst du dich oben im Reiter 'Anmelden' einloggen.")
            
    st.stop() # Beendet das Skript hier, damit das Dashboard unten nicht geladen wird.

# Das eigentliche DASHBOARD nach dem Login
st.title("✈️ Flights Dashboard") # Titel des Dashboards.
if st.sidebar.button("Logout"): # Logout-Button in der Seitenleiste.
    st.session_state.logged_in = False # Wenn Logout dann, Login-Status zurücksetzen.
    st.session_state.token = None # Token entfernen.
    if "temp_secret" in st.session_state: del st.session_state.temp_secret # Entfernen temporärer QR-Daten, falls vorhanden.
    st.rerun() # Seite wird neu geladen --> es erscheint wieder die Login-Seite.

# Suche 
st.header("1️⃣ Flüge suchen") # Überschrift 
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
        st.dataframe(df) # Zeigt das Dashboard als interaktive Tabelle im Dashboard an.
        avg_delay = df['departure_delay'].dropna().mean() if 'departure_delay' in df else 0 # Berechnet die durchschnittliche Abflugverspätung.
        cancelled_pct = df['cancelled'].mean() if 'cancelled' in df else 0 # Berechnet den Anteil ausgefallener Flüge.
        st.write(f"Durchschnittliche Verspätung: {avg_delay:.2f} Minuten") # Zeigt die Durchschnittsverspätung an.
        st.write(f"Anteil ausgefallene Flüge: {cancelled_pct*100:.1f}%") # Zeigt den Prozentsatz an.
    else: # Falls keine Ergebnisse gefunden wurden.
        st.warning("Keine Ergebnisse") 

# Flug anzeigen 
st.header("2️⃣ Explizite Flugsuche") # Überschrift.
fid = st.text_input("Flight ID anzeigen") # Textfeld zur Eingabe der Flight ID.
if st.button("Anzeigen"): # Prüft, ob der "Anzeigen"-Button geklickt wurde.
    flight = get_flight(fid) # Ruft die Funktion zum Abrufen des Fluges auf.
    if flight: st.json(flight) # Zeigt den Flug als formatiertes JSON an.
    else: st.error("Flight nicht gefunden") # Zeigt eine Fehlermeldung an.

# Flug hinzufügen 
st.header("3️⃣ Flug hinzufügen")
new_id = st.text_input("Flight ID hinzufügen") # Erstellt das Textfeld für die Flight ID
cols_add = st.columns(2) # Definiert zwei Spalten 
airline_input = cols_add[0].text_input("Airline ID (optional)") # Textfeld in Spalte 1 (links).
scheduled_dep = cols_add[1].text_input("Scheduled Departure (YYYY-MM-DD HH:MM)") # Textfeld in Spalte 2 (rechts).
cancelled = st.checkbox("Cancelled") # Erstellt checkbox 

if st.button("Hinzufügen"): # Prüft, ob der "Hinzufügen"-Button geklickt wurde.
    payload = {
        "flight_id": new_id, 
        "cancelled": cancelled,
        "airline_id": airline_input if airline_input else None, 
        "scheduled_departure": scheduled_dep if scheduled_dep else None,
    } 
    res = add_flight(payload) # Ruft die Funktion zum Hinzufügen auf.
    if res: 
        st.success(f"Flug {new_id} erfolgreich hinzugefügt.") # Erfolgsmeldung.
    else: 
        st.error("Fehler beim Hinzufügen. (Berechtigung fehlt oder ID existiert?)") # Fehlermeldung.

# Flug löschen 
st.header("4️⃣ Flug löschen") # Zeigt die Überschrift an.
del_id = st.text_input("Flight ID löschen") # Erstellt ein Textfeld zur Eingabe der Flight ID.
if st.button("Löschen"): # Prüft, ob der "Löschen"-Button geklickt wurde.
    res = delete_flight(del_id) # Ruft die Funktion zum Löschen auf.
    if res: st.success("Flug erfolgreich gelöscht.") 
    else: st.error("Fehler beim Löschen (Berechtigung fehlt?)")


# Da das Skript bei jeder Benutzerinteraktion (z.B.  Texteingabe oder ein Button-Klick) vollständig von oben nach unten neu ausgeführt wird, würden normalerweise alle zuvor erhobenen Daten gelöscht werden. 
# Damit das nicht passiert habe ichden sogenannten Session State implementiert.

# Session State funktioniert so: Zu Beginn wird geprüft, ob bereits ein gültiger Anmeldestatus vorliegt. 
# Solange der Nutzer nicht authentifiziert ist, wird der Zugriff auf das eigentliche Dashboard durch den Befehl st.stop() blockiert. 
# Erst wenn der Nutzer im Login-Prozess sowohl sein korrektes Passwort als auch den zeitbasierten Duo Mobile Code (TOTP) eingibt, wird ein von der API generierter OAuth2-Token im Session State hinterlegt.
# Dieser Token dient dann als digitaler Ausweis und wird beim Hinzufügen oder Löschen von Flügen, im HTTP-Header mitgesendet, um die Autorisierung gegenüber der FastAPI sicherzustellen.

# Daneben wird session State auch für die Registrierung genutzt.
# Sobald ein  ein neues Konto erstellt wird, generiert das Backend ein einmaliges(Secret).
# Damit dieses Secret nicht durch den sofortigen Rerender von Streamlit verloren geht, wird es temporär im Session State zwischengespeichert. 
# Dies erlaubt es dem Dashboard, stabil einen QR-Code anzuzeigen, den der Mitarbeiter in aller Ruhe mit seiner Duo Mobile App scannen kann. 
# Durch eine Logout-Logik wird das ganze dann wieder aus dem session state gelöscht. Es ist also nur solange gespeichert, bis der  nutzer sich ausloggt oder die Seite neu lädt. """