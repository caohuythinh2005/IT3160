from typing import Any, Optional

class Agent:
    def __init__(self, index: int = 0):
        self.index = index

    def getAction(self, gameState: Any) -> str:
        raise NotImplementedError("This method should be overridden by subclasses")
    
    def registerInitialState(self, gameState: Any) -> None:
        return None
    
    def final(self, gameState: Any) -> None:
        return None
    