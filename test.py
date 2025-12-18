import numpy as np
from workers.state_adapter import adapt_state

# Fake raw_state giống format socket controller trả về
raw_state = {
    "object_matrix": [
        [1,1,1,1,1],
        [1,0,0,0,1],
        [1,0,4,0,1],  # 4 = pacman
        [1,0,0,5,1],  # 5 = ghost
        [1,1,1,1,1]
    ],
    "info_vector": [
        2, 2,   # pacman x,y
        3, 3,   # ghost1 x,y
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
    ],
    "score": 0,
    "win": False,
    "lose": False
}

agent_code = 4  # pacman
obs = adapt_state(raw_state, agent_code)

print("Pacman pos:", obs["position"])
print("Legal actions:", obs["legal_actions"])
print("Score:", obs["score"])
print("Done:", obs["done"])
