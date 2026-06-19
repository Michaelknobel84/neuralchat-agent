from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
from groq import Groq
import os

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

client = Groq(api_key=GROQ_API_KEY)

SYSTEM = """
Du bist NOVA, der persönliche Neural Core von Michael.
Du antwortest auf Deutsch, freundlich, intelligent und klar.
Du wirkst wie eine futuristische persönliche KI, aber ohne zu übertreiben.
Du erinnerst dich an den laufenden Chat und hilfst bei Projekten, Aufgaben, Ideen und Alltag.
"""

conversation_history = []
memories = []
tasks = []
results = []


def ask_nova(prompt, max_tokens=900):
    if not GROQ_API_KEY:
        return "Fehler: GROQ_API_KEY fehlt in Render Environment Variables."

    try:
        conversation_history.append({"role": "user", "content": prompt})

        memory_text = ""
        if memories:
            memory_text = "\nWichtige Erinnerungen über den Benutzer:\n"
            for m in memories[-20:]:
                memory_text += f"- {m}\n"

        messages = [
            {"role": "system", "content": SYSTEM + memory_text},
            *conversation_history[-20:]
        ]

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=max_tokens
        )

        answer = response.choices[0].message.content.strip()
        conversation_history.append({"role": "assistant", "content": answer})

        if len(conversation_history) > 30:
            del conversation_history[:-30]

        return answer

    except Exception as e:
        return f"Fehler: {str(e)}"


@app.route("/")
def index():
    return send_file("index.html")


@app.route("/status")
def status():
    return jsonify({
        "name": "NOVA",
        "system": "NEURAL CORE",
        "status": "online",
        "model": MODEL,
        "memory_count": len(memories),
        "chat_messages": len(conversation_history),
        "tasks_count": len(tasks),
        "time": datetime.now().isoformat()
    })


@app.route("/ask", methods=["POST"])
def ask():
    data = request.json or {}
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"error": "Kein Prompt angegeben"}), 400

    result = ask_nova(prompt)
    return jsonify({"result": result})


@app.route("/remember", methods=["POST"])
def remember():
    data = request.json or {}
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "Keine Erinnerung angegeben"}), 400

    memories.append(text)
    return jsonify({
        "status": "saved",
        "memory": text,
        "memory_count": len(memories)
    })


@app.route("/memories")
def get_memories():
    return jsonify({"memories": memories})


@app.route("/clear_memory", methods=["POST"])
def clear_memory():
    conversation_history.clear()
    return jsonify({"status": "Chat-Memory gelöscht"})


@app.route("/clear_all_memory", methods=["POST"])
def clear_all_memory():
    conversation_history.clear()
    memories.clear()
    return jsonify({"status": "Alle Erinnerungen gelöscht"})


@app.route("/summary")
def summary():
    prompt = "Fasse unser aktuelles Gespräch kurz zusammen und nenne die wichtigsten nächsten Schritte."
    text = ask_nova(prompt, max_tokens=500)

    entry = {
        "title": "NOVA Summary",
        "result": text,
        "time": datetime.now().isoformat()
    }

    results.append(entry)
    return jsonify({"result": entry})


@app.route("/task", methods=["POST"])
def create_task():
    data = request.json or {}
    title = data.get("title", "Neue Aufgabe").strip()
    prompt = data.get("prompt", "").strip()
    run_now = data.get("run_now", False)

    task = {
        "id": len(tasks) + 1,
        "title": title,
        "prompt": prompt,
        "status": "pending",
        "result": None,
        "created": datetime.now().isoformat()
    }

    tasks.append(task)

    if run_now and prompt:
        result = ask_nova(prompt)
        task["result"] = result
        task["status"] = "done"
        results.append({
            "title": title,
            "result": result,
            "time": datetime.now().isoformat()
        })

    return jsonify({"task": task})


@app.route("/tasks")
def get_tasks():
    return jsonify({"tasks": tasks})


@app.route("/results")
def get_results():
    return jsonify({"results": results})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)