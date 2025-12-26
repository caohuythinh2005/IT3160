import os
import random
from collections import deque

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from base.pacman_agent import PacmanAgent
from envs.directions import Directions
import envs.layouts as layouts

CHECKPOINT_DIR = "checkpoints"
CHECKPOINT_FILE = os.path.join(CHECKPOINT_DIR, "pacman_dqn_latest.pth")


class QNetwork(nn.Module):
    def __init__(self, input_shape, num_agents_features, action_size):
        super(QNetwork, self).__init__()
        self.conv1 = nn.Conv2d(input_shape[0], 16, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
        conv_out_size = 32 * input_shape[1] * input_shape[2]
        self.agent_fc1 = nn.Linear(num_agents_features, 64)
        self.agent_fc2 = nn.Linear(64, 64)
        self.fc1 = nn.Linear(conv_out_size + 64, 256)
        self.fc2 = nn.Linear(256, action_size)

    def forward(self, matrix_tensor, agent_tensor):
        x = F.relu(self.conv1(matrix_tensor))
        x = F.relu(self.conv2(x))
        x = x.view(x.size(0), -1)
        a = F.relu(self.agent_fc1(agent_tensor))
        a = F.relu(self.agent_fc2(a))
        combined = torch.cat([x, a], dim=1)
        combined = F.relu(self.fc1(combined))
        return self.fc2(combined)


class DQNPacmanAgent(PacmanAgent):
    def __init__(self, index=0, state_shape=(1, 11, 20), action_size=4, max_ghosts=4):
        super().__init__(index)
        print(f"[{index}] Init DQN Agent")
        os.makedirs(CHECKPOINT_DIR, exist_ok=True)
        print(f"[{index}] Checkpoint dir ready: {CHECKPOINT_DIR}")
        self.state_shape = state_shape
        self.actions_list = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]
        self.max_ghosts = max_ghosts
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.9995
        self.batch_size = 64
        self.memory = deque(maxlen=30000)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[{index}] Device: {self.device}")
        num_agents_features = 2 + max_ghosts * 3  
        self.model = QNetwork(state_shape, num_agents_features, action_size).to(self.device)
        self.target_model = QNetwork(state_shape, num_agents_features, action_size).to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.00025)
        self.criterion = nn.MSELoss()
        self.total_steps = 0
        self.episode_count = 0
        self.accumulated_loss = []
        latest_ckpt = self._get_latest_checkpoint()
        if latest_ckpt:
            print(f"[{index}] Found latest checkpoint: {latest_ckpt}")
            self.load_checkpoint(latest_ckpt)
            print(
                f"[{index}] Loaded | EP={self.episode_count} "
                f"| Steps={self.total_steps} | Eps={self.epsilon:.4f}"
            )
        else:
            print(f"[{index}] No checkpoint found, training from scratch")
            self.update_target()

    def _get_latest_checkpoint(self):
        return CHECKPOINT_FILE if os.path.exists(CHECKPOINT_FILE) else None

    def load_checkpoint(self, path):
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.target_model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint.get('epsilon', self.epsilon)
        self.total_steps = checkpoint.get('total_steps', 0)
        self.episode_count = checkpoint.get('episode', 0)

    def save_checkpoint(self):
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'total_steps': self.total_steps,
            'episode': self.episode_count
        }, CHECKPOINT_FILE)
        print(f"[DQN] CHECKPOINT SAVED -> {CHECKPOINT_FILE}")

    def _state_to_tensor(self, gameState):
        H, W = self.state_shape[1], self.state_shape[2]
        matrix = gameState.object_matrix.astype(np.float32) / float(layouts.WALL)
        matrix_tensor = torch.from_numpy(matrix).unsqueeze(0).unsqueeze(0) 
        matrix_tensor = F.interpolate(matrix_tensor, size=(H, W), mode='nearest')
        features = []
        px, py = gameState.getPacmanPosition()
        features += [px / W, py / H]
        for g in gameState.ghosts:
            features += [g.x / W, g.y / H, g.scared_timer / 40.0]
        while len(features) < 2 + self.max_ghosts * 3:
            features.append(0.0)

        agent_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0) 

        return matrix_tensor.to(self.device), agent_tensor.to(self.device)

    def getAction(self, gameState) -> str:
        legal = gameState.getLegalActions(self.index) if hasattr(gameState, 'getLegalActions') else ['North', 'South', 'East', 'West']
        if not legal:
            return Directions.LEFT

        if random.random() <= self.epsilon:
            return random.choice(legal)

        matrix_tensor, agent_tensor = self._state_to_tensor(gameState)
        with torch.no_grad():
            q_values = self.model(matrix_tensor, agent_tensor)

        sorted_indices = torch.argsort(q_values, descending=True).squeeze().tolist()
        if isinstance(sorted_indices, int):
            sorted_indices = [sorted_indices]

        for idx in sorted_indices:
            action = self.actions_list[idx]
            if action in legal:
                return action
        return random.choice(legal)

    def update_policy(self, state, action, reward, next_state, done):
        if action in self.actions_list:
            self.memory.append((state, self.actions_list.index(action), reward, next_state, done))

        self.total_steps += 1
        loss_val = self.train()
        if loss_val:
            self.accumulated_loss.append(loss_val)

        if self.total_steps % 500 == 0:
            print(f"[DQN] Update target network @ step {self.total_steps}")
            self.update_target()

        if done:
            self.episode_count += 1
            self.log_training()
            self.save_checkpoint()

    def train(self):
        if len(self.memory) < self.batch_size:
            return None

        minibatch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*minibatch)

        matrix_batch = torch.cat([self._state_to_tensor(s)[0] for s in states])
        agent_batch = torch.cat([self._state_to_tensor(s)[1] for s in states])
        next_matrix_batch = torch.cat([self._state_to_tensor(ns)[0] for ns in next_states])
        next_agent_batch = torch.cat([self._state_to_tensor(ns)[1] for ns in next_states])

        reward_batch = torch.tensor(rewards, dtype=torch.float32).to(self.device)
        action_batch = torch.tensor(actions, dtype=torch.long).to(self.device)
        done_batch = torch.tensor(dones, dtype=torch.float32).to(self.device)

        current_q = self.model(matrix_batch, agent_batch).gather(1, action_batch.unsqueeze(1))

        with torch.no_grad():
            max_next_q = self.target_model(next_matrix_batch, next_agent_batch).max(1)[0]
            target_q = reward_batch + (1 - done_batch) * self.gamma * max_next_q

        loss = self.criterion(current_q.squeeze(), target_q)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        return loss.item()

    def update_target(self):
        self.target_model.load_state_dict(self.model.state_dict())

    def log_training(self):
        avg_loss = np.mean(self.accumulated_loss) if self.accumulated_loss else 0
        print(
            f"[DQN] EP={self.episode_count} | "
            f"Steps={self.total_steps} | "
            f"Loss={avg_loss:.4f} | "
            f"Eps={self.epsilon:.4f}"
        )
        self.accumulated_loss = []
