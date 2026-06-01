from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import torch
from torch.utils.data import Dataset


ENV_STYLES = {
    "A": {"background": (0.12, 0.16, 0.22), "object": (0.95, 0.30, 0.25), "noise": 0.035, "shift": 0.00},
    "B": {"background": (0.20, 0.14, 0.12), "object": (0.25, 0.70, 0.95), "noise": 0.055, "shift": 0.18},
    "C": {"background": (0.10, 0.23, 0.16), "object": (0.95, 0.75, 0.20), "noise": 0.050, "shift": -0.15},
    "D": {"background": (0.26, 0.23, 0.31), "object": (0.70, 0.92, 0.45), "noise": 0.070, "shift": 0.33},
}


@dataclass(frozen=True)
class Sample:
    image: np.ndarray
    state: np.ndarray
    action_chunk: np.ndarray
    env_id: str


def _render_image(state: np.ndarray, env_id: str, image_size: int, rng: np.random.Generator) -> np.ndarray:
    style = ENV_STYLES[env_id]
    image = np.ones((3, image_size, image_size), dtype=np.float32)
    image *= np.array(style["background"], dtype=np.float32)[:, None, None]

    cx = int((state[0] * 0.5 + 0.5) * (image_size - 1))
    cy = int((state[1] * 0.5 + 0.5) * (image_size - 1))
    radius = 3 + int(abs(state[2]) * 3)
    yy, xx = np.ogrid[:image_size, :image_size]
    mask = (xx - cx) ** 2 + (yy - cy) ** 2 <= radius**2
    image[:, mask] = np.array(style["object"], dtype=np.float32)[:, None]

    goal_x = int((state[4] * 0.5 + 0.5) * (image_size - 1))
    goal_y = int((state[5] * 0.5 + 0.5) * (image_size - 1))
    image[:, max(0, goal_y - 1) : min(image_size, goal_y + 2), :] += 0.08
    image[:, :, max(0, goal_x - 1) : min(image_size, goal_x + 2)] += 0.08

    image += rng.normal(0.0, style["noise"], size=image.shape).astype(np.float32)
    return np.clip(image, 0.0, 1.0)


def _expert_action_chunk(state: np.ndarray, env_id: str, chunk_size: int, action_dim: int) -> np.ndarray:
    style_shift = ENV_STYLES[env_id]["shift"]
    chunk = []
    current = state[:action_dim].copy()
    target = np.array([state[4], state[5], np.sin(state[6]), np.cos(state[7])], dtype=np.float32)

    for step in range(chunk_size):
        phase = (step + 1) / chunk_size
        correction = 0.42 * (target - current)
        periodic = 0.05 * np.array(
            [
                np.sin(state[2] + phase + style_shift),
                np.cos(state[3] - phase),
                np.sin(state[6] * phase),
                np.cos(state[7] + style_shift),
            ],
            dtype=np.float32,
        )
        action = correction + periodic
        current = current + action
        chunk.append(action)

    return np.stack(chunk, axis=0).astype(np.float32)


class CalvinLikeDataset(Dataset):
    """Small deterministic dataset that mimics CALVIN visual domain shifts."""

    def __init__(
        self,
        env_ids: Iterable[str],
        samples_per_env: int,
        image_size: int,
        state_dim: int,
        action_dim: int,
        chunk_size: int,
        seed: int,
    ) -> None:
        self.samples: list[Sample] = []
        for env_index, env_id in enumerate(env_ids):
            if env_id not in ENV_STYLES:
                raise ValueError(f"Unknown environment {env_id!r}; choose from {sorted(ENV_STYLES)}")
            rng = np.random.default_rng(seed + env_index * 997)
            for _ in range(samples_per_env):
                state = rng.uniform(-1.0, 1.0, size=(state_dim,)).astype(np.float32)
                state[4:6] = np.clip(state[:2] + rng.normal(0.0, 0.45, size=(2,)), -1.0, 1.0)
                image = _render_image(state, env_id, image_size, rng)
                action = _expert_action_chunk(state, env_id, chunk_size, action_dim)
                self.samples.append(Sample(image=image, state=state, action_chunk=action, env_id=env_id))

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor | str]:
        sample = self.samples[index]
        return {
            "image": torch.from_numpy(sample.image),
            "state": torch.from_numpy(sample.state),
            "action": torch.from_numpy(sample.action_chunk),
            "env_id": sample.env_id,
        }
