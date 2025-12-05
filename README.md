# ✈️ Flight Dashboard (Streamlit & FastAPI Microservice Frontend)

Dieses Projekt ist das **Frontend (Dashboard)** für ein Microservice-System, das Flugdaten verwaltet und analysiert. Es basiert auf Streamlit und kommuniziert über HTTP-Anfragen mit einer separaten **FastAPI-API** (dem Backend-Service).

Das Dashboard ermöglicht Benutzern die interaktive Suche, Anzeige, das Hinzufügen und das Löschen von Flugdatensätzen.

---

## 🎯 Architektur

Die Anwendung besteht aus mindestens zwei Komponenten, die idealerweise in einer **Docker Compose**-Umgebung ausgeführt werden:

1.  **Dashboard (Streamlit):** Das Frontend, das die Benutzeroberfläche bereitstellt und alle Anfragen an die API sendet.
2.  **API (FastAPI):** Der Backend-Service, der die Geschäftslogik (Suche, Speichern, Löschen) verarbeitet und die tatsächliche Datenquelle (z.B. eine Datenbank) verwaltet.

### Wichtiger Hinweis zur Verbindung

Die Verbindung zur API verwendet den **Docker Service Name** `http://api:8000`. Dies funktioniert nur, wenn das Dashboard und die API im selben Docker-Netzwerk laufen und die API den Service-Namen `api` hat.

```python
API_URL = "http://api:8000"  # Docker-Compose Service Name

✨ Funktionen des Dashboards

Das Dashboard bietet vier Hauptbereiche zur Interaktion mit den Flugdaten:
1. Flüge suchen (/flights/search)

    Funktion: Ermöglicht die Suche nach Flügen anhand mehrerer Kriterien (Airline, Origin, Destination, Wochentag).

    Analyse: Zeigt die Ergebnisse in einem interaktiven DataFrame an und berechnet wichtige Metriken (Durchschnittliche Abflugverspätung und Anteil ausgefallener Flüge).

    API-Methode: POST an /flights/search

2. Explizite Flugsuche (/flights/{flight_id})

    Funktion: Ruft die vollständigen Details eines einzelnen Flugdatensatzes anhand seiner eindeutigen Flight ID ab.

    Anzeige: Zeigt die Rohdaten des Fluges als formatiertes JSON an.

    API-Methode: GET an /flights/{flight_id}

3. Flug hinzufügen (/flights/add)

    Funktion: Erlaubt das Hinzufügen neuer Flugdatensätze zur Datenbank.

    Eingaben: Erfordert die Flight ID sowie optional Airline ID, Scheduled Departure und den Status Cancelled.

    API-Methode: POST an /flights/add

4. Flug löschen (/flights/{flight_id})

    Funktion: Entfernt einen Datensatz dauerhaft aus der Datenbank unter Angabe der Flight ID.

    API-Methode: DELETE an /flights/{flight_id}

🛠️ Einrichten und Starten
Voraussetzungen

    Python (3.8+)

    Docker (Empfohlen für die Microservice-Architektur)

    FastAPI-Backend: Ein laufender FastAPI-Service, der die Endpunkte /flights/search, /flights/{flight_id}, /flights/add und /flights/{flight_id} (DELETE) bereitstellt.

Installation der Abhängigkeiten

Installieren Sie die Python-Bibliotheken für das Streamlit-Frontend:
Bash

pip install streamlit pandas requests

Starten der Anwendung

Da diese Anwendung auf eine separate API zugreift, muss die API zuerst gestartet werden (z.B. über Docker Compose).

Wenn das FastAPI-Backend unter dem Service-Namen api auf Port 8000 läuft:

    Frontend starten:
    Bash

streamlit run [DATEINAME_DES_SKRIPTS].py
