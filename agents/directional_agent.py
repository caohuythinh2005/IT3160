from typing import Any, Dict
import random
from agents.agent import Agent
from envs.directions import Directions

class DirectionalAgent(Agent):

    def getAction(self, observation: Dict[str, Any]) -> str:
        pos = observation.get("position")
        legal = observation.get("legal_actions", [])

        if not pos or not legal:
            return random.choice([Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST])

        gs = observation.get("game_state")
        if gs is None:
            return random.choice(legal)

        pac_pos = gs.pacmman_pos()
        x, y = pos
        px, py = pac_pos

        dx = px - x
        dy = py - y

        candidates = []
        if abs(dx) >= abs(dy):
            if dx > 0:
                candidates.append(Directions.EAST)
            elif dx < 0:
                candidates.append(Directions.WEST)
            if dy > 0:
                candidates.append(Directions.SOUTH)
            elif dy < 0:
                candidates.append(Directions.NORTH)
        else:
            if dy > 0:
                candidates.append(Directions.SOUTH)
            elif dy < 0:
                candidates.append(Directions.NORTH)
            if dx > 0:
                candidates.append(Directions.EAST)
            elif dx < 0:
                candidates.append(Directions.WEST)

        for action in candidates:
            if action in legal:
                return action

        return random.choice(legal)
