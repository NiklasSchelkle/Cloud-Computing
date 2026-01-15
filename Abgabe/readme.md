# Flughafen-Management Dashboard (Cloud Computing)

Dieses Projekt umfasst ein vollständiges Dashboard zur Verwaltung von Flugdaten, inklusive einer gesicherten API, einer PostgreSQL-Datenbank und einer Zwei-Faktor-Authentifizierung (2FA).

---

## Schnellstart (Deployment)

Um das Projekt in einer sauberen Umgebung zu starten, folgen Sie diesen Schritten:

### flights_clean unzippen und die csv in den root Ordner legen. 

### Repo kopieren:
```bash
git clone https://github.com/NiklasSchelkle/Cloud-Computing.git
```

# In den Ordner navigieren
```bash
cd "hier Pfad einfügen"
```
# Docker Compose starten
```bash
docker-compose up --build
```

Wichtiger Hinweis zum Startprozess (Race Condition):
Da die PostgreSQL-Datenbank beim ersten Start Zeit zur Initialisierung benötigt, kann es vorkommen, dass die API (flights_api) vorzeitig abbricht, weil die Datenbank noch keine Verbindungen annimmt.

Sollte die API den Status exited with code 1 zeigen, starten Sie diese bitte manuell neu, sobald die Datenbank bereit ist. Ist mir ein paar Mal passiert, obwohl in der Compose eigentlich definiert wurde, dass die API warten muss...
```bash
docker-compose start api
```
Oder einfach in Docker auf den Playbutton neben flights_api klicken.

Dann Dashboard aufrufen:
Öffnen Sie im Browser: http://localhost:8501

# Authentifizierung & Sicherheit

Das System nutzt eine Multi-Faktor-Authentifizierung (MFA) sowie OAuth2-Tokens.
Registrierung & Login

E-Mail-Validierung:
Eine Registrierung ist nur mit einer E-Mail-Adresse mit der Endung @FlughafenABC möglich.
(Es ist natürlich egal, ob man diese Mail tatsächlich besitzt)

2FA-Einrichtung:
Nach der Registrierung wird ein QR-Code angezeigt. Dieser muss mit der Duo Mobile App (oder einer vergleichbaren TOTP-App) gescannt werden.

Login:
Für den Login werden Username, Passwort und der aktuelle 6-stellige Code aus der App benötigt.

# Probleme
Time-Drift Problematik:
Der zweite Faktor (TOTP) ist extrem zeitkritisch. Während des Testens habe ich festgestellt, dass es manchmal nicht klappt, obwohl alles richtig ist.
Der Grund dafür sind Sekundenunterschiede zwischen dem Host-System (PC) und dem mobilen Endgerät (Handy). Dies kann dazu führen, dass der Login mit 401 Unauthorized abgelehnt wird. Oft habe ich die Seite http://localhost:8501 einfach refreshed und es zu unterschiedlichen Zeitpunkten probiert. Nach ein paar Versuchen hat es dann immer geklappt.

Datenbank-Resets:
Bei einem Löschen der Docker-Volumes (-v) werden alle Benutzerdaten entfernt.
In diesem Fall muss der alte Account in der Duo Mobile App gelöscht und ein neuer QR-Code gescannt werden, da die geheimen Schlüssel (Secrets) bei jeder Registrierung neu generiert werden.

# Technische Komponenten

Frontend: Streamlit (Zustandsverwaltung via session_state)

Backend: FastAPI (Python)

Datenbank: PostgreSQL

Sicherheit: Passlib (Hashing), PyJWT (Tokens), OTP (MFA)



