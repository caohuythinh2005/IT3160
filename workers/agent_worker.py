import sys
import os
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from frontend.socket_client import SocketClient
from agents.factory import make_agent
from envs.game_state import deserialize_state
from config.socket_config import HOST, PORT

def main():
    if len(sys.argv) < 3:
        print("Usage: python agent_worker.py <agent_idx> <algo>")
        sys.exit(1)

    agent_idx = int(sys.argv[1])
    algo = sys.argv[2]
    agent = make_agent(algo, agent_idx)

    client = SocketClient(host=HOST, port=PORT)

    while True:
        try:
            if not client.connect():
                print(f"[Worker {agent_idx}] Cannot connect, retrying in 2s...")
                time.sleep(2)
                continue

            print(f"[Worker {agent_idx}] Connected, running algo: {algo}")

            while True:
                client.send({"type": "request_state", "agent": agent_idx})
                msg = client.recv(timeout=1.0)
                if not msg or msg.get("type") != "state":
                    time.sleep(0.05)
                    continue

                if msg.get("current_turn") != agent_idx:
                    time.sleep(0.05)
                    continue

                game_state = deserialize_state(msg.get("state"))
                action = agent.getAction(game_state)
                if action:
                    client.send({"type": "action", "agent": agent_idx, "action": action})

                time.sleep(0.05)

        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError) as e:
            print(f"[Worker {agent_idx}] Connection lost: {e}, retrying in 2s...")
            client.close()
            time.sleep(2)
        except Exception as e:
            print(f"[Worker {agent_idx}] Unexpected error: {e}")
            client.close()
            time.sleep(2)

if __name__ == "__main__":
    main()
