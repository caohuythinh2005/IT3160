AGENT_SETTINGS = {
    0: {
        "name": "Pacman",
        "available_algos": ["RandomPacman"],
        "default": "RandomPacman"
    },
    1: {
        "name": "Ghost 1",
        "available_algos": ["RandomGhost", "DirectionalGhost"],
        "default": "RandomGhost"
    },
    2: {
        "name": "Ghost 2",
        "available_algos": ["RandomGhost", "DirectionalGhost"],
        "default": "DirectionalGhost"
    }
}

ALGO_MAP = {
    "randompacman": "random_pacman",
    "randomghost": "random_ghost",
    "directionalghost": "directional_ghost",
}

def get_factory_algo_name(ui_algo_name):
    return ALGO_MAP.get(ui_algo_name.lower(), ui_algo_name.lower())