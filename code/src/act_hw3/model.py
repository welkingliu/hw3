from __future__ import annotations

import torch
from torch import nn


class ACTPolicy(nn.Module):
    """Compact ACT-style policy with visual encoding and action chunk prediction."""

    def __init__(
        self,
        image_size: int,
        state_dim: int,
        action_dim: int,
        chunk_size: int,
        hidden_dim: int,
        num_heads: int,
        num_layers: int,
    ) -> None:
        super().__init__()
        self.chunk_size = chunk_size
        self.action_dim = action_dim

        self.visual_encoder = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=5, stride=2, padding=2),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, hidden_dim, kernel_size=3, stride=2, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
        )
        self.state_encoder = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
        )
        self.context = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
        )
        self.query = nn.Parameter(torch.randn(chunk_size, hidden_dim) * 0.02)
        decoder_layer = nn.TransformerDecoderLayer(
            d_model=hidden_dim,
            nhead=num_heads,
            dim_feedforward=hidden_dim * 4,
            dropout=0.1,
            batch_first=True,
            activation="gelu",
        )
        self.decoder = nn.TransformerDecoder(decoder_layer, num_layers=num_layers)
        self.action_head = nn.Sequential(
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, action_dim),
        )

    def forward(self, image: torch.Tensor, state: torch.Tensor) -> torch.Tensor:
        visual = self.visual_encoder(image)
        state_feature = self.state_encoder(state)
        memory = self.context(torch.cat([visual, state_feature], dim=-1)).unsqueeze(1)
        queries = self.query.unsqueeze(0).expand(image.shape[0], -1, -1)
        decoded = self.decoder(tgt=queries, memory=memory)
        return self.action_head(decoded)
