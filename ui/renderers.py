from abc import ABC, abstractmethod
from typing import Tuple
from envs.game_state import GameState

class BaseDisplay(ABC):
    def __init__(self, zoom: float = 1.0, frame_time: float = 0.0):
        self.zoom = zoom
        self.frame_time = frame_time

    @abstractmethod
    def initialize(self, state: GameState) -> None:
        """Initialize the display with the given game state."""
        pass

    @abstractmethod
    def update(self, state: GameState) -> None:
        """Update the display according to the new game state."""
        pass

    @abstractmethod
    def finish(self) -> None:
        """Cleanup resources when display is finished."""
        pass


# Renderer interface
class Renderer(ABC):
    @abstractmethod
    def render(self, state: GameState) -> None:
        """Render a frame based on the current game state."""
        pass


# Food-specific renderer
class FoodRenderer(Renderer, ABC):
    @abstractmethod
    def clear_food(self, position: Tuple[int, int]) -> None:
        """Remove food from the given position on the display."""
        pass


# Info pane for score/messages
class InfoPane(ABC):
    @abstractmethod
    def display_score(self, score: float) -> None:
        """Display the current score."""
        pass

    @abstractmethod
    def display_message(self, message: str) -> None:
        """Display a message to the player."""
        pass
