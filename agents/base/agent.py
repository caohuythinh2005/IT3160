from typing import Any
from envs.game_state import GameState

class Agent:
    def __init__(self, index: int = 0):
        self.index = index

    def getAction(self, gameState: GameState) -> str:
        raise NotImplementedError("This method should be overridden by subclasses")
    
    def registerInitialState(self, gameState: GameState) -> None:
        return None
    
    def final(self, gameState: GameState) -> None:
        return None
