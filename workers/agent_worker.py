import sys
import os
import time
import socket

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from envs.game_state import deserialize_state
from frontend.socket_client import SocketClient
from agents.factory import make_agent
from config.socket_config import HOST, PORT

def main():
    if len(sys.argv) < 3:
        sys.exit(1)

    agent_idx = int(sys.argv[1])
    algo = sys.argv[2]

    agent = make_agent(algo, agent_idx)
    client = SocketClient(host=HOST, port=PORT)

    print(f"[Worker {agent_idx}] Running with algorithm: {algo}")

    while True:
        if not client.sock:
            print(11111)
            if not client.connect():
                time.sleep(1)
                continue

        try:
            client.send({"type": "request_state", "agent": agent_idx})
            msg = client.recv(timeout=1.0)
            print(f"[Worker {agent_idx}] Received message: {msg}")
            if msg and msg.get("type") == "state":
                game_state = deserialize_state(msg.get("state"))
                action = agent.getAction(game_state)
                if action:
                    client.send({"type": "action", "agent": agent_idx, "action": action})

            time.sleep(0.05)
        except:
            client.close()
            time.sleep(1)

if __name__ == "__main__":
    main()
