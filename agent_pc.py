import requests
import time
import socket
import sys
import os

SERVER = "https://samia-server.onrender.com"

def is_internet_available():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except:
        return False

def keep_alive():
    try:
        requests.get(SERVER, timeout=5)
    except:
        pass

def wait_for_server():
    print("🔄 Connexion au serveur SAMIA...")

    while True:
        if not is_internet_available():
            print("❌ Pas d'internet... nouvelle tentative")
            time.sleep(5)
            continue

        try:
            requests.get(SERVER, timeout=5)
            print("✅ Serveur connecté")
            return True
        except:
            print("⏳ Serveur en attente (Render en veille...)")
            time.sleep(5)

def safe_request(endpoint):
    try:
        response = requests.get(f"{SERVER}/{endpoint}", timeout=10)
        return response.json()
    except Exception as e:
        print(f"❌ Erreur réseau: {e}")
        return None

def execute_command(cmd):
    if cmd == "shutdown":
        os.system("shutdown /s /t 1")

    elif cmd == "restart":
        os.system("shutdown /r /t 1")

    elif cmd == "open_chrome":
        os.system("start chrome")

def main():
    wait_for_server()

    error_detected = False

    while True:
        try:
            question = safe_request("get_question")
            command = safe_request("get_command")

            if question:
                print("📩 Question reçue:", question)

            if command and command.get("command"):
                cmd = command["command"]
                print("⚙️ Exécution:", cmd)
                execute_command(cmd)

            time.sleep(2)

        except Exception as e:
            print(f"❌ ERREUR CRITIQUE: {e}")
            error_detected = True
            break

    return error_detected


if __name__ == "__main__":
    error = main()

    # 🔥 comportement fenêtre CMD
    if not error:
        # ✅ pas d’erreur → fermer
        sys.exit()
    else:
        # ❌ erreur → rester ouvert
        input("Appuie sur Entrée pour fermer...")