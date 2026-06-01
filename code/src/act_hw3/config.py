from dataclasses import dataclass


@dataclass
class ExperimentConfig:
    seed: int = 7
    image_size: int = 32
    state_dim: int = 8
    action_dim: int = 4
    chunk_size: int = 8
    train_samples_per_env: int = 800
    val_samples_per_env: int = 200
    batch_size: int = 64
    epochs: int = 8
    learning_rate: float = 3e-4
    weight_decay: float = 1e-4
    hidden_dim: int = 128
    num_heads: int = 4
    num_layers: int = 2
    success_threshold: float = 0.16
