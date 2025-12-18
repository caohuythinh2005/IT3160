from dataclasses import dataclass
import numpy as np

@dataclass
class GameState:
    object_matrix: np.ndarray
    info_vector: np.ndarray
    score: float
    win: bool = False
    lose: bool = False

    def copy(self) -> "GameState":
        return GameState(
            object_matrix=self.object_matrix.copy(),
            info_vector=self.info_vector.copy(),
            score=self.score,
            win=self.win,
            lose=self.lose,
        )

    # ---- Query helpers ----
    def pacman_pos(self):
        return int(self.info_vector[0]), int(self.info_vector[1])

    def ghost_pos(self, i: int):
        idx = 2 + i * 2
        return int(self.info_vector[idx]), int(self.info_vector[idx + 1])

    def num_food_left(self):
        return int(self.info_vector[17])

    def isWin(self):
        return self.win

    def isLose(self):
        return self.lose
