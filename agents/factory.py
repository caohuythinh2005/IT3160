from agents.ghosts.directional_ghost_agent import DirectionalGhostAgent
from agents.ghosts.random_ghost_agent import RandomGhostAgent
from agents.pacman.keyboard_pacman_agent import KeyboardPacmanAgent
from config.agent_config import get_factory_algo_name

def make_agent(algo: str, index: int):
    internal_algo = get_factory_algo_name(algo)
    
    if internal_algo == "keyboard_pacman":
        return KeyboardPacmanAgent(index)
    elif internal_algo == "random_ghost":
        return RandomGhostAgent(index)
    elif internal_algo == "directional_ghost":
        return DirectionalGhostAgent(index)
    else:
        raise ValueError(f"Unknown agent algo '{internal_algo}' (original: '{algo}')")