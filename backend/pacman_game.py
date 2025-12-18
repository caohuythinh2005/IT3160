import numpy as np
from envs.game_state import GameState, AgentInfo, GhostInfo
from envs import layouts
from ui.renderers import BaseDisplay


class PacmanGame:
    def __init__(self, map_file: str, display: BaseDisplay = None):
        self.map_file = map_file
        self.state = self.load_map(map_file)
        self.last_actions = {}
        self.display = display

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
                    pacman = AgentInfo(x=x, y=y, dir=2)
                elif ch == 'G':
                    ghost_id = len(ghosts)
                    object_matrix[y, x] = getattr(
                        layouts, f"GHOST{ghost_id+1}", layouts.GHOST1
                    )
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

    def move_pacman(self, action: str):
        pac = self.state.pacman
        action_map = {"North": 1, "East": 2, "South": 3, "West": 4}
        if action not in action_map:
            return

        pac.dir = action_map[action]
        dx, dy = 0, 0

        if pac.dir == 1: dy = -1
        elif pac.dir == 2: dx = 1
        elif pac.dir == 3: dy = 1
        elif pac.dir == 4: dx = -1

        nx, ny = pac.x + dx, pac.y + dy
        H, W = self.state.object_matrix.shape

        if 0 <= nx < W and 0 <= ny < H and self.state.object_matrix[ny, nx] != layouts.WALL:
            target = self.state.object_matrix[ny, nx]

            if target == layouts.FOOD:
                self.state.score += 10
            elif target == layouts.CAPSULE:
                self.state.score += 50

            self.state.object_matrix[pac.y, pac.x] = layouts.EMPTY
            self.state.object_matrix[ny, nx] = layouts.PACMAN
            pac.x, pac.y = nx, ny

            for g in self.state.ghosts:
                if g.x == pac.x and g.y == pac.y:
                    if g.scared_timer <= 0:
                        self.state.lose = True
                    else:
                        self.state.score += 200
                        g.x, g.y = 1, 1
                        g.scared_timer = 0

        if not np.any(self.state.object_matrix == layouts.FOOD):
            self.state.win = True

    def move_ghosts(self, ghost_idx: int, action: str):
        ghost = self.state.ghosts[ghost_idx]
        action_map = {
            "North": (0, -1),
            "East": (1, 0),
            "South": (0, 1),
            "West": (-1, 0)
        }

        if action not in action_map:
            return

        dx, dy = action_map[action]
        nx, ny = ghost.x + dx, ghost.y + dy
        H, W = self.state.object_matrix.shape

        if 0 <= nx < W and 0 <= ny < H and self.state.object_matrix[ny, nx] != layouts.WALL:
            self.state.object_matrix[ghost.y, ghost.x] = layouts.EMPTY
            ghost.x, ghost.y = nx, ny
            ghost.dir = {"North":1, "East":2, "South":3, "West":4}[action]
            self.state.object_matrix[ny, nx] = getattr(layouts, f"GHOST{ghost_idx+1}", layouts.GHOST1)

        if ghost.scared_timer > 0:
            ghost.scared_timer -= 1

        pac = self.state.pacman
        if ghost.x == pac.x and ghost.y == pac.y:
            if ghost.scared_timer > 0:
                self.state.score += 200
                ghost.x, ghost.y = 1, 1
                ghost.scared_timer = 0
            else:
                self.state.lose = True


    def apply_action(self, agent_idx: int, action: str):
        self.last_actions[agent_idx] = action

        if agent_idx == 0:
            self.move_pacman(action)
        else:
            self.move_ghosts(agent_idx - 1, action)

        return True

    def draw_ui_tick(self):
        if self.display:
            self.display.update(self.state)

    def check_game_over(self) -> bool:
        if self.state.win or self.state.lose:
            if self.display:
                self.display.finish()
            return True
        return False

    def draw_ui(self):
        if self.display:
            self.display.update(self.state)
        else:
            print(f"Score: {self.state.score} | Last actions: {self.last_actions}")

    def update_score(self, delta: float):
        self.state.score += delta
        self.draw_ui()
