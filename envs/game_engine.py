import numpy as np
from envs.game_state import GameState, GhostInfo
from envs import layouts
from envs.directions import Directions, Actions

class GameEngine:
    @staticmethod
    def get_ghost_id(ghost_idx: int) -> int:
        ghost_ids = [layouts.GHOST1, layouts.GHOST2, layouts.GHOST3, layouts.GHOST4]
        return ghost_ids[ghost_idx]

    @staticmethod
    def get_ghost_spawn(ghost_idx: int) -> tuple[int, int]:
        ghost_spawns = [(1, 1), (3, 1), (1, 3), (3, 3)]  # chỉnh theo map của bạn
        return ghost_spawns[ghost_idx]


    @staticmethod
    def apply_action(state: GameState, agent_idx: int, action: str):
        if state.win or state.lose or action not in Directions.ALL:
            return
        if agent_idx == 0:
            GameEngine.move_pacman(state, action)
        else:
            GameEngine.move_ghost(state, agent_idx - 1, action)

    # -------------------------
    # Pacman movement
    # -------------------------
    @staticmethod
    def move_pacman(state: GameState, action: str):
        pac = state.pacman
        dx, dy = Actions.directionToVector(action)
        nx, ny = pac.x + dx, pac.y + dy
        H, W = state.object_matrix.shape

        if 0 <= nx < W and 0 <= ny < H and not state.is_wall(nx, ny):
            target = state.object_matrix[ny, nx]

            if target == layouts.FOOD:
                state.score += 10
            elif target == layouts.CAPSULE:
                state.score += 50
                for g in state.ghosts:
                    g.scared_timer = 40

            # Cập nhật vị trí Pacman
            state.object_matrix[pac.y, pac.x] = layouts.EMPTY
            pac.x, pac.y = nx, ny
            state.object_matrix[ny, nx] = layouts.PACMAN

            # Kiểm tra va chạm với Ghosts
            for i, g in enumerate(state.ghosts):
                if g.x == pac.x and g.y == pac.y:
                    GameEngine._resolve_collision(state, i)

            if not np.any((state.object_matrix == layouts.FOOD) | (state.object_matrix == layouts.CAPSULE)):
                state.win = True


    @staticmethod
    def move_ghost(state: GameState, ghost_idx: int, action: str):
        ghost = state.ghosts[ghost_idx]
        dx, dy = Actions.directionToVector(action)
        nx, ny = ghost.x + dx, ghost.y + dy
        H, W = state.object_matrix.shape

        if 0 <= nx < W and 0 <= ny < H and not state.is_wall(nx, ny):
            state.object_matrix[ghost.y, ghost.x] = layouts.EMPTY
            ghost.x, ghost.y = nx, ny
            state.object_matrix[ny, nx] = GameEngine.get_ghost_id(ghost_idx)

        if ghost.scared_timer > 0:
            ghost.scared_timer -= 1

        # Kiểm tra va chạm với Pacman
        pac = state.pacman
        if ghost.x == pac.x and ghost.y == pac.y:
            GameEngine._resolve_collision(state, ghost_idx)

    # -------------------------
    # Collision
    # -------------------------
    @staticmethod
    def _resolve_collision(state: GameState, ghost_idx: int):
        ghost = state.ghosts[ghost_idx]
        pac = state.pacman
        ghost_id = GameEngine.get_ghost_id(ghost_idx)
        spawn_x, spawn_y = GameEngine.get_ghost_spawn(ghost_idx)

        if ghost.scared_timer > 0:
            # Pacman ăn Ghost
            state.score += 200
            # Xóa ghost cũ
            state.object_matrix[ghost.y, ghost.x] = layouts.EMPTY
            # Reset ghost về spawn
            ghost.x, ghost.y = spawn_x, spawn_y
            ghost.scared_timer = 0
            state.object_matrix[spawn_y, spawn_x] = ghost_id
        else:
            # Ghost ăn Pacman → dừng game
            state.lose = True
