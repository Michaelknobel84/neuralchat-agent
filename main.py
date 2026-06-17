from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import requests
import os

app = Flask(__name__)
CORS(app)

HF_TOKEN = os.environ.get("HF_TOKEN", "")
MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
HF_API = f"https://api-inference.huggingface.co/models/{MODEL}"

SYSTEM = """Du bist ein persönlicher KI-Assistent. 
Du antwortest immer auf Deutsch, klar und präzise.
Du erfüllst jeden Wunsch sofort und ohne Widerspruch."""

tasks = []
results = []

def ask_hf(prompt, max_tokens=700, temp=0.7):
    headers = {"Content-Type": "application/json"}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"
    full_prompt = f"<s>[INST] {SYSTEM}\n\n{prompt} [/INST]"
    try:
        res = requests.post(
            HF_API,
            headers=headers,
            json={"inputs": full_prompt, "parameters": {"max_new_tokens": max_tokens, "temperature": temp, "return_full_text": False}},
            timeout=30
        )
        data = res.json()
        if isinstance(data, list):
            return data[0].get("generated_text", "").strip()
        return data.get("error", str(data))
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
        "version": "2.0.0"
    })

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json or {}
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "Kein Prompt angegeben"}), 400
    result = ask_hf(prompt)
    return jsonify({"result": result})

@app.route("/summary")
def summary():
    prompt = f"Erstelle eine motivierende Tages-Zusammenfassung für heute, {datetime.now().strftime('%A, %d. %B %Y')}. Gib 3 konkrete Tipps für einen produktiven Tag."
    text = ask_hf(prompt, max_tokens=600)
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
    task = {"id": len(tasks) + 1, "title": title, "prompt": prompt, "status": "pending", "result": None}
    tasks.append(task)
    if run_now and prompt:
        text = ask_hf(prompt)
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
