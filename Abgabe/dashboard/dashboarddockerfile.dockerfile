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

# Streamlit starten
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
#  wird ausgeführt, wenn der Container gestartet wird.
# 1. Ruft Streamlit auf.
# 2. Führt die app.py aus.
# 3. Stellt sicher, dass die Anwendung auf allen Netzwerkschnittstellen (0.0.0.0 = Placeholder für alle) im Container erreichbar ist und intern auf Port 8501 lauscht.