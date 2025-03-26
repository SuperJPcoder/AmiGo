import torch
import torch.nn as nn
import torch.nn.functional as F

class PolicyValueNetwork(nn.Module):
    def __init__(self, board_size=5):
        super(PolicyValueNetwork, self).__init__()
        self.board_size = board_size

        # Convolutional Block
        self.conv1 = nn.Conv2d(1, 64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 64, kernel_size=3, padding=1)

        # Residual Block 1
        self.res1_conv1 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
        self.res1_conv2 = nn.Conv2d(64, 64, kernel_size=3, padding=1)

        # Residual Block 2
        self.res2_conv1 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
        self.res2_conv2 = nn.Conv2d(64, 64, kernel_size=3, padding=1)

        # Policy Head
        self.policy_conv = nn.Conv2d(64, 2, kernel_size=1)
        self.policy_fc = nn.Linear(2 * board_size * board_size, board_size * board_size)

        # Value Head
        self.value_conv = nn.Conv2d(64, 1, kernel_size=1)
        self.value_fc1 = nn.Linear(board_size * board_size, 64)
        self.value_fc2 = nn.Linear(64, 1)

    def forward(self, x):
        # Input shape: (batch_size, 1, board_size, board_size)
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))

        # Residual Block 1
        res1 = x
        x = F.relu(self.res1_conv1(x))
        x = self.res1_conv2(x)
        x += res1
        x = F.relu(x)

        # Residual Block 2
        res2 = x
        x = F.relu(self.res2_conv1(x))
        x = self.res2_conv2(x)
        x += res2
        x = F.relu(x)

        # Policy Head
        policy = F.relu(self.policy_conv(x))
        policy = policy.view(policy.size(0), -1)
        policy = F.softmax(self.policy_fc(policy), dim=1)

        # Value Head
        value = F.relu(self.value_conv(x))
        value = value.view(value.size(0), -1)
        value = F.relu(self.value_fc1(value))
        value = torch.tanh(self.value_fc2(value))

        return policy, value

    def predict(self, board_state):
        board_tensor = torch.tensor(board_state, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
        policy, value = self.forward(board_tensor)
        return policy.detach().numpy()[0], value.item()
