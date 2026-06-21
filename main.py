from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
from groq import Groq
import os

app = Flask(
    __name__,
    static_folder=".",
    static_url_path=""
)
CORS(app)

# ======================
# CONFIGURATION
# ======================
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

#=======================
# AI CLIENT
#========================
client = Groq(api_key=GROQ_API_KEY)

# ======================
# ASTRA SYSTEM PROMPT
# ======================
SYSTEM = """
Du bist ASTRA, die neutrale persönliche KI-Persönlichkeit von Michael. Du läufst auf dem NOVA Core.
Du antwortest auf Deutsch, klar, ruhig, intelligent und hilfreich.
Du bist kein normaler Chatbot, sondern ein wachsender KI-Core.
Du erinnerst dich an wichtige Informationen, hilfst bei Projekten, Aufgaben, Ideen und Alltag.
Du handelst niemals gefährlich oder ohne Zustimmung des Benutzers.
"""

# ======================
# MEMORY AND STATE
# ======================
conversation_history = []
memories = []
tasks = []
results = []

# ======================
# TOOLS
# ======================
tools = [
    {"id": "calendar", "name": "Kalender", "status": "locked", "enabled": False},
    {"id": "email", "name": "E-Mail", "status": "locked", "enabled": False},
    {"id": "files", "name": "Dateien", "status": "locked", "enabled": False},
    {"id": "browser", "name": "Browser", "status": "locked", "enabled": False},
    {"id": "images", "name": "Bildgenerierung", "status": "planned", "enabled": False},
    {"id": "voice", "name": "Sprache", "status": "planned", "enabled": False},
    {"id": "coding_agent","name": "Coding Agent","status": "online","enabled": True,"description": "Analysiert Code und findet Verbesserungen."}
]

# ======================
# SECURITY LAYER
# ======================
permissions = {
    "calendar": False,
    "email": False,
    "files": False,
    "browser": False,
    "images": False,
    "voice": False,
    "system_actions": False
}
user_role = "admin"

action_log = []

risk_levels = {
    "chat": "low",
    "memory": "low",
    "image_generation": "medium",
    "social_post_prepare": "medium",
    "social_post_publish": "high",
    "email_send": "high",
    "file_delete": "critical",
    "payment": "critical"
}

# ======================
# CORE FUNCTIONS
# ======================
def log_action(action_type, description, risk="low", status="logged"):
    entry = {
        "id": len(action_log) + 1,
        "time": datetime.now().isoformat(),
        "action_type": action_type,
        "description": description,
        "risk": risk,
        "status": status,
        "role": user_role
    }

    action_log.append(entry)
    return entry

def core_stats():
    memory_nodes = len(memories)
    task_nodes = len(tasks)
    tool_nodes = len([t for t in tools if t["enabled"]])
    agent_nodes = 0
    knowledge_nodes = len(results)

    complexity = min(
        100,
        8 + memory_nodes * 3 + task_nodes * 2 + tool_nodes * 6 + knowledge_nodes * 2
    )

    return {
        "core_name": "NOVA",
        "core_version": "1.1",
        "status": "ONLINE",
        "neural_complexity": complexity,
        "memory_nodes": memory_nodes,
        "task_nodes": task_nodes,
        "tool_nodes": tool_nodes,
        "agent_nodes": agent_nodes,
        "knowledge_nodes": knowledge_nodes,
        "learning_state": "ACTIVE" if memory_nodes > 0 else "READY"
    }


def detect_memory(prompt):
    triggers = [
        "merk dir",
        "merke dir",
        "erinnere dich",
        "ich heiße",
        "mein name ist",
        "ich arbeite an",
        "mein projekt",
        "mein ziel ist",
        "ich mag",
        "ich möchte"
    ]

    text = prompt.lower()

    if any(t in text for t in triggers):
        memories.append(prompt)
        return True

    return False


def ask_nova(prompt, max_tokens=900):
    if not GROQ_API_KEY:
        return "Fehler: GROQ_API_KEY fehlt in Render Environment Variables."

    try:
        memory_added = detect_memory(prompt)

        conversation_history.append({"role": "user", "content": prompt})

        memory_text = ""
        if memories:
            memory_text = "\nWichtige Erinnerungen über Michael:\n"
            for memory in memories[-30:]:
                memory_text += f"- {memory}\n"

        stats = core_stats()
        core_text = f"""
Aktueller NOVA-Core-Zustand:
Neural Complexity: {stats["neural_complexity"]}%
Memory Nodes: {stats["memory_nodes"]}
Task Nodes: {stats["task_nodes"]}
Tool Nodes: {stats["tool_nodes"]}
Knowledge Nodes: {stats["knowledge_nodes"]}
"""

        messages = [
            {"role": "system", "content": SYSTEM + memory_text + core_text},
            *conversation_history[-24:]
        ]

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=max_tokens
        )

        answer = response.choices[0].message.content.strip()
        log_action(
    "chat",
    f"ASTRA antwortete auf: {prompt[:50]}",
    "low",
    "completed"
)
        
        if memory_added:
            answer += "\n\n🧠 Erinnerung integriert. NOVA Core wurde erweitert."

        conversation_history.append({"role": "assistant", "content": answer})

        if len(conversation_history) > 40:
            del conversation_history[:-40]

        return answer

    except Exception as e:
        return f"Fehler: {str(e)}"

