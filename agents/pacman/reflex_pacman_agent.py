from base.pacman_agent import PacmanAgent
from envs.game_state import GameState
from envs.directions import Directions, Actions
import numpy as np
import envs.layouts as layouts

class ReflexPacmanAgent(PacmanAgent):
    def __init__(self, index):
        super().__init__(index)

    def getAction(self, gameState: GameState) -> str:
        legal = gameState.getLegalActions(self.index)
        
        best_score = -float('inf')
        best_action = legal[0]
        
        for action in legal:
            score = self.evaluationFunction(gameState, action)
            if score > best_score:
                best_score = score
                best_action = action
        return best_action

    def evaluationFunction(self, gameState, action):
        from envs.layouts import FOOD, GHOST1
        px, py = gameState.getPacmanPosition()
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = px + dx, py + dy
        
        for i in range(gameState.num_ghosts()):
            gx, gy = gameState.getGhostPosition(i)
            ghost_dist = abs(next_x - gx) + abs(next_y - gy)
            if ghost_dist <= 1:
                return -10000
            
        
        eval_score = 0
        if gameState.object_matrix[next_y, next_x] == FOOD:
            eval_score += 10
            
        food_indices = np.argwhere(gameState.object_matrix == FOOD)
        if len(food_indices) > 0:
            min_food_dist = min([abs(next_x - fx) + abs(next_y - fy) for fy, fx in food_indices])
            eval_score += 1.0 / (min_food_dist + 1)
            
        return eval_score