import numpy as np
from envs.game_state import GameState, AgentInfo, GhostInfo
from envs.game_engine import GameEngine 
from envs import layouts
from ui.renderers import BaseDisplay

class PacmanGame:
    def __init__(self, map_file: str, display: BaseDisplay = None):
        self.map_file = map_file
        self.state = self.load_map(map_file)
        self.state_size = self.state.object_matrix.shape
        self.last_actions = {}
        self.display = display
        self.paused = False

        if self.display:
            self.display.initialize(self.state)

    def load_map(self, file_path: str) -> GameState:
        with open(file_path, "r") as f:
            lines = [line.rstrip("\n") for line in f if line.strip()]

        H, W = len(lines), len(lines[0])
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
                    pacman = AgentInfo(x=x, y=y, dir="East")
                elif ch == 'G':
                    ghost_id = len(ghosts)
                    object_matrix[y, x] = getattr(layouts, f"GHOST{ghost_id+1}", layouts.GHOST1)
                    ghosts.append(GhostInfo(x=x, y=y, dir="East", scared_timer=0))
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

    def get_state(self) -> GameState:
        return self.state

    def get_state_size(self):
        return self.state_size

    def toggle_pause(self):
        self.paused = not self.paused

    def set_pause(self, value: bool):
        self.paused = value

    def apply_action(self, agent_idx: int, action: str):
        if self.paused:
            return False
        self.last_actions[agent_idx] = action
        GameEngine.apply_action(self.state, agent_idx, action)
        return True

    def draw_ui_tick(self):
        if self.display and not self.paused:
            self.display.update(self.state)

    def check_game_over(self) -> bool:
        if self.state.win or self.state.lose:
            if self.display:
                self.display.finish()
            return True
        return False
