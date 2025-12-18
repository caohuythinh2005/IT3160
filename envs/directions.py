from typing import Tuple, List, Any, Dict
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class Directions:
    NORTH = "North"
    SOUTH = "South"
    EAST = "East"
    WEST = "West"

    ALL = [NORTH, SOUTH, EAST, WEST]

    LEFT = {
        NORTH: WEST,
        WEST: SOUTH,
        SOUTH: EAST,
        EAST: NORTH,
    }

    RIGHT = {
        NORTH: EAST,
        EAST: SOUTH,
        SOUTH: WEST,
        WEST: NORTH,
    }

    REVERSE = {
        NORTH: SOUTH,
        SOUTH: NORTH,
        EAST: WEST,
        WEST: EAST,
    }

class Actions:
    _directions = {
        Directions.NORTH: (0, -1),
        Directions.SOUTH: (0, 1),
        Directions.EAST: (1, 0),
        Directions.WEST: (-1, 0),
    }

    _directionsAsList = list(_directions.items())

    @staticmethod
    def directionToVector(direction: str) -> Tuple[int, int]:
        return Actions._directions[direction]
    
    @staticmethod
    def getPossibleActions(
        pos : Tuple[int, int],
        walls,
    ) -> List[str]:
        x, y = pos
        H, W = walls.shape

        possible: List[str] = []

        for direction, (dx, dy) in Actions._dỉrectionsAsList:
            nx, ny = x + dx, y + dy
            if nx < 0 or ny < 0 or nx >= W or ny >= H:
                continue

            if walls[ny, nx]:
                continue

            possible.append(direction)

        return possible
    

    @staticmethod
    def getLegalActions(pos: Tuple[int, int], walls) -> List[str]:
        return Actions.getPossibleActions(pos, walls)
        

