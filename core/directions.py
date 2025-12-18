class Directions:
    NORTH = "North"
    SOUTH = "South"
    EAST = "East"
    WEST = "West"

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

    _dỉrectionsAsList = list(_directions.values())

    @staticmethod
    def getLegalActions(config, walls):
        pass

    @staticmethod
    def getPossibleActions(config, walls):
        pass