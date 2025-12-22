from base.pacman_agent import PacmanAgent
from envs.game_state import GameState
from envs.directions import Directions, Actions
import numpy as np
import envs.layouts as layouts

class GreedyPacmanAgent(PacmanAgent):
    def __init__(self, index):
        super().__init__(index)
        
    def getAction(self, gameState: GameState) -> str:
        legal = gameState.getLegalActions(self.index)
        if not legal: return Directions.WEST
        
        px, py = gameState.getPacmanPosition()
        
        
        food_indices = np.argwhere(gameState.object_matrix == layouts.FOOD)
        
        if len(food_indices) == 0:
            return np.random.choice(legal)

        best_action = legal[0]
        min_distance = float('inf')

        for action in legal:
            dx, dy = Actions.directionToVector(action)
            next_x, next_y = px + dx, py + dy
            
            for f_y, f_x in food_indices:
                dist = abs(next_x - f_x) + abs(next_y - f_y)
                if dist < min_distance:
                    min_distance = dist
                    best_action = action
                    
        return best_action