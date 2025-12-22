import os
import sys
import numpy as np
import time

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.pacman_game import PacmanGame
from agents.factory import make_agent
from envs.directions import Directions
from ui.tkinter_ui import TkinterDisplay
from config import point

MAP_FILE = os.path.join(PROJECT_ROOT, "maps/mediumClassic.map")

NUM_EPISODES = 10000
SAVE_EVERY = 1

SHOW_UI_EVERY = 1
FRAME_TIME = 0.001


def train():
    tmp_game = PacmanGame(MAP_FILE)
    h, w = tmp_game.get_state_size()
    state_shape = (1, h, w) 

    pacman = make_agent("dqn_pacman", 0, state_shape=state_shape)

    ghosts = [
        make_agent("random_ghost", 1),
        make_agent("random_ghost", 2)
    ]

    all_agents = [pacman] + ghosts
    num_agents = len(all_agents)

    print("\n--- BẮT ĐẦU HUẤN LUYỆN ---")
    print(f"Hiển thị UI mỗi {SHOW_UI_EVERY} episode\n")

    for ep in range(1, NUM_EPISODES + 1):

        current_display = (
            TkinterDisplay(zoom=1.5, frame_time=FRAME_TIME)
            if ep % SHOW_UI_EVERY == 0 else None
        )

        game = PacmanGame(MAP_FILE, display=current_display)
        state = game.get_state()

        if current_display:
            current_display.update(state)

        last_score = 0
        step_count = 0
        done = False

        time1 = 0

        while not done:
            time1 += 1
            curr_idx = step_count % num_agents
            agent = all_agents[curr_idx]

            legal_actions = state.getLegalActions(curr_idx)
            action = agent.getAction(state) if legal_actions else Directions.LEFT

            game.apply_action(curr_idx, action)
            next_state = game.get_state()

            if current_display:
                current_display.update(next_state)

            if curr_idx == 0:  # pacman
                current_score = next_state.getScore()
                reward = current_score
                reward += time1 * point.TIME_PENALTY
                done = game.check_game_over()

                if done:
                    if next_state.isWin():
                        reward += point.WIN_REWARD
                    elif next_state.isLose():
                        reward += point.PACMAN_DEATH_PENALTY

                print(f"Step {step_count}: Action={action}, Reward={reward:.2f}, Score={current_score:.1f}")

                if hasattr(pacman, "update_policy"):
                    pacman.update_policy(
                        state,
                        action,
                        reward,
                        next_state,
                        done
                    )

                last_score = current_score
            else:
                done = game.check_game_over()

            state = next_state
            step_count += 1

        status = "WIN" if state.isWin() else "LOSE"
        epsilon = getattr(pacman, "epsilon", 0)

        print(
            f"Ep: {ep:<5} | "
            f"{status:<5} | "
            f"Score: {state.getScore():>6.1f} | "
            f"Eps: {epsilon:.3f} | "
            f"Steps: {step_count}"
        )

        if ep % SAVE_EVERY == 0 and hasattr(pacman, "save_checkpoint"):
            pacman.save_checkpoint()

        if current_display:
            current_display.finish()

    print("\n--- HUẤN LUYỆN HOÀN TẤT ---")


if __name__ == "__main__":
    train()
