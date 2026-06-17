from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
from groq import Groq
import os

app = Flask(__name__)
CORS(app)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama3-8b-8192"  # ALT - löschen
MODEL = "llama-3.3-70b-versatile"

SYSTEM = "Du bist ein persönlicher KI-Assistent. Antworte immer auf Deutsch, klar, freundlich und präzise."

tasks = []
results = []

def ask_groq(prompt, max_tokens=700):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Fehler: {str(e)}"

@app.route("/")
def index():
    return send_file("index.html")

@app.route("/status")
def status():
    return jsonify({
        "agent": "NeuralChat Agent",
        "status": "online",
        "tasks_count": len(tasks),
        "results_count": len(results),
        "time": datetime.now().isoformat(),
        "version": "3.0.0",
        "model": MODEL
    })

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json or {}
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "Kein Prompt angegeben"}), 400
    result = ask_groq(prompt)
    return jsonify({"result": result})

@app.route("/summary")
def summary():
    prompt = f"Erstelle eine motivierende Tages-Zusammenfassung für heute, {datetime.now().strftime('%A, %d. %B %Y')}. Gib 3 konkrete Tipps für einen produktiven Tag."
    text = ask_groq(prompt, max_tokens=500)
    entry = {
        "title": "Tages-Zusammenfassung",
        "result": text,
        "time": datetime.now().isoformat()
    }
    results.append(entry)
    return jsonify({"result": entry})

@app.route("/task", methods=["POST"])
def create_task():
    data = request.json or {}
    title = data.get("title", "Task")
    prompt = data.get("prompt", "")
    run_now = data.get("run_now", False)
    task = {"id": len(tasks)+1, "title": title, "prompt": prompt, "status": "pending", "result": None}
    tasks.append(task)
    if run_now and prompt:
        text = ask_groq(prompt)
        task["result"] = text
        task["status"] = "done"
        results.append({"title": title, "result": text, "time": datetime.now().isoformat()})
    return jsonify({"task": task})

@app.route("/results")
def get_results():
    return jsonify({"results": results})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