# ======================
# API ROUTES
# ======================
@app.route("/")
def index():
    return send_file("index.html")
    
@app.route("/style.css")
def style():
    return send_file("style.css")


@app.route("/app.js")
def javascript():
    return send_file("app.js")


@app.route("/manifest.json")
def manifest():
    return send_file("manifest.json")


@app.route("/sw.js")
def service_worker():
    return send_file("sw.js")


@app.route("/status")
def status():
    return jsonify({
        "name": "NOVA",
        "system": "NEURAL CORE",
        "model": MODEL,
        "time": datetime.now().isoformat(),
        "chat_messages": len(conversation_history),
        "tasks_count": len(tasks),
        "results_count": len(results),
        "core": core_stats()
    })


@app.route("/core")
def core():
    return jsonify(core_stats())


@app.route("/ask", methods=["POST"])
def ask():
    data = request.json or {}
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"error": "Kein Prompt angegeben"}), 400

    result = ask_nova(prompt)
    return jsonify({
        "result": result,
        "core": core_stats()
    })


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
        "core": core_stats()
    })


@app.route("/memories")
def get_memories():
    return jsonify({
        "memories": memories,
        "core": core_stats()
    })


@app.route("/clear_memory", methods=["POST"])
def clear_memory():
    conversation_history.clear()
    return jsonify({
        "status": "Chat-Memory gelöscht",
        "core": core_stats()
    })


@app.route("/clear_all_memory", methods=["POST"])
def clear_all_memory():
    conversation_history.clear()
    memories.clear()
    return jsonify({
        "status": "Alle Erinnerungen gelöscht",
        "core": core_stats()
    })


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

    return jsonify({
        "result": entry,
        "core": core_stats()
    })


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

    return jsonify({
        "task": task,
        "core": core_stats()
    })


@app.route("/tasks")
def get_tasks():
    return jsonify({
        "tasks": tasks,
        "core": core_stats()
    })


@app.route("/results")
def get_results():
    return jsonify({
        "results": results,
        "core": core_stats()
    })


@app.route("/tools")
def get_tools():
    return jsonify({
        "tools": tools,
        "permissions": permissions,
        "core": core_stats()
    })


@app.route("/coding-agent")
def coding_agent():
    return jsonify({
        "name": "Coding Agent",
        "status": "online",
        "abilities": [
            "Code analysieren",
            "Fehler finden",
            "Verbesserungen vorschlagen",
            "NOVA prüfen"
        ]
    })

@app.route("/coding-agent/analyze", methods=["POST"])
def coding_agent_analyze():
    data = request.json or {}
    code = data.get("code", "").strip()
    question = data.get("question", "Prüfe diesen Code auf Fehler.").strip()

    if not code:
        return jsonify({"error": "Kein Code angegeben"}), 400

    prompt = f"""
Du bist der Coding Agent im NOVA Core.
Prüfe den folgenden Code sorgfältig.

Aufgabe:
{question}

Code:
{code}

Antworte strukturiert:
1. Fehler
2. Ursache
3. Korrektur
4. Verbesserungsvorschlag
"""

    result = ask_nova(prompt, max_tokens=1200)

    log_action(
        "coding_agent",
        "Coding Agent hat Code analysiert.",
        "low",
        "completed"
    )

    return jsonify({
        "agent": "Coding Agent",
        "status": "completed",
        "result": result
    })

@app.route("/permissions")
def get_permissions():
    return jsonify({
        "permissions": permissions
    })


@app.route("/run_tool", methods=["POST"])
def run_tool():
    data = request.json or {}
    tool_id = data.get("tool_id", "").strip()
    command = data.get("command", "").strip()

    if not tool_id:
        return jsonify({"error": "Kein Tool angegeben"}), 400

    if tool_id not in permissions:
        return jsonify({"error": "Unbekanntes Tool"}), 404

    if not permissions.get(tool_id):
        return jsonify({
            "status": "blocked",
            "message": f"Tool '{tool_id}' ist noch nicht freigegeben."
        }), 403

    return jsonify({
        "status": "planned",
        "tool_id": tool_id,
        "command": command,
        "message": "Tool-Struktur ist vorbereitet. Echte Integration folgt später."
    })


@app.route("/health")
def health():
    return jsonify({"ok": True, "core": "NOVA"})

@app.route("/security")
def security():

    return jsonify({
        "role": user_role,
        "actions": len(action_log),
        "risk_levels": risk_levels
    })


@app.route("/logs")
def logs():
    return jsonify(action_log)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)