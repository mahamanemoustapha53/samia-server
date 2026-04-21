from flask import Flask, request, jsonify
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

AUTHORIZED_VOICE = "masmm_voice.wav"

SECRET_TOKEN = "MASMM_SUPER_SECRET_2006"

screen_store = {"image": None}

def check_token(req):
    token = req.headers.get("Authorization")
    return token == SECRET_TOKEN

# 🔥 STOCKAGE TEMPORAIRE (RAM)
question_store = {"question": None}
answer_store = {"answer": None}
command_store = {"command": None}

def verify_voice(voice_file):
    return True

@app.route("/")
def home():
    return {"message": "SAMIA server running"}

@app.route("/samia")
def samia():
    return {"name": "SAMIA_PC", "status": "online"}

@app.route("/screen", methods=["POST"])
def receive_screen():
    if not check_token(request):
        return {"status": "error"}, 403

    data = request.get_json()
    screen_store["image"] = data.get("image")

    return {"status": "ok"}

@app.route("/get_screen", methods=["GET"])
def get_screen():
    if not check_token(request):
        return {"status": "error"}, 403

    return {"image": screen_store["image"]}

# =========================
# 🔥 FLUTTER → QUESTION
# =========================
@app.route("/ask", methods=["POST"])
def ask():
    if not check_token(request):
        return {"status": "error", "message": "Unauthorized"}, 403
    data = request.get_json(silent=True) or {}
    question = data.get("question")
    if not question:
        return {"status": "error", "message": "Question vide"}

    question_store["question"] = question

    return {"status": "ok", "message": "Question reçue"}

# =========================
# 🔥 AGENT → GET QUESTION
# =========================
@app.route("/get_question", methods=["GET"])
def get_question():
    if not check_token(request):
        return {"status": "error", "message": "Unauthorized"}, 403
    q = question_store["question"]
    question_store["question"] = None
    return {"question": q}

# =========================
# 🔥 AGENT → SEND ANSWER
# =========================
@app.route("/send_answer", methods=["POST"])
def send_answer():
    if not check_token(request):
        return {"status": "error", "message": "Unauthorized"}, 403
    data = request.get_json(silent=True) or {}
    answer_store["answer"] = data.get("answer")
    if not data.get("answer"):
        return {"status": "error", "message": "Réponse vide"}
    return {"status": "ok"}

# =========================
# 🔥 FLUTTER → GET ANSWER
# =========================
@app.route("/get_answer", methods=["GET"])
def get_answer():
    if not check_token(request):
        return {"status": "error", "message": "Unauthorized"}, 403
    a = answer_store["answer"]
    answer_store["answer"] = None
    return {"answer": a}

# =========================
# 🔥 COMMANDE → ENVOYER
# =========================
@app.route("/command", methods=["POST"])
def command():
    if not check_token(request):
        return {"status": "error", "message": "Unauthorized"}, 403

    data = request.get_json(silent=True) or {}
    cmd = data.get("command")

    if not cmd:
        return {"status": "error", "message": "Commande vide"}

    ALLOWED_COMMANDS = ["shutdown", "restart", "open_chrome"]

    if cmd not in ALLOWED_COMMANDS:
        return {"status": "error", "message": "Commande interdite"}

    command_store["command"] = cmd

    return {"status": "ok"}

# =========================
# 🔥 AGENT → GET COMMAND
# =========================
@app.route("/get_command", methods=["GET"])
def get_command():
    if not check_token(request):
        return {"status": "error", "message": "Unauthorized"}, 403
    cmd = command_store["command"]
    command_store["command"] = None
    return {"command": cmd}

# =========================
# 🔥 NOUVELLE ROUTE WEB CHAT (IMPORTANT)
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    if not check_token(request):
        return {"status": "error", "message": "Unauthorized"}, 403

    data = request.get_json(silent=True) or {}
    message = data.get("message", "").lower()

    # 🔥 COMMANDES
    if "ouvre chrome" in message or "open chrome" in message:
        return {"status": "ok", "type": "command", "command": "open_chrome"}

    if "redémarre" in message or "restart pc" in message:
        return {"status": "ok", "type": "command", "command": "restart"}

    if "redémarre" in message or "open OBS" in message:
        return {"status": "ok", "type": "command", "command": "open_OBS"}

    if "éteins" in message or "shutdown" in message:
        return {"status": "ok", "type": "command", "command": "shutdown"}

    if "écran" in message:
        return {"type": "screen", "action": "start"}

    if "ferme l'écran" in message:
        return {"type": "screen", "action": "stop"}

    # 🔥 ENVOYER QUESTION À L'AGENT (OLLAMA)
    question_store["question"] = message

    return {"status": "ok", "type": "processing"}

# =========================
# 🔥 RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)