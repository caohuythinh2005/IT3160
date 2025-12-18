from base.agent import Agent
from envs.game_state import GameState
from envs.directions import Directions
import random

class PacmanAgent(Agent):
    def getAction(self, gameState: GameState) -> str:
        legal = gameState.getLegalActions(self.index)
        if not legal:
            return random.choice([Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST])
        return random.choice(legal)

    def registerInitialState(self, gameState: GameState) -> None:
        self.start_state = gameState.copy()
        return None
