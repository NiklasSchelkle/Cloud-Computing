# Basis-Image --> Python kann genutzt werden
FROM python:3.11-slim

# Arbeitsverzeichnis
# Erstellt den Ordner /app im Container und legt ihn als Standardpfad fest.
# Alle nachfolgenden Befehle (COPY, RUN) finden in diesem /app-Ordner statt.
WORKDIR /app 

# Abhängigkeiten kopieren
COPY requirements.txt .

# Pakete installieren
RUN pip install --no-cache-dir -r requirements.txt

# Quellcode kopieren
COPY . .

# Server starten 
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# 1. main:app: Zeigt auf die FastAPI-Instanz (im Modul main, Variable app).
# 2. --host 0.0.0.0 = Wer kann mich erreichen? (nötig, sagt alle aus meinem Netzwerk), port --> Hier erreichst du mich.
# 3. --port 8000: Legt den internen Port fest, auf dem die API im Container läuft.