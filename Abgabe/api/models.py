"""Datenbank-Modell für die Flugdatenbank.

Diese Datei definiert die Struktur der "flights"-Tabelle, die von SQLAlchemy verwendet wird.
Sie erbt von der "Base"-Klasse aus database.py und legt die Spaltennamen, -typen
und Schlüsseleigenschaften fest (z.B. flight_id als Primary Key)."""

from sqlalchemy import Column, String, Float, Boolean, TIMESTAMP, Integer, Index
from database import Base

class Flight(Base): # Importiert die Base-Klasse. Alle Datenmodelle müssen von dieser Klasse erben, damit SQLAlchemy sie erkennt und die Tabelle in der Datenbank erstellen kann.
                    # alle Eigenschaften und Fähigkeiten von Base werden übernommen. So funktioniert die Datenbank-Funktionalität von SQLAlchemy in meinem Python-Modell
    __tablename__ = "flights" # Weist die Klasse der physischen Datenbanktabelle mit dem Namen "flights" zu.
    __table_args__ = ( # spezielle Indizes zur Leistungssteigerung.habe ich unten erklärt! --> Man umgeht damit einen Full Table scan!
        Index("idx_airline", "airline"),
        Index("idx_origin", "origin"),
        Index("idx_destination", "destination"),
        Index("idx_weekday", "weekday"),
        Index("idx_flight_id","flight_id"),
    )

    flight_id = Column(String, primary_key=True)  # Wichtig --> Definiert die Spalte flight_id als eindeutigen Primärschlüssel (Primary Key).
    # --> kennzeichnet jede Zeile EINDEUTUTIG --> schnellste Möglichkeit einen Flug zu finden! erstellt automatisch einen Index auf diese Spalte --> schnelle Suche!
    airline_id = Column(String, nullable=True) # Der Rest ist die Simple definition der Spalten mit ihren Datentypen. nullable = TRUE bedeutet, dass das Feld leer sein darf.
    airline = Column(String, nullable=True)    # Wichtig ist aber, dass die Spalten und die Datentypen exakt zur CSV passen!!!!!
    aircraft_id = Column(String, nullable=True)
    scheduled_departure = Column(TIMESTAMP, nullable=True)
    departure = Column(TIMESTAMP, nullable=True)
    departure_delay = Column(Float, nullable=True)
    scheduled_arrival = Column(TIMESTAMP, nullable=True)
    arrival = Column(TIMESTAMP, nullable=True)
    arrival_delay = Column(Float, nullable=True)
    air_time = Column(Float, nullable=True)
    distance = Column(Float, nullable=True)
    manufacturer = Column(String, nullable=True)
    model = Column(String, nullable=True)
    year = Column(Float, nullable=True)
    engines = Column(Float, nullable=True)
    seats = Column(Float, nullable=True)
    max_weight_pounds = Column(String, nullable=True)
    origin = Column(String, nullable=True)
    name_origin = Column(String, nullable=True)
    latitude_origin = Column(Float, nullable=True)
    longitude_origin = Column(Float, nullable=True)
    destination = Column(String, nullable=True)
    name_destination = Column(String, nullable=True)
    latitude_destination = Column(Float, nullable=True)
    longitude_destination = Column(Float, nullable=True)
    weekday = Column(String, nullable=True)
    hour = Column(Integer, nullable=True)
    cancelled = Column(Boolean, nullable=True)

class User(Base): # Definiert die User-Klasse, die von 'Base' erbt. --> SQLAlchemy erkennt diese Klasse als Datenbankmodell.
    __tablename__ = "users" # Name der physischen Tabelle in der PostgreSQL-Datenbank

    id = Column(Integer, primary_key=True, index=True) # Definiert eine automatische ID als Primärschlüssel. "index=True" sorgt für eine extrem schnelle Identifizierung des Datensatzes.
    username = Column(String, unique=True, index=True, nullable=False) # Speichert den Nutzernamen. "unique=True" verhindert doppelte Accounts, "nullable=False" macht es zum Pflichtfeld.
    email = Column(String, unique=True, index=True, nullable=False) # E-Mail-Adresse mit denselben Einschränkungen wie der Nutzername.
    hashed_password = Column(String, nullable=False) # Speichert das Passwort. Aber eben nur das gehashte Passwort, um Sicherheit zu gewährleisten. --> best Practice
    otp_secret = Column(String, nullable=True) # Spalte für das "Shared Secret", wird beim Scannen des QR-Codes an das Handy übertragen.  "nullable=True" erlaubt es, Nutzer erst anzulegen und das Secret danach zu generieren.


"""
Was die Flight-Klasse von Base erbt:

    Metadaten-Verwaltung: Die Fähigkeit, Tabellennamen (__tablename__) und Spaltendefinitionen zu sammeln und sie in das SQL-Schema zu übersetzen.

    Tabellenerstellung: Die notwendige Funktionalität, um später mit Base.metadata.create_all() die Tabelle tatsächlich in der PostgreSQL-Datenbank zu erstellen.

    ORM-Fähigkeit:  mit der SQLAlchemy Python-Objekte (Flight) in Datenbankzeilen umwandelt und umgekehrt."""

"""

Das Problem ohne Indizes 

Ohne Indizes auf den Suchspalten (POST-Endpunktes) muss ein Full Table Scan durchgeführt werden.

Die Datenbank musste also jede einzelne der über 246.000 Zeilen nacheinander lesen und prüfen, ob die Bedingung zutrifft. --> Langsam

Die Lösung mit Indizes (Index Scan)

Die Indizes funktionieren wie das Inhaltsverzeichnis eines Buches:

Implementierung: Die Zeilen Index('idx_...') weisen PostgreSQL an, eine separate, optimierte Struktur für die Werte in diesen Spalten zu erstellen. 
Diese Struktur ist intern vorsortiert und speichert die genaue Position der zugehörigen Datenzeilen.

Abfrage: Wenn Sman nun im POST-Endpunkt sucht, weiß die Datenbank sofort, wo die gesuchten Daten liegen. Sie muss nicht die gesamte Tabelle durchlesen.

Auswirkung: Die Suchzeit reduziert sich von vielen Sekunden auf wenige Millisekunden, da der Server direkt zu den relevanten Datensätzen springen kann.

"""