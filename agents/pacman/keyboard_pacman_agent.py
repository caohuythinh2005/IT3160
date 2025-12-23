import threading
import time
import random
import msvcrt
import sys

from base.pacman_agent import PacmanAgent
from envs.game_state import GameState
from envs.directions import Directions

class KeyboardPacmanAgent(PacmanAgent):
    def __init__(self, index):
        super().__init__(index)
        self.desired_move = None
        self.last_real_move = None 
        self.running = True
        self.listener_thread = threading.Thread(target=self.check_keyboard, daemon=True)
        self.listener_thread.start()
        
        print("Keyboard Agent Started! Use W A S D to move.")

    def check_keyboard(self):

        while self.running:
            if msvcrt.kbhit():
                try:
                    key = msvcrt.getch().decode('utf-8').lower()
                    if key == 'w': self.desired_move = Directions.NORTH
                    elif key == 's': self.desired_move = Directions.SOUTH
                    elif key == 'a': self.desired_move = Directions.WEST
                    elif key == 'd': self.desired_move = Directions.EAST
                except Exception:
                    pass
            time.sleep(0.005)

    def getAction(self, gameState: GameState) -> str:
        legal = gameState.getLegalActions(self.index)
        if not legal:
            return Directions.NORTH 
        if self.desired_move in legal:
            self.last_real_move = self.desired_move 
            return self.desired_move


        if self.last_real_move in legal:
            return self.last_real_move

        choice = random.choice(legal)
        self.last_real_move = choice 
        return choice

    def __del__(self):
        self.running = False