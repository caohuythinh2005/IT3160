import sys
import os
import random
from base.ghost_agent import GhostAgent
from envs.game_state import GameState
from envs.directions import Directions, Actions

class SmartGhostAgent(GhostAgent):
    def __init__(self, index):
        super().__init__(index)
        
    def getAction(self, gameState: GameState) -> str:
        legal = gameState.getLegalActions(self.index)
        if not legal:
            return Directions.LEFT

        ghost_pos = gameState.getAgentPosition(self.index)
        pacman_pos = gameState.getPacmanPosition()
        is_scared = gameState.is_ghost_scared(self.index - 1) 

        target = pacman_pos

        distances = []
        for action in legal:
            dx, dy = Actions.directionToVector(action)
            next_x, next_y = ghost_pos[0] + dx, ghost_pos[1] + dy
            
            dist = abs(next_x - target[0]) + abs(next_y - target[1])
            distances.append((dist, action))

        if is_scared:
            best_action = max(distances, key=lambda x: x[0])[1]
            if random.random() < 0.2:
                return random.choice(legal)
        else:
            distances.sort(key=lambda x: x[0])
            
            if random.random() < 0.8:
                best_action = distances[0][1]
            else:
                best_action = random.choice(legal)

        return best_action