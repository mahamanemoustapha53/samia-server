from flask import Flask, request, jsonify
import os

app = Flask(__name__)

AUTHORIZED_VOICE = "masmm_voice.wav"

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

# =========================
# 🔥 FLUTTER → QUESTION
# =========================
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question")

    question_store["question"] = question

    return {"status": "ok", "message": "Question reçue"}

# =========================
# 🔥 AGENT → GET QUESTION
# =========================
@app.route("/get_question", methods=["GET"])
def get_question():
    q = question_store["question"]
    question_store["question"] = None
    return {"question": q}

# =========================
# 🔥 AGENT → SEND ANSWER
# =========================
@app.route("/send_answer", methods=["POST"])
def send_answer():
    data = request.json
    answer_store["answer"] = data.get("answer")
    return {"status": "ok"}

# =========================
# 🔥 FLUTTER → GET ANSWER
# =========================
@app.route("/get_answer", methods=["GET"])
def get_answer():
    a = answer_store["answer"]
    answer_store["answer"] = None
    return {"answer": a}

# =========================
# 🔥 COMMANDE → ENVOYER
# =========================
@app.route("/command", methods=["POST"])
def command():
    data = request.json
    cmd = data.get("command")

    command_store["command"] = cmd

    return {"status": "ok"}

# =========================
# 🔥 AGENT → GET COMMAND
# =========================
@app.route("/get_command", methods=["GET"])
def get_command():
    cmd = command_store["command"]
    command_store["command"] = None
    return {"command": cmd}

# =========================
# 🔥 RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)