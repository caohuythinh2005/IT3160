import random
from agent import Agent
from core.directions import Directions
from typing import Any

class RandomAgent(Agent):
    def getAction(self, gameState: Any) -> str:
        legalMoves = gameState.getLegalActions(self.index)
        return random.choice(legalMoves)
