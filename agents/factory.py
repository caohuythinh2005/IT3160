from agents.agent import Agent
from agents.directional_agent import DirectionalAgent
from agents.random_agent import RandomAgent

def make_agent(name: str, index: int = 0) -> Agent:
    name = name.lower()
    if name == "random":
        return RandomAgent(index)
    if name == "directional":
        return DirectionalAgent(index)
    else:
        raise ValueError(f"Unknown agent type: {name}")