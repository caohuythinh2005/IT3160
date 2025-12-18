import socket
import json
import numpy as np
from envs.game_state import GameState
import time

HOST = "127.0.0.1"
PORT = 50008

# Fake game state
fake_state = GameState(
    object_matrix=np.array([
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 4, 0, 1],
        [1, 0, 0, 5, 1],
        [1, 1, 1, 1, 1]
    ]),
    info_vector=np.array([2, 2, 3, 3] + [0]*21),
    score=0.0,
    win=False,
    lose=False
)

def serialize_state(state: GameState) -> dict:
    return {
        "object_matrix": state.object_matrix.tolist(),
        "info_vector": state.info_vector.tolist(),
        "score": state.score,
        "win": state.win,
        "lose": state.lose
    }

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"[FakeServer] running on {HOST}:{PORT}")

    try:
        while True:
            conn, addr = s.accept()
            print(f"[FakeServer] Connected by {addr}")
            with conn:
                while True:
                    data = conn.recv(4096)
                    if not data:
                        break
                    try:
                        msg = json.loads(data.decode("utf-8"))
                    except Exception:
                        continue

                    if msg.get("type") == "request_state":
                        # Send game state
                        conn.sendall(json.dumps({
                            "type": "state",
                            "state": serialize_state(fake_state)
                        }).encode("utf-8"))
                        print(f"[FakeServer] Sent state to agent {msg.get('agent')}")
                    elif msg.get("type") == "action":
                        # Just print received action
                        print(f"[FakeServer] Received action from agent {msg.get('agent')}: {msg.get('action')}")
                    time.sleep(0.05)
    except KeyboardInterrupt:
        print("[FakeServer] Shutting down")
