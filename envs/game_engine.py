import numpy as np
from envs.game_state import GameState
from envs import layouts
from envs.directions import Actions, Directions
from config import point

class GameEngine:
    @staticmethod
    def get_ghost_id(ghost_idx: int) -> int:
        ghost_ids = [layouts.GHOST1, layouts.GHOST2, layouts.GHOST3, layouts.GHOST4]
        return ghost_ids[ghost_idx]

    @staticmethod
    def get_ghost_spawn(ghost_idx: int) -> tuple[int, int]:
        ghost_spawns = [(1, 1), (3, 1), (1, 3), (3, 3)]
        return ghost_spawns[ghost_idx] if ghost_idx < len(ghost_spawns) else (1, 1)

    @staticmethod
    def apply_action(state: GameState, agent_idx: int, action: str):
        if state.win or state.lose or action not in Directions.ALL:
            return

        if agent_idx == 0:
            GameEngine.move_pacman(state, action)
        else:
            GameEngine.move_ghost(state, agent_idx - 1, action)

    @staticmethod
    def move_pacman(state: GameState, action: str):
        pac = state.pacman
        dx, dy = Actions.directionToVector(action)
        nx, ny = int(pac.x + dx), int(pac.y + dy)
        H, W = state.object_matrix.shape

        if not (0 <= nx < W and 0 <= ny < H) or state.is_wall(nx, ny):
            return

        target = state.object_matrix[ny, nx]
        if target == layouts.FOOD:
            state.score += point.FOOD_REWARD
            state.object_matrix[ny, nx] = layouts.EMPTY
        elif target == layouts.CAPSULE:
            state.score += point.CAPSULE_REWARD
            state.object_matrix[ny, nx] = layouts.EMPTY
            for g in state.ghosts:
                g.scared_timer = 40

        pac.x, pac.y = nx, ny
        pac.dir = action

        for i, g in enumerate(state.ghosts):
            if int(g.x) == pac.x and int(g.y) == pac.y:
                GameEngine._resolve_collision(state, i)
                if state.lose: return

        if not np.any(np.isin(state.object_matrix, [layouts.FOOD, layouts.CAPSULE])):
            state.win = True

    @staticmethod
    def move_ghost(state: GameState, ghost_idx: int, action: str):
        ghost = state.ghosts[ghost_idx]
        dx, dy = Actions.directionToVector(action)
        nx, ny = int(ghost.x + dx), int(ghost.y + dy)
        H, W = state.object_matrix.shape

        if 0 <= nx < W and 0 <= ny < H and not state.is_wall(nx, ny):
            ghost.x, ghost.y = nx, ny
            ghost.dir = action

        if ghost.scared_timer > 0:
            ghost.scared_timer -= 1

        pac = state.pacman
        if int(ghost.x) == int(pac.x) and int(ghost.y) == int(pac.y):
            GameEngine._resolve_collision(state, ghost_idx)

    @staticmethod
    def _resolve_collision(state: GameState, ghost_idx: int):
        ghost = state.ghosts[ghost_idx]
        spawn_x, spawn_y = GameEngine.get_ghost_spawn(ghost_idx)

        if ghost.scared_timer > 0:
            state.score += point.GHOST_EAT_REWARD
            ghost.x, ghost.y = spawn_x, spawn_y
            ghost.scared_timer = 0
        else:
            state.lose = True