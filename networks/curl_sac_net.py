import numpy as np
from scipy import ndimage
from collections import OrderedDict

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Normal
from utils import torch_utils

LOG_SIG_MAX = 2
LOG_SIG_MIN = -20
epsilon = 1e-6

class CURLSACEncoder(nn.Module):
    def __init__(self, input_shape=(2, 64, 64), output_dim=1024):
        super().__init__()
        self.conv = torch.nn.Sequential(
            # 64x64
            nn.Conv2d(input_shape[0], 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            # 32x32
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            # 16x16
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            # 8x8
            nn.Conv2d(256, 512, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Flatten(),
            torch.nn.Linear(512 * 8 * 8, 1024),
            nn.ReLU(inplace=True),
            torch.nn.Linear(1024, output_dim),
        )

    def forward(self, x):
        return self.conv(x)

class CURLSACCritic(nn.Module):
    def __init__(self, encoder, encoder_output_dim=1024, hidden_dim=512, action_dim=5):
        super().__init__()
        self.encoder = encoder
        # Q1
        self.critic_fc_1 = torch.nn.Sequential(
            torch.nn.Linear(encoder_output_dim + action_dim, hidden_dim),
            nn.ReLU(inplace=True),
            torch.nn.Linear(hidden_dim, 1)
        )

        # Q2
        self.critic_fc_2 = torch.nn.Sequential(
            torch.nn.Linear(encoder_output_dim + action_dim, hidden_dim),
            nn.ReLU(inplace=True),
            torch.nn.Linear(hidden_dim, 1)
        )

    def forward(self, obs, act):
        obs_enc = self.encoder(obs)
        out_1 = self.critic_fc_1(torch.cat((obs_enc, act), dim=1))
        out_2 = self.critic_fc_2(torch.cat((obs_enc, act), dim=1))
        return out_1, out_2

class CURLSACGaussianPolicy(nn.Module):
    def __init__(self, encoder, encoder_output_dim=1024, hidden_dim=512, action_dim=5, action_space=None):
        super().__init__()
        self.encoder = encoder
        self.mean_linear = torch.nn.Sequential(
            torch.nn.Linear(encoder_output_dim, hidden_dim),
            nn.ReLU(inplace=True),
            torch.nn.Linear(hidden_dim, action_dim)
        )
        self.log_std_linear = torch.nn.Sequential(
            torch.nn.Linear(encoder_output_dim, hidden_dim),
            nn.ReLU(inplace=True),
            torch.nn.Linear(hidden_dim, action_dim)
        )

        # action rescaling
        if action_space is None:
            self.action_scale = torch.tensor(1.)
            self.action_bias = torch.tensor(0.)
        else:
            self.action_scale = torch.FloatTensor(
                (action_space.high - action_space.low) / 2.)
            self.action_bias = torch.FloatTensor(
                (action_space.high + action_space.low) / 2.)

        self.apply(torch_utils.weights_init)

    def forward(self, x):
        x = self.encoder(x)
        mean = self.mean_linear(x)
        log_std = self.log_std_linear(x)
        log_std = torch.clamp(log_std, min=LOG_SIG_MIN, max=LOG_SIG_MAX)
        return mean, log_std

    def sample(self, x):
        mean, log_std = self.forward(x)
        std = log_std.exp()
        normal = Normal(mean, std)
        x_t = normal.rsample()  # for reparameterization trick (mean + std * N(0,1))
        y_t = torch.tanh(x_t)
        action = y_t * self.action_scale + self.action_bias
        log_prob = normal.log_prob(x_t)
        # Enforcing Action Bound
        log_prob -= torch.log(self.action_scale * (1 - y_t.pow(2)) + epsilon)
        log_prob = log_prob.sum(1, keepdim=True)
        mean = torch.tanh(mean) * self.action_scale + self.action_bias
        return action, log_prob, mean


class CURL(nn.Module):
    """
    CURL
    """

    def __init__(self, z_dim, encoder, encoder_target):
        super(CURL, self).__init__()
        self.encoder = encoder

        self.encoder_target = encoder_target

        self.W = nn.Parameter(torch.rand(z_dim, z_dim))

    def encode(self, x, detach=False, ema=False):
        """
        CURLSACEncoder: z_t = e(x_t)
        :param x: x_t, x y coordinates
        :return: z_t, value in r2
        """
        if ema:
            with torch.no_grad():
                z_out = self.encoder_target(x)
        else:
            z_out = self.encoder(x)

        if detach:
            z_out = z_out.detach()
        return z_out

    def compute_logits(self, z_a, z_pos):
        """
        Uses logits trick for CURL:
        - compute (B,B) matrix z_a (W z_pos.T)
        - positives are all diagonal elements
        - negatives are all other elements
        - to compute loss use multiclass cross entropy with identity matrix for labels
        """
        Wz = torch.matmul(self.W, z_pos.T)  # (z_dim,B)
        logits = torch.matmul(z_a, Wz)  # (B,B)
        logits = logits - torch.max(logits, 1)[0][:, None]
        return logits