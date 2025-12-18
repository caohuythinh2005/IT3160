import sys
import os
import socket
import json
import threading
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ui.tkinter_ui import TkinterDisplay
from pacman_game import PacmanGame
from config.socket_config import HOST, PORT
from envs.game_state import serialize_state

MAP_FILE = os.path.join(PROJECT_ROOT, "maps/mediumClassic.map")
if not os.path.isfile(MAP_FILE):
    raise FileNotFoundError(f"[Error] Map file not found: {MAP_FILE}")

NUM_AGENTS = 3
state_lock = threading.Lock()
ui = TkinterDisplay(zoom=1.5, frame_time=0.05)
game = PacmanGame(MAP_FILE, display=ui)

current_turn_agent = 0
pending_actions = {}  # agent_idx -> action
last_executed = {}    # agent_idx -> last action

def handle_action(agent_idx, action):
    global current_turn_agent
    with state_lock:
        if agent_idx != current_turn_agent:
            return
        pending_actions[agent_idx] = action
        print(f"[Server] Action received: agent {agent_idx} -> {action}")

def update_game_tick():
    global current_turn_agent
    with state_lock:
        action = pending_actions.get(current_turn_agent)
        if action:
            applied = game.apply_action(current_turn_agent, action)
            if applied:
                print(f"[Server] Action executed: agent {current_turn_agent} -> {action}")
                last_executed[current_turn_agent] = action
            else:
                print(f"[Server] Action ignored: agent {current_turn_agent} -> {action}")
        pending_actions.clear()
        if game.display:
            game.display.update(game.get_state())
        current_turn_agent = (current_turn_agent + 1) % NUM_AGENTS

def get_current_state():
    with state_lock:
        return serialize_state(game.get_state())

def handle_client(conn, addr):
    print(f"[Server] New connection: {addr}")
    buffer = ""
    try:
        while True:
            data = conn.recv(8192)
            if not data:
                print(f"[Server] {addr} disconnected.")
                break

            buffer += data.decode("utf-8")
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    print(f"[Server] JSONDecodeError from {addr}: {line}")
                    continue

                msg_type = msg.get("type")

                if msg_type == "action":
                    agent_idx = msg.get("agent")
                    action = msg.get("action")
                    handle_action(agent_idx, action)

                elif msg_type == "request_state":
                    agent_idx = msg.get("agent")
                    state_dict = get_current_state()
                    res = {
                        "type": "state",
                        "state": state_dict,
                        "current_turn": current_turn_agent
                    }
                    conn.sendall((json.dumps(res) + "\n").encode("utf-8"))

                elif msg_type == "get_status":
                    res = {"type": "status", "last_executed": last_executed}
                    conn.sendall((json.dumps(res) + "\n").encode("utf-8"))

                elif msg_type == "command":
                    print(f"[Server] Set algo for agent {msg.get('agent')}: {msg.get('algo')}")

                else:
                    print(f"[Server] Unknown message type: {msg_type}")

    except ConnectionResetError:
        print(f"[Server] {addr} disconnected abruptly.")
    finally:
        conn.close()

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(20)
    print(f"--- SERVER + UI RUNNING AT {HOST}:{PORT} ---")

    try:
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\n[Server] Shutting down...")
    finally:
        s.close()

def game_loop():
    while True:
        update_game_tick()
        time.sleep(0.05)

if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=game_loop, daemon=True).start()
    print("--- Pacman server + UI running ---")
    ui.mainloop()
