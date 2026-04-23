import requests
import time
import socket
import sys
import os
import mss
import cv2
import numpy as np
import base64

SERVER = "https://samia-server.onrender.com"

ALLOWED_COMMANDS = [
    "shutdown",
    "restart",
    "open_chrome",
    "open_notepad",
    "bluetooth_on",
    "wifi_hotspot"
]

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

def capture_screen():
    with mss.mss() as sct:
        screen = sct.grab(sct.monitors[1])
        img = np.array(screen)

        _, buffer = cv2.imencode(".jpg", img)
        jpg_as_text = base64.b64encode(buffer).decode("utf-8")

        return jpg_as_text

def safe_request(endpoint):
    try:
        response = requests.get(
            f"{SERVER}/{endpoint}",
            headers={"Authorization": "MASMM_SUPER_SECRET_2006"},
            timeout=10
        )
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

    elif cmd == "open_OBS":
        os.system('"C:\\Program Files\\obs-studio\\bin\\64bit\\obs64.exe"')

    elif cmd == "open_notepad":
        os.system("start notepad")

    elif cmd == "bluetooth_on":
        os.system("powershell Start-Service bthserv")

    elif cmd == "wifi_hotspot":
        os.system("netsh wlan start hostednetwork")

def ask_ollama(prompt):
    try:
        res = requests.post("http://localhost:11434/api/generate", json={
            "model": "qwen2.5:0.5b",
            "prompt": prompt,
            "stream": False
        }, timeout=60)

        data = res.json()
        return data.get("response", "Pas de réponse")

    except Exception as e:
        return f"Erreur Ollama: {e}"

def main():
    wait_for_server()

    error_detected = False
    screen_active = False   # ✅ DOIT ÊTRE ICI (GLOBAL LOOP)

    while True:
        try:
            question = safe_request("get_question")
            command = safe_request("get_command")

            # ======================
            # 🔥 GESTION COMMANDES
            # ======================
            if command and command.get("command"):
                cmd = command["command"]
                print("⚙️ Commande:", cmd)

                if cmd == "screen_on":
                    screen_active = True
                    print("🟢 Écran ACTIVÉ")

                elif cmd == "screen_off":
                    screen_active = False
                    print("🔴 Écran DÉSACTIVÉ")

                else:
                    execute_command(cmd)

            # ======================
            # 🔥 STREAM ÉCRAN (SAFE)
            # ======================
            if screen_active:
                try:
                    screen_data = capture_screen()

                    requests.post(
                        f"{SERVER}/screen",
                        json={"image": screen_data},
                        headers={"Authorization": "MASMM_SUPER_SECRET_2006"},
                        timeout=10
                    )

                except Exception as e:
                    print("⚠️ Erreur écran:", e)

            # ======================
            # 🔥 QUESTION → OLLAMA
            # ======================
            if question and question.get("question"):
                q = question["question"]
                print("📩 Question reçue:", q)

                answer = ask_ollama(q)
                print("🤖 Réponse:", answer)

                requests.post(
                    f"{SERVER}/send_answer",
                    json={"answer": answer},
                    headers={"Authorization": "MASMM_SUPER_SECRET_2006"},
                    timeout=10
                )

            time.sleep(2)  # 🔥 IMPORTANT (anti crash Render)

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