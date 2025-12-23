from agents.ghosts.directional_ghost_agent import DirectionalGhostAgent
from agents.ghosts.random_ghost_agent import RandomGhostAgent
from config.agent_config import get_factory_algo_name
from agents.pacman.random_pacman_agent import RandomPacManAgent
from agents.pacman.greedy_pacman_agent import GreedyPacmanAgent
from agents.pacman.reflex_pacman_agent import ReflexPacmanAgent
from agents.ghosts.smart_ghost_agent import SmartGhostAgent
from agents.pacman.qdn_pacman_agent import DQNPacmanAgent

def make_agent(algo: str, index: int, **kwargs):
    internal_algo = get_factory_algo_name(algo)
    
    if internal_algo == "random_ghost":
        return RandomGhostAgent(index)
    elif internal_algo == "directional_ghost":
        return DirectionalGhostAgent(index)
    elif internal_algo == "random_pacman":
        return RandomPacManAgent(index)
    elif internal_algo == "greedy_pacman":
        return GreedyPacmanAgent(index)
    elif internal_algo == "reflex_pacman":
        return ReflexPacmanAgent(index)
    elif internal_algo == "smart_ghost":
        return SmartGhostAgent(index)
    elif internal_algo == "dqn_pacman":
        state_shape = kwargs.get("state_shape", (1, 11, 20))  
        return DQNPacmanAgent(index=index, state_shape=state_shape)
    elif internal_algo == "keyboard_pacman":
        from agents.pacman.keyboard_pacman_agent import KeyboardPacmanAgent
        return KeyboardPacmanAgent(index)
    else:
        raise ValueError(f"Unknown agent algo '{internal_algo}' (original: '{algo}')")
