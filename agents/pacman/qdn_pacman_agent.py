import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
import random
import os
import time
from collections import deque
from base.pacman_agent import PacmanAgent
from envs.directions import Directions, Actions
import envs.layouts as layouts

class QNetwork(nn.Module):
    def __init__(self, input_shape, action_size):
        super(QNetwork, self).__init__()
        self.conv1 = nn.Conv2d(input_shape[0], 16, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
        self.flatten_size = 32 * input_shape[1] * input_shape[2]
        self.fc1 = nn.Linear(self.flatten_size, 256)
        self.fc2 = nn.Linear(256, action_size)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        return self.fc2(x)

class DQNPacmanAgent(PacmanAgent):
    def __init__(self, index=0, state_shape=(1, 15, 20), action_size=4):
        super().__init__(index)
        self.state_shape = state_shape
        self.actions_list = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]
        
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.9995
        self.batch_size = 64
        self.memory = deque(maxlen=30000)
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = QNetwork(state_shape, action_size).to(self.device)
        self.target_model = QNetwork(state_shape, action_size).to(self.device)
        self.update_target()
        
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.00025)
        self.criterion = nn.MSELoss()

        self.total_steps = 0
        self.episode_count = 0
        self.accumulated_loss = []

    def _state_to_tensor(self, gameState):
        matrix = gameState.object_matrix.astype(np.float32) / float(layouts.WALL)
        return torch.from_numpy(matrix).unsqueeze(0).unsqueeze(0).to(self.device)

    def getAction(self, gameState) -> str:
        legal = gameState.getLegalActions(self.index)
        if not legal: return Directions.STOP

        if np.random.rand() <= self.epsilon:
            return random.choice(legal)
        
        state_t = self._state_to_tensor(gameState)
        with torch.no_grad():
            q_values = self.model(state_t)
        
        sorted_indices = torch.argsort(q_values, descending=True).squeeze().tolist()
        for idx in sorted_indices:
            action = self.actions_list[idx]
            if action in legal: return action
        return random.choice(legal)

    def update_policy(self, state, action, reward, next_state, done):
        if action in self.actions_list:
            action_idx = self.actions_list.index(action)
            self.memory.append((state, action_idx, reward, next_state, done))
        
        self.total_steps += 1
        loss_val = self.train()
        if loss_val: self.accumulated_loss.append(loss_val)
        
        if self.total_steps % 500 == 0:
            self.update_target()
            
        if done:
            self.episode_count += 1
            self.log_training(reward)
            if self.episode_count % 50 == 0:
                self.save_checkpoint(f"pacman_dqn_ep{self.episode_count}.pth")

    def train(self):
        if len(self.memory) < self.batch_size:
            return None

        minibatch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*minibatch)
        
        state_batch = torch.cat([self._state_to_tensor(s) for s in states])
        next_state_batch = torch.cat([self._state_to_tensor(ns) for ns in next_states])
        reward_batch = torch.tensor(rewards, dtype=torch.float32).to(self.device)
        action_batch = torch.tensor(actions, dtype=torch.long).to(self.device)
        done_batch = torch.tensor(dones, dtype=torch.float32).to(self.device)

        current_q = self.model(state_batch).gather(1, action_batch.unsqueeze(1))
        with torch.no_grad():
            max_next_q = self.target_model(next_state_batch).max(1)[0]
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

    def log_training(self, last_reward):
        avg_loss = np.mean(self.accumulated_loss) if self.accumulated_loss else 0
        print(f"EP: {self.episode_count:<4} | Steps: {self.total_steps:<6} | Loss: {avg_loss:.4f} | Eps: {self.epsilon:.3f}")
        self.accumulated_loss = []

    def save_checkpoint(self, filename):
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'total_steps': self.total_steps,
            'episode': self.episode_count
        }, filename)
        print(f"--- CHECKPOINT SAVED: {filename} ---")

    def load_checkpoint(self, filename):
        if os.path.exists(filename):
            ckpt = torch.load(filename)
            self.model.load_state_dict(ckpt['model_state_dict'])
            self.optimizer.load_state_dict(ckpt['optimizer_state_dict'])
            self.epsilon = ckpt['epsilon']
            self.total_steps = ckpt['total_steps']
            self.episode_count = ckpt['episode']
            self.update_target()
            print(f"--- CHECKPOINT LOADED: {filename} ---") 