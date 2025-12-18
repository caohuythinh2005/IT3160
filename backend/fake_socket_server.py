import sys
import os
import socket
import json
import numpy as np
import threading
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, os.path.join(project_root))

from envs.game_state import GameState, AgentInfo, GhostInfo, serialize_state
from config.socket_config import HOST, PORT

fake_state = GameState(
    object_matrix=np.zeros((5,5)),
    pacman=AgentInfo(x=2, y=2, dir=0),
    ghosts=[
        GhostInfo(x=3, y=3, dir=0, scared_timer=0), 
        GhostInfo(x=1, y=1, dir=0, scared_timer=0)
    ],
    score=0.0, win=False, lose=False
)

last_actions = {0: "-", 1: "-", 2: "-"}
last_actions_lock = threading.Lock()

def handle_client(conn, addr):
    print(f"[FakeServer] New connection from: {addr}")
    buffer = ""

    try:
        while True:
            data = conn.recv(8192)
            if not data:
                print(f"[FakeServer] {addr} disconnected.")
                break

            buffer += data.decode("utf-8")

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    print(f"[FakeServer] JSONDecodeError from {addr}: {line}")
                    continue

                msg_type = msg.get("type")

                if msg_type == "request_state":
                    res = {
                        "type": "state",
                        "state": serialize_state(fake_state)
                    }
                    conn.sendall((json.dumps(res) + "\n").encode("utf-8"))

                elif msg_type == "action":
                    agent_idx = msg.get("agent")
                    action = msg.get("action")
                    with last_actions_lock:
                        last_actions[agent_idx] = action
                        # Print all last actions whenever one is updated
                        print(f"[Actions Updated] {last_actions}")

                elif msg_type == "get_status":
                    with last_actions_lock:
                        status_copy = last_actions.copy()
                    res = {
                        "type": "status",
                        "last_executed": status_copy
                    }
                    conn.sendall((json.dumps(res) + "\n").encode("utf-8"))

                else:
                    print(f"[FakeServer] Unknown message type from {addr}: {msg_type}")

    except ConnectionResetError:
        print(f"[FakeServer] {addr} disconnected abruptly.")
    except Exception as e:
        print(f"[FakeServer] Error handling {addr}: {e}")
    finally:
        conn.close()

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        s.bind((HOST, PORT))
        s.listen(20)
        print(f"--- FAKE BACKEND SERVER ---")
        print(f"Running at: {HOST}:{PORT}")
        print(f"Press Ctrl+C to stop.")

        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

    except KeyboardInterrupt:
        print("\n[FakeServer] Shutting down server...")
    except Exception as e:
        print(f"[FakeServer] Server error: {e}")
    finally:
        s.close()

if __name__ == "__main__":
    start_server()
