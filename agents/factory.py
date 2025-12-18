from agents.ghosts.directional_ghost_agent import DirectionalGhostAgent
from agents.ghosts.random_ghost_agent import RandomGhostAgent
from config.agent_config import get_factory_algo_name
from agents.pacman.random_pacman_agent import RandomPacManAgent

def make_agent(algo: str, index: int):
    internal_algo = get_factory_algo_name(algo)
    
    if internal_algo == "random_ghost":
        return RandomGhostAgent(index)
    elif internal_algo == "directional_ghost":
        return DirectionalGhostAgent(index)
    elif internal_algo == "random_pacman":
        return RandomPacManAgent(index)
    else:
        raise ValueError(f"Unknown agent algo '{internal_algo}' (original: '{algo}')")