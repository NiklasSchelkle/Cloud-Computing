FROM python:3.11-slim
WORKDIR /app

# Greift in den api-Ordner, um die requirements zu kopieren
COPY api/requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# Kopiert die restlichen Dateien aus dem Root (Abgabe)
COPY flights_clean.csv .
COPY .env .
COPY ingest.py .

CMD ["python", "ingest.py"]