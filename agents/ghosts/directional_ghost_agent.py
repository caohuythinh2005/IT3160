import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from base.agent import Agent
from base.ghost_agent import GhostAgent
from envs.game_state import GameState
from envs.directions import Directions
import random

class DirectionalGhostAgent(GhostAgent):
    def __init__(self, index):
        super().__init__(index)
    def getAction(self, gameState: GameState) -> str:
        legal = gameState.getLegalActions(self.index)
        if not legal:
            return random.choice([Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST])

        ghost_x, ghost_y = gameState.getAgentPosition(self.index)
        pac_x, pac_y = gameState.getPacmanPosition()

        dx = pac_x - ghost_x
        dy = pac_y - ghost_y

        preferred = []
        if abs(dx) >= abs(dy):
            if dx > 0: preferred.append(Directions.EAST)
            elif dx < 0: preferred.append(Directions.WEST)
            if dy > 0: preferred.append(Directions.SOUTH)
            elif dy < 0: preferred.append(Directions.NORTH)
        else:
            if dy > 0: preferred.append(Directions.SOUTH)
            elif dy < 0: preferred.append(Directions.NORTH)
            if dx > 0: preferred.append(Directions.EAST)
            elif dx < 0: preferred.append(Directions.WEST)

        for action in preferred:
            if action in legal:
                return action

        return random.choice(legal)