import numpy as np
from envs.game_state import GameState, AgentInfo, GhostInfo, serialize_state
from envs import layouts

class PacmanGame:
    def __init__(self, map_file: str):
        """Khởi tạo game từ file map"""
        self.map_file = map_file
        self.state = self.load_map(map_file)
        self.last_actions = {}

    def load_map(self, file_path: str) -> GameState:
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
                    ghost_id = len(ghosts)
                    object_matrix[y, x] = getattr(layouts, f"GHOST{ghost_id+1}", layouts.GHOST1)
                    ghosts.append(GhostInfo(x=x, y=y, dir=0, scared_timer=0))
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

    def serialize_state(self) -> dict:
        return serialize_state(self.state)

    def move_pacman(self, action: str):
        pac = self.state.pacman
        print(f"[Debug] Pacman at ({pac.x}, {pac.y}) moves {action}")

    def move_ghosts(self):
        for g in self.state.ghosts:
            print(f"[Debug] Ghost at ({g.x}, {g.y}) moves randomly")

    def apply_action(self, agent_idx: int, action: str):
        self.last_actions[agent_idx] = action
        if agent_idx == 0:
            self.move_pacman(action)
        else:
            print(f"[Debug] Agent {agent_idx} action: {action}")


    def check_game_over(self) -> bool:
        return False

    def update_score(self):
        pass

    def draw_ui(self):
        """Vẽ map đơn giản ra console"""
        mat = self.state.object_matrix
        H, W = mat.shape
        for y in range(H):
            line = ""
            for x in range(W):
                val = mat[y, x]
                if val == layouts.WALL:
                    line += "%"
                elif val == layouts.FOOD:
                    line += "."
                elif val == layouts.CAPSULE:
                    line += "o"
                elif val == layouts.PACMAN:
                    line += "P"
                elif val in [layouts.GHOST1, layouts.GHOST2, layouts.GHOST3, layouts.GHOST4]:
                    line += "G"
                else:
                    line += " "
            print(line)
        print(f"Score: {self.state.score}, Last actions: {self.last_actions}")
