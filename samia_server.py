from flask import Flask, request, jsonify

app = Flask(__name__)

# 🔥 mémoire simple
latest_command = None
latest_question = None
latest_answer = None

@app.route("/")
def home():
    return {"message": "SAMIA server running"}

# 📩 recevoir question depuis téléphone
@app.route("/ask", methods=["POST"])
def ask():
    global latest_question

    data = request.json
    latest_question = data.get("question")

    return {"status": "processing"}

# 📥 PC récupère question
@app.route("/get_question")
def get_question():
    global latest_question
    return {"question": latest_question}

# 📤 PC envoie réponse
@app.route("/send_answer", methods=["POST"])
def send_answer():
    global latest_answer

    data = request.json
    latest_answer = data.get("answer")

    return {"status": "ok"}

# 📲 téléphone récupère réponse
@app.route("/get_answer")
def get_answer():
    global latest_answer
    return {"answer": latest_answer}

# 📩 envoyer commande depuis téléphone
@app.route("/command", methods=["POST"])
def command():
    global latest_command

    data = request.json
    latest_command = data.get("command")

    return {"status": "sent"}

# 💻 PC récupère commande
@app.route("/get_command")
def get_command():
    global latest_command
    return {"command": latest_command}

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)