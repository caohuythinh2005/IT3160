from base.agent import Agent
from base.ghost_agent import GhostAgent
from envs.game_state import GameState
from envs.directions import Directions
import random


class RandomGhostAgent(GhostAgent):
    def __init__(self, index):
        super().__init__(index)

    def getAction(self, gameState: GameState) -> str:
        legal = gameState.getLegalActions(self.index)
        if not legal:
            return random.choice([Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST])
        return random.choice(legal)
