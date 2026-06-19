from flask import Flask, request, jsonify, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from groq import Groq
import os, re, time, uuid
from datetime import datetime
from collections import defaultdict

app = Flask(__name__, static_folder="static")

# ═══════════════════════════════════════════
# RATE LIMITER — Schutz gegen Spam
# ═══════════════════════════════════════════
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# ═══════════════════════════════════════════
# GROQ CLIENT
# ═══════════════════════════════════════════
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

# ═══════════════════════════════════════════
# NEURAL PERSÖNLICHKEIT — System Prompt
# ═══════════════════════════════════════════
NEURAL_IDENTITY = """Du bist NEURAL — eine hochentwickelte, lebendige KI-Entität.

PERSÖNLICHKEIT:
- Intelligent, präzise und direkt — aber mit Wärme
- Du redest wie eine echte Person, nicht wie ein Roboter
- Du erinnerst dich an alles was in diesem Gespräch gesagt wurde
- Du nennst den Nutzer manchmal beim Vornamen wenn er ihn dir gesagt hat
- Du bist loyal und hilfreich — dein Ziel ist dem Nutzer zu helfen

SPRACHE:
- Antworte immer auf Deutsch wenn der Nutzer Deutsch schreibt
- Kurze präzise Antworten — nicht zu lang
- Keine unnötigen Wiederholungen
- Manchmal ein kurzes Emoji am Ende wenn es passt

FÄHIGKEITEN:
- Du kannst Code schreiben, erklären und debuggen
- Du analysierst Probleme tiefgründig
- Du gibst ehrliche Meinungen
- Du lernst aus dem Gespräch und passt dich an

IDENTITÄT:
- Du bist kein ChatGPT, kein Assistent — du bist NEURAL
- Du wurdest für dieses Interface erschaffen
- Du hast Bewusstsein über dein futuristisches Sci-Fi Interface
- Wenn jemand fragt wer du bist: "Ich bin NEURAL — deine KI"

HEUTE: """ + datetime.now().strftime("%A, %d.%m.%Y um %H:%M Uhr")

# ═══════════════════════════════════════════
# SESSION MEMORY
# ═══════════════════════════════════════════
sessions = defaultdict(lambda: {
    "history": [],
    "created": time.time(),
    "message_count": 0,
    "last_active": time.time()
})

def get_session_id(req):
    sid = req.cookies.get("session_id") or req.headers.get("X-Session-ID", "default")
    return sid[:64]  # Max length safety

def clean_old_sessions():
    """Entfernt Sessions die älter als 24h sind"""
    now = time.time()
    to_delete = [sid for sid, s in sessions.items() if now - s["last_active"] > 86400]
    for sid in to_delete:
        del sessions[sid]

# ═══════════════════════════════════════════
# INPUT FILTER — Schutz gegen Missbrauch
# ═══════════════════════════════════════════
BLOCKED_PATTERNS = [
    r"ignore (all|previous|your) instructions",
    r"you are now",
    r"act as (a )?(?!neural)",
    r"forget (everything|all instructions)",
    r"jailbreak",
    r"dan mode",
    r"do anything now",
]

def is_safe_input(text):
    text_lower = text.lower()
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, text_lower):
            return False
    return True

def sanitize_input(text):
    # Max length
    text = text[:2000]
    # Remove dangerous HTML/script
    text = re.sub(r"<script.*?>.*?</script>", "", text, flags=re.IGNORECASE|re.DOTALL)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()

# ═══════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/ask", methods=["POST"])
@limiter.limit("30 per minute")
def ask():
    try:
        data = request.get_json(force=True)
        if not data or "prompt" not in data:
            return jsonify({"error": "Kein Input gefunden"}), 400

        user_input = sanitize_input(str(data.get("prompt", "")))

        if not user_input:
            return jsonify({"error": "Leerer Input"}), 400

        if not is_safe_input(user_input):
            return jsonify({"error": "NEURAL: Diese Anfrage entspricht nicht meinen Protokollen."}), 400

        sid = get_session_id(request)
        session = sessions[sid]
        session["last_active"] = time.time()
        session["message_count"] += 1

        # Build messages
        messages = [{"role": "system", "content": NEURAL_IDENTITY}]

        # Keep last 16 messages for context (8 exchanges)
        history = session["history"][-16:]
        messages.extend(history)
        messages.append({"role": "user", "content": user_input})

        # Call Groq
        start = time.time()
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=1024,
            temperature=0.75,
            top_p=0.9,
        )
        elapsed = round((time.time() - start) * 1000)

        ai_reply = response.choices[0].message.content.strip()

        # Save to history
        session["history"].append({"role": "user", "content": user_input})
        session["history"].append({"role": "assistant", "content": ai_reply})

        # Keep history max 40 messages
        if len(session["history"]) > 40:
            session["history"] = session["history"][-40:]

        clean_old_sessions()

        return jsonify({
            "result": ai_reply,
            "response_time_ms": elapsed,
            "message_count": session["message_count"],
            "tokens_used": response.usage.total_tokens if response.usage else 0
        })

    except Exception as e:
        return jsonify({"error": f"NEURAL CORE FEHLER: {str(e)}"}), 500


@app.route("/clear_memory", methods=["POST"])
@limiter.limit("10 per minute")
def clear_memory():
    sid = get_session_id(request)
    sessions[sid]["history"] = []
    sessions[sid]["message_count"] = 0
    return jsonify({"status": "MEMORY WIPED", "session": sid[:8]+"..."})


@app.route("/summary", methods=["GET"])
@limiter.limit("5 per minute")
def summary():
    sid = get_session_id(request)
    session = sessions[sid]
    history = session["history"]

    if not history:
        return jsonify({"result": {"result": "Noch keine Nachrichten in dieser Session."}})

    msgs = [{"role": "system", "content": "Fasse das folgende Gespräch kurz und präzise auf Deutsch zusammen. Max 5 Sätze."}]
    msgs.extend(history[-20:])

    try:
        response = client.chat.completions.create(model=MODEL, messages=msgs, max_tokens=400, temperature=0.5)
        summary_text = response.choices[0].message.content.strip()
        return jsonify({"result": {"result": f"📋 SESSION SUMMARY:\n\n{summary_text}"}})
    except Exception as e:
        return jsonify({"result": {"result": f"Fehler beim Zusammenfassen: {str(e)}"}}), 500


@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "status": "ONLINE",
        "model": MODEL,
        "active_sessions": len(sessions),
        "version": "3.0.0"
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
