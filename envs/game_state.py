from dataclasses import dataclass
import numpy as np
from typing import List, Tuple, Any, Optional


@dataclass
class GameState:
    object_matrix: np.ndarray
    infor_vector: np.ndarray
    scrore: float
    win: bool = False
    lose: bool = False
    
    def copy(self) -> "GameState":
        return GameState(
            object_matrix=self.object_matrix.copy(),
            infor_vector=self.infor_vector.copy(),
            scrore=self.scrore,
            win=self.win,
            lose=self.lose,
        )
    
    # ---- Query helpers ----
    def pacmman_pos(self):
        return int(self.infor_vector[0]), int(self.infor_vector[1])
    
    def ghost_pos(self, i: int):
        idx = 2 + i * 2
        return int(self.infor_vector[idx]), int(self.infor_vector[idx + 1])
    
    def num_food_left(self):
        return int(self.infor_vector[17])
    
    def isWin(self):
        return self.win
    
    def isLose(self):
        return self.lose
    


    