AGENT_SETTINGS = {
    0: {
        "name": "Pacman",
        "available_algos": ["KeyboardPacman", "RandomPacman", "GreedyPacman", "ReflexPacman", "DQNPacman"],
        "default": "KeyboardPacman"
    },
    1: {
        "name": "Ghost 1",
        "available_algos": ["RandomGhost", "DirectionalGhost", "SmartGhost"],
        "default": "RandomGhost"
    },
    2: {
        "name": "Ghost 2",
        "available_algos": ["RandomGhost", "DirectionalGhost", "SmartGhost"],
        "default": "RandomGhost"
    }
}

ALGO_MAP = {
    "randompacman": "random_pacman",
    "greedypacman": "greedy_pacman",
    "reflexpacman": "reflex_pacman",
    "randomghost": "random_ghost",
    "directionalghost": "directional_ghost",
    "smartghost": "smart_ghost",
    "dqnpacman": "dqn_pacman",
    "keyboardpacman": "keyboard_pacman"
}

def get_factory_algo_name(ui_algo_name):
    return ALGO_MAP.get(ui_algo_name.lower(), ui_algo_name.lower())