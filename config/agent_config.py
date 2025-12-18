AGENT_SETTINGS = {
    0: {
        "name": "Pacman",
        "available_algos": ["Keyboard", "Random"],
        "default": "Keyboard"
    },
    1: {
        "name": "Ghost 1",
        "available_algos": ["Random", "Directional"],
        "default": "Random"
    },
    2: {
        "name": "Ghost 2",
        "available_algos": ["Random", "Directional"],
        "default": "Directional"
    }
}

ALGO_MAP = {
    "keyboard": "keyboard_pacman",
    "random": "random_ghost",
    "directional": "directional_ghost",
}

def get_factory_algo_name(ui_algo_name):
    return ALGO_MAP.get(ui_algo_name.lower(), ui_algo_name.lower())