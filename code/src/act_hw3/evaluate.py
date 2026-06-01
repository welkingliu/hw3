from __future__ import annotations

import argparse
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader

from .config import ExperimentConfig
from .model import ACTPolicy
from .synthetic_calvin import CalvinLikeDataset
from .utils import device_from_arg, ensure_dir, set_seed, write_json


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Zero-shot evaluation for ACT policy.")
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--env", default="D")
    parser.add_argument("--output", default="runs/eval_D")
    parser.add_argument("--samples", type=int, default=400)
    parser.add_argument("--batch-size", type=int, default=ExperimentConfig.batch_size)
    parser.add_argument("--threshold", type=float, default=ExperimentConfig.success_threshold)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--seed", type=int, default=ExperimentConfig.seed + 20_000)
    return parser


def main() -> None:
    args = make_parser().parse_args()
    output = ensure_dir(Path(args.output))
    set_seed(args.seed)
    device = device_from_arg(args.device)
    checkpoint = torch.load(args.checkpoint, map_location=device)
    cfg = ExperimentConfig(**checkpoint["config"])

    model = ACTPolicy(
        cfg.image_size,
        cfg.state_dim,
        cfg.action_dim,
        cfg.chunk_size,
        cfg.hidden_dim,
        cfg.num_heads,
        cfg.num_layers,
    ).to(device)
    model.load_state_dict(checkpoint["model"])
    model.eval()

    dataset = CalvinLikeDataset(
        [args.env],
        args.samples,
        cfg.image_size,
        cfg.state_dim,
        cfg.action_dim,
        cfg.chunk_size,
        args.seed,
    )
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=False, num_workers=0)
    criterion = nn.L1Loss(reduction="none")
    sample_l1: list[float] = []

    with torch.no_grad():
        for batch in loader:
            image = batch["image"].to(device)
            state = batch["state"].to(device)
            action = batch["action"].to(device)
            pred = model(image, state)
            losses = criterion(pred, action).mean(dim=(1, 2))
            sample_l1.extend(float(v) for v in losses.cpu())

    mean_l1 = sum(sample_l1) / max(len(sample_l1), 1)
    success_rate = sum(v < args.threshold for v in sample_l1) / max(len(sample_l1), 1)
    result = {
        "checkpoint": str(args.checkpoint),
        "train_envs": checkpoint.get("train_envs", []),
        "test_env": args.env,
        "action_l1": mean_l1,
        "success_threshold": args.threshold,
        "success_rate": success_rate,
        "num_samples": len(sample_l1),
    }
    write_json(output / "results.json", result)
    print(f"env={args.env} action_l1={mean_l1:.4f} success_rate={success_rate:.3f}")


if __name__ == "__main__":
    main()
