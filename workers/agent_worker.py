import sys
import time
import random
import numpy as np
from envs.game_state import GameState
from frontend.socket_client import SocketClient

STEP_SLEEP = 0.1

def adapt_state(raw_state: dict, agent_code: int) -> dict:
    gs = GameState(
        object_matrix=np.array(raw_state["object_matrix"]),
        info_vector=np.array(raw_state["info_vector"]),
        score=float(raw_state["score"]),
        win=raw_state["win"],
        lose=raw_state["lose"]
    )
    obs = {
        "game_state": gs,
        "agent_code": agent_code,
        "legal_actions": ["North", "South", "East", "West"]
    }
    return obs

class RandomAgent:
    def getAction(self, obs):
        legal = obs.get("legal_actions", [])
        return random.choice(legal) if legal else "North"

def main():
    if len(sys.argv) < 3:
        print("Usage: python agent_worker.py <agent_idx> <algo>")
        sys.exit(1)

    agent_idx = int(sys.argv[1])
    algo = sys.argv[2]

    agent = RandomAgent()
    client = SocketClient()

    print(f"[Agent Worker {agent_idx}] started with algo '{algo}'")

    while True:
        try:
            # 1️⃣ Request state
            client.send({"type": "request_state", "agent": agent_idx})

            # 2️⃣ Receive state
            raw_msg = client.recv()
            if not raw_msg or raw_msg.get("type") != "state":
                time.sleep(STEP_SLEEP)
                continue

            obs = adapt_state(raw_msg["state"], agent_idx)
            print(f"[Agent Worker {agent_idx}] received state:\n{obs['game_state']}")

            # 3️⃣ Choose action
            action = agent.getAction(obs)
            print(f"[Agent Worker {agent_idx}] sending action: {action}")

            # 4️⃣ Send action
            client.send({"type": "action", "agent": agent_idx, "action": action})
            time.sleep(STEP_SLEEP)

        except KeyboardInterrupt:
            print(f"[Agent Worker {agent_idx}] terminating.")
            break
        except Exception as e:
            print(f"[Agent Worker {agent_idx}] Error: {e}")
            time.sleep(STEP_SLEEP)

if __name__ == "__main__":
    main()
