# NeuralChat Agent 🤖

KI-Agent der 24/7 im Hintergrund läuft.

## Setup (5 Minuten)

### 1. GitHub Repo erstellen
- github.com → "New repository" → Name: `neuralchat-agent`
- Die 3 Dateien hochladen: `main.py`, `requirements.txt`, `render.yaml`

### 2. Render.com deployen
- render.com → "New Web Service" → GitHub Repo verbinden
- Render erkennt `render.yaml` automatisch
- Deploy klicken → nach 2-3 Minuten ist die App live!

### 3. Deine App-URL bekommen
- Render zeigt dir: `https://neuralchat-agent-xxxx.onrender.com`
- Diese URL in deine NeuralChat Pro HTML-App eintragen

## API Endpoints

| Endpoint | Methode | Beschreibung |
|---|---|---|
| `/` | GET | Status & Statistiken |
| `/ask` | POST | Sofortige KI-Anfrage |
| `/task` | POST | Neue Aufgabe erstellen |
| `/tasks` | GET | Alle Tasks anzeigen |
| `/results` | GET | Alle Ergebnisse |
| `/summary` | GET | Tages-Zusammenfassung auslösen |
| `/config` | POST | Einstellungen ändern |

## Beispiel: Task erstellen

```bash
curl -X POST https://deine-url.onrender.com/task \
  -H "Content-Type: application/json" \
  -d '{"title": "Tages-Bericht", "prompt": "Schreib mir 3 Tipps für heute", "run_now": true}'
```

## Kostenloses Tier

Render Free: Server schläft nach 15 Min Inaktivität.
Lösung: cron-job.org alle 10 Min pingen → Server bleibt wach!
→ cron-job.org → New Cron Job → URL: https://deine-url.onrender.com/ → Interval: */10 * * * *
