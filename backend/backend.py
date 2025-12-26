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
clients_lock = threading.Lock()
connected_clients = set() 
ui = TkinterDisplay(zoom=1.5, frame_time=0.001)
game = PacmanGame(MAP_FILE, display=ui)

current_turn_agent = 0
pending_actions = {}
last_executed = {}
paused = False

def handle_action(agent_idx, action):
    global current_turn_agent
    with state_lock:
        if paused:
            return
        if agent_idx != current_turn_agent:
            return
        if isinstance(action, list) and len(action) > 0:
            action = action[0]
        pending_actions[agent_idx] = action

def update_game_tick():
    global current_turn_agent
    with state_lock:
        if paused:
            return
        action = pending_actions.get(current_turn_agent)
        if action is not None:
            applied = game.apply_action(current_turn_agent, action)
            if applied:
                last_executed[current_turn_agent] = action
        pending_actions.clear()
        if game.display:
            game.display.update(game.get_state())
        current_turn_agent = (current_turn_agent + 1) % NUM_AGENTS

def get_current_state():
    with state_lock:
        return serialize_state(game.get_state())

def handle_client(conn, addr):
    global paused
    client_id = f"{addr[0]}:{addr[1]}"

    with clients_lock:
        connected_clients.add(client_id)
        print(f"[SERVER] Client connected: {client_id} | Total: {len(connected_clients)}")

    buffer = ""
    try:
        while True:
            data = conn.recv(8192)
            if not data:
                break

            buffer += data.decode("utf-8")
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue

                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue

                msg_type = msg.get("type")

                if msg_type == "action":
                    handle_action(msg.get("agent"), msg.get("action"))

                elif msg_type == "request_state":
                    res = {
                        "type": "state",
                        "state": get_current_state(),
                        "current_turn": current_turn_agent
                    }
                    conn.sendall((json.dumps(res) + "\n").encode("utf-8"))

                elif msg_type == "get_status":
                    res = {
                        "type": "status",
                        "connected": True,
                        "num_clients": len(connected_clients),
                        "last_executed": last_executed,
                        "paused": paused
                    }
                    conn.sendall((json.dumps(res) + "\n").encode("utf-8"))

                elif msg_type == "command":
                    cmd = msg.get("cmd")
                    if cmd == "pause":
                        paused = True
                        game.set_pause(True)
                    elif cmd == "unpause":
                        paused = False
                        game.set_pause(False)

    except ConnectionResetError:
        print(f"[SERVER] Client reset connection: {client_id}")

    finally:
        with clients_lock:
            connected_clients.discard(client_id)
            print(f"[SERVER] Client disconnected: {client_id} | Total: {len(connected_clients)}")
        conn.close()

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(20)
    print(f"[SERVER] Listening on {HOST}:{PORT}")

    try:
        while True:
            conn, addr = s.accept()
            threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True
            ).start()
    finally:
        s.close()

def game_loop():
    while True:
        update_game_tick()
        time.sleep(0.05)

if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=game_loop, daemon=True).start()
    ui.mainloop()
