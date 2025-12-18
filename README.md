project/
├── pyproject.toml          # (optional) chuẩn hoá package
├── README.md

├── src/
│   ├── frontend/           # UI / Controller / Socket server
│   │   ├── __init__.py
│   │   ├── socket_server.py
│   │   └── socket_client.py
│   │
│   ├── workers/            # Process chạy độc lập (IO only)
│   │   ├── __init__.py
│   │   ├── agent_worker.py
│   │   └── state_adapter.py
│   │
│   ├── agents/             # AI agents (KHÔNG socket, KHÔNG sleep)
│   │   ├── __init__.py
│   │   ├── base.py         # Agent interface
│   │   ├── factory.py
│   │   │
│   │   ├── rule_based/
│   │   │   ├── __init__.py
│   │   │   ├── random_agent.py
│   │   │   └── directional_agent.py
│   │   │
│   │   ├── rl/
│   │   │   ├── __init__.py
│   │   │   ├── dqn_wrapper.py
│   │   │   ├── ppo_wrapper.py
│   │   │   └── common.py
│   │   │
│   │   └── pacman/         # Code gốc / legacy (model, utils)
│   │       ├── __init__.py
│   │       ├── dqn_agent.py
│   │       └── networks.py
│   │
│   ├── envs/               # (optional) Env abstraction
│   │   ├── __init__.py
│   │   ├── base_env.py
│   │   └── pacman_env.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── geometry.py
│   │   ├── logging.py
│   │   └── timing.py
│   │
│   └── configs/
│       ├── agents.yaml
│       └── env.yaml
│
├── scripts/
│   ├── run_worker.sh
│   ├── train_dqn.py
│   └── evaluate.py
│
├── checkpoints/
│   └── dqn/
│
└── tests/
    ├── test_agents.py
    └── test_state_adapter.py
