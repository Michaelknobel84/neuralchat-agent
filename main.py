# ============================================
# NeuralChat Agent - KI-Agent mit Scheduling
# Läuft 24/7 auf Render.com (kostenlos)
# ============================================

from flask import Flask, request, jsonify
import requests
import schedule
import threading
import time
import json
from datetime import datetime

app = Flask(__name__)

# ============================================
# KONFIGURATION — hier anpassen
# ============================================
CONFIG = {
    "model": "mistralai/Mistral-7B-Instruct-v0.3",
    "hf_api_url": "https://api-inference.huggingface.co/models/",
    "hf_token": "",  # Optional: HF Token für mehr Requests
    "webhook_url": "",  # Optional: Discord/Slack Webhook URL
    "language": "Deutsch",
}

# Aufgaben-Speicher (im RAM, wird bei Neustart geleert)
tasks = []
results = []

# ============================================
# KI-FUNKTION
# ============================================
def ask_ai(prompt, system="Du bist ein hilfreicher Assistent. Antworte auf Deutsch."):
    headers = {"Content-Type": "application/json"}
    if CONFIG["hf_token"]:
        headers["Authorization"] = f"Bearer {CONFIG['hf_token']}"

    full_prompt = f"<|system|>\n{system}</s>\n<|user|>\n{prompt}</s>\n<|assistant|>\n"

    try:
        res = requests.post(
            CONFIG["hf_api_url"] + CONFIG["model"],
            headers=headers,
            json={
                "inputs": full_prompt,
                "parameters": {
                    "max_new_tokens": 400,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            },
            timeout=30
        )
        data = res.json()
        if isinstance(data, list) and data[0].get("generated_text"):
            return data[0]["generated_text"].strip()
        return f"Fehler: {data.get('error', 'Unbekannt')}"
    except Exception as e:
        return f"Verbindungsfehler: {str(e)}"

# ============================================
# WEBHOOK (optional: Discord/Slack)
# ============================================
def send_webhook(message):
    if not CONFIG["webhook_url"]:
        return
    try:
        requests.post(CONFIG["webhook_url"], json={"content": message}, timeout=10)
    except:
        pass

# ============================================
# GEPLANTE AUFGABEN
# ============================================
def daily_summary():
    print(f"[{datetime.now()}] Tages-Zusammenfassung wird erstellt...")
    prompt = f"""Erstelle eine motivierende Tages-Zusammenfassung für heute, {datetime.now().strftime('%A, %d.%m.%Y')}.
    Enthalte: 1) Einen motivierenden Satz, 2) 3 produktive Aufgaben-Vorschläge, 3) Ein Tipp für den Tag."""

    result = ask_ai(prompt)
    entry = {
        "type": "daily_summary",
        "time": datetime.now().isoformat(),
        "result": result
    }
    results.append(entry)
    send_webhook(f"🌅 **Tages-Zusammenfassung**\n{result}")
    print(f"Zusammenfassung erstellt: {result[:100]}...")

def hourly_check():
    print(f"[{datetime.now()}] Stündlicher Check...")
    # Bearbeite ausstehende Tasks
    for task in tasks:
        if task["status"] == "pending":
            print(f"Bearbeite Task: {task['title']}")
            result = ask_ai(task["prompt"])
            task["status"] = "done"
            task["result"] = result
            task["completed_at"] = datetime.now().isoformat()
            results.append({
                "type": "task_result",
                "task_id": task["id"],
                "title": task["title"],
                "time": datetime.now().isoformat(),
                "result": result
            })
            send_webhook(f"✅ **Task erledigt: {task['title']}**\n{result[:300]}")

# Zeitplan registrieren
schedule.every().day.at("07:00").do(daily_summary)
schedule.every().hour.do(hourly_check)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

# Scheduler in Hintergrund-Thread starten
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

# ============================================
# API ENDPOINTS
# ============================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "agent": "NeuralChat Agent",
        "version": "1.0.0",
        "time": datetime.now().isoformat(),
        "tasks_count": len(tasks),
        "results_count": len(results)
    })

@app.route("/ask", methods=["POST"])
def ask():
    """Sofortige KI-Anfrage"""
    data = request.json
    prompt = data.get("prompt", "")
    system = data.get("system", "Du bist ein hilfreicher Assistent. Antworte auf Deutsch.")

    if not prompt:
        return jsonify({"error": "Kein Prompt angegeben"}), 400

    result = ask_ai(prompt, system)
    return jsonify({
        "prompt": prompt,
        "result": result,
        "time": datetime.now().isoformat(),
        "model": CONFIG["model"]
    })

@app.route("/task", methods=["POST"])
def create_task():
    """Neue geplante Aufgabe erstellen"""
    data = request.json
    task = {
        "id": len(tasks) + 1,
        "title": data.get("title", "Aufgabe"),
        "prompt": data.get("prompt", ""),
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "result": None,
        "completed_at": None
    }
    tasks.append(task)

    # Sofort ausführen wenn gewünscht
    if data.get("run_now", False):
        result = ask_ai(task["prompt"])
        task["status"] = "done"
        task["result"] = result
        task["completed_at"] = datetime.now().isoformat()

    return jsonify({"message": "Task erstellt", "task": task})

@app.route("/tasks", methods=["GET"])
def get_tasks():
    """Alle Tasks anzeigen"""
    return jsonify({"tasks": tasks, "count": len(tasks)})

@app.route("/results", methods=["GET"])
def get_results():
    """Alle Ergebnisse anzeigen"""
    return jsonify({"results": results[-20:], "count": len(results)})

@app.route("/summary", methods=["GET"])
def trigger_summary():
    """Tages-Zusammenfassung sofort auslösen"""
    daily_summary()
    latest = next((r for r in reversed(results) if r["type"] == "daily_summary"), None)
    return jsonify({"message": "Zusammenfassung erstellt", "result": latest})

@app.route("/config", methods=["POST"])
def update_config():
    """Konfiguration aktualisieren"""
    data = request.json
    if "webhook_url" in data:
        CONFIG["webhook_url"] = data["webhook_url"]
    if "hf_token" in data:
        CONFIG["hf_token"] = data["hf_token"]
    if "model" in data:
        CONFIG["model"] = data["model"]
    return jsonify({"message": "Konfiguration aktualisiert", "config": {k:v for k,v in CONFIG.items() if k != "hf_token"}})

# ============================================
# START
# ============================================
if __name__ == "__main__":
    print("NeuralChat Agent gestartet!")
    print(f"Modell: {CONFIG['model']}")
    print("Geplante Jobs: Täglich 07:00 + Stündlich")
    app.run(host="0.0.0.0", port=8080, debug=False)
