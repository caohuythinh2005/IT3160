from dataclasses import dataclass, field
import numpy as np
from typing import List

from envs.directions import Actions
from envs import layouts

@dataclass
class AgentInfo:
    x: int
    y: int
    dir: int = 0

@dataclass
class GhostInfo(AgentInfo):
    scared_timer: float = 0.0

@dataclass
class GameState:
    object_matrix: np.ndarray
    pacman: AgentInfo
    ghosts: List[GhostInfo] = field(default_factory=list)
    score: float = 0.0
    win: bool = False
    lose: bool = False

    def copy(self) -> "GameState":
        return GameState(
            object_matrix=self.object_matrix.copy(),
            pacman=AgentInfo(self.pacman.x, self.pacman.y, self.pacman.dir),
            ghosts=[GhostInfo(g.x, g.y, g.dir, g.scared_timer) for g in self.ghosts],
            score=self.score,
            win=self.win,
            lose=self.lose
        )

    def getPacmanPosition(self):
        return self.pacman.x, self.pacman.y

    def getGhostPosition(self, i: int):
        return self.ghosts[i].x, self.ghosts[i].y

    def getAgentPosition(self, agent_index: int):
        if agent_index == 0:
            return self.getPacmanPosition()
        return self.getGhostPosition(agent_index - 1)

    def getLegalActions(self, agent_index: int):
        if agent_index == 0:
            pos = self.getPacmanPosition()
        else:
            pos = self.getGhostPosition(agent_index - 1)
        walls = self.object_matrix == layouts.WALL
        return Actions.getLegalActions(pos, walls)

    def ghost_scared_timer(self, i: int):
        return self.ghosts[i].scared_timer

    def is_ghost_scared(self, i: int):
        return self.ghosts[i].scared_timer > 0

    def num_ghosts(self):
        return len(self.ghosts)

    def is_wall(self, x, y):
        return self.object_matrix[y, x] == layouts.WALL

    def is_food(self, x, y):
        return self.object_matrix[y, x] == layouts.FOOD

    def is_capsule(self, x, y):
        return self.object_matrix[y, x] == layouts.CAPSULE

    def is_ghost(self, x, y):
        return any(g.x == x and g.y == y for g in self.ghosts)

    def has_food_or_capsule(self):
        return np.any(
            (self.object_matrix == layouts.FOOD) |
            (self.object_matrix == layouts.CAPSULE)
        )

    def update_win(self):
        if not self.has_food_or_capsule():
            self.win = True

    def getScore(self) -> float:
        return float(self.score)

    def isWin(self) -> bool:
        return self.win

    def isLose(self) -> bool:
        return self.lose

    def isGameOver(self) -> bool:
        return self.win or self.lose

    def getFood(self):
        return self.object_matrix == layouts.FOOD

    def getWalls(self):
        return self.object_matrix == layouts.WALL


def serialize_state(state: GameState) -> dict:
    return {
        "object_matrix": state.object_matrix.tolist(),
        "pacman": {
            "x": state.pacman.x,
            "y": state.pacman.y,
            "dir": state.pacman.dir
        },
        "ghosts": [
            {
                "x": g.x,
                "y": g.y,
                "dir": g.dir,
                "scared_timer": g.scared_timer
            } for g in state.ghosts
        ],
        "score": state.score,
        "win": state.win,
        "lose": state.lose
    }


def deserialize_state(d: dict) -> GameState:
    return GameState(
        object_matrix=np.array(d["object_matrix"]),
        pacman=AgentInfo(**d["pacman"]),
        ghosts=[GhostInfo(**g) for g in d["ghosts"]],
        score=d["score"],
        win=d["win"],
        lose=d["lose"]
    )
