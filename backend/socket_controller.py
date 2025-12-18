import sys
import os
import socket
import json
import threading

# Ensure project root is on sys.path so sibling packages (like `envs`) can be imported
# when running this script from the `backend` directory.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from pacman_game import PacmanGame
from config.socket_config import HOST, PORT

# Khởi tạo game
MAP_FILE = os.path.join(os.path.dirname(__file__), "../maps/mediumClassic.map")
game = PacmanGame(MAP_FILE)

# -------------------------------
# Socket handler
# -------------------------------
def handle_client(conn, addr):
    print(f"[Backend] New connection from: {addr}")
    buffer = ""

    try:
        while True:
            data = conn.recv(8192)
            if not data:
                print(f"[Backend] {addr} disconnected.")
                break

            buffer += data.decode("utf-8")

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    print(f"[Backend] JSONDecodeError from {addr}: {line}")
                    continue

                msg_type = msg.get("type")
                if msg_type == "request_state":
                    res = {
                        "type": "state",
                        "state": game.serialize_state()
                    }
                    conn.sendall((json.dumps(res) + "\n").encode("utf-8"))

                elif msg_type == "action":
                    agent_idx = msg.get("agent")
                    action = msg.get("action")
                    game.apply_action(agent_idx, action)
                    game.draw_ui()

                elif msg_type == "get_status":
                    res = {
                        "type": "status",
                        "last_executed": game.last_actions
                    }
                    conn.sendall((json.dumps(res) + "\n").encode("utf-8"))

                else:
                    print(f"[Backend] Unknown message type: {msg_type}")

    except ConnectionResetError:
        print(f"[Backend] {addr} disconnected abruptly.")
    finally:
        conn.close()


def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(20)
    print(f"--- BACKEND SERVER --- Running at {HOST}:{PORT}")

    try:
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\n[Backend] Shutting down server...")
    finally:
        s.close()


if __name__ == "__main__":
    start_server()