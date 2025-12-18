import numpy as np
from envs.game_state import GameState, AgentInfo, GhostInfo
from envs import layouts
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def load_map(file_path: str) -> GameState:
    with open(file_path, "r") as f:
        lines = [line.rstrip("\n") for line in f.readlines() if line.strip()]
    
    H = len(lines)
    W = len(lines[0])
    object_matrix = np.zeros((H, W), dtype=int)
    pacman = None
    ghosts = []

    for y, line in enumerate(lines):
        for x, ch in enumerate(line):
            if ch == '%':
                object_matrix[y, x] = layouts.WALL
            elif ch == '.':
                object_matrix[y, x] = layouts.FOOD
            elif ch == 'o':
                object_matrix[y, x] = layouts.CAPSULE
            elif ch == 'P':
                object_matrix[y, x] = layouts.PACMAN
                pacman = AgentInfo(x=x, y=y, dir=0)
            elif ch == 'G':
                # gán số ghost liên tiếp (layouts.GHOST1, GHOST2,...)
                ghost_id = len(ghosts)
                object_matrix[y, x] = getattr(layouts, f"GHOST{ghost_id+1}", layouts.GHOST1)
                ghosts.append(GhostInfo(x=x, y=y, dir=0, scared_timer=0))
            elif ch == ' ':
                object_matrix[y, x] = layouts.EMPTY
            else:
                object_matrix[y, x] = layouts.EMPTY

    return GameState(
        object_matrix=object_matrix,
        pacman=pacman,
        ghosts=ghosts,
        score=0.0,
        win=False,
        lose=False
    )

# -------------------------------
# Demo
# -------------------------------
# if __name__ == "__main__":
#     print(os.getcwd())
#     state = load_map("maps/mediumClassic.map")
#     print(state)
