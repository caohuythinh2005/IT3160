import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from base.agent import Agent
from base.pacman_agent import PacmanAgent
from envs.game_state import GameState
from envs.directions import Directions
import random
import msvcrt

class KeyboardPacmanAgent(PacmanAgent):
    def __init__(self, index=0):
        super().__init__(index)
        self.next_action = None

    def getAction(self, gameState):
        if msvcrt.kbhit():
            key = msvcrt.getch()
            
            if key == b'\xe0':
                key2 = msvcrt.getch()
                arrow_map = {
                    b'H': 'NORTH',  # mũi tên lên
                    b'P': 'SOUTH',  # mũi tên xuống
                    b'K': 'WEST',   # mũi tên trái
                    b'M': 'EAST'    # mũi tên phải
                }
                if key2 in arrow_map:
                    self.next_action = arrow_map[key2]

            # WASD
            key_map = {b'w':'NORTH', b's':'SOUTH', b'a':'WEST', b'd':'EAST'}
            if key in key_map:
                self.next_action = key_map[key]

        action = self.next_action
        self.next_action = None
        return action
