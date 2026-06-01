from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader
from tqdm import tqdm

from .config import ExperimentConfig
from .model import ACTPolicy
from .synthetic_calvin import CalvinLikeDataset
from .utils import append_metrics, device_from_arg, ensure_dir, plot_metrics, set_seed, write_json


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train a lightweight ACT policy.")
    parser.add_argument("--envs", default="A", help="Comma-separated training environments, e.g. A or A,B,C.")
    parser.add_argument("--output", default="runs/act_A", help="Directory for checkpoints and metrics.")
    parser.add_argument("--epochs", type=int, default=ExperimentConfig.epochs)
    parser.add_argument("--batch-size", type=int, default=ExperimentConfig.batch_size)
    parser.add_argument("--train-samples", type=int, default=ExperimentConfig.train_samples_per_env)
    parser.add_argument("--val-samples", type=int, default=ExperimentConfig.val_samples_per_env)
    parser.add_argument("--learning-rate", type=float, default=ExperimentConfig.learning_rate)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--seed", type=int, default=ExperimentConfig.seed)
    return parser


def evaluate(model: ACTPolicy, loader: DataLoader, criterion: nn.Module, device: torch.device) -> float:
    model.eval()
    total = 0.0
    count = 0
    with torch.no_grad():
        for batch in loader:
            image = batch["image"].to(device)
            state = batch["state"].to(device)
            action = batch["action"].to(device)
            pred = model(image, state)
            loss = criterion(pred, action)
            total += float(loss.item()) * image.shape[0]
            count += image.shape[0]
    return total / max(count, 1)


def main() -> None:
    args = make_parser().parse_args()
    cfg = ExperimentConfig(
        seed=args.seed,
        epochs=args.epochs,
        batch_size=args.batch_size,
        train_samples_per_env=args.train_samples,
        val_samples_per_env=args.val_samples,
        learning_rate=args.learning_rate,
    )
    envs = [env.strip() for env in args.envs.split(",") if env.strip()]
    output = ensure_dir(Path(args.output))
    set_seed(cfg.seed)
    device = device_from_arg(args.device)

    train_set = CalvinLikeDataset(
        envs,
        cfg.train_samples_per_env,
        cfg.image_size,
        cfg.state_dim,
        cfg.action_dim,
        cfg.chunk_size,
        cfg.seed,
    )
    val_set = CalvinLikeDataset(
        envs,
        cfg.val_samples_per_env,
        cfg.image_size,
        cfg.state_dim,
        cfg.action_dim,
        cfg.chunk_size,
        cfg.seed + 10_000,
    )
    train_loader = DataLoader(train_set, batch_size=cfg.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_set, batch_size=cfg.batch_size, shuffle=False, num_workers=0)

    model = ACTPolicy(
        cfg.image_size,
        cfg.state_dim,
        cfg.action_dim,
        cfg.chunk_size,
        cfg.hidden_dim,
        cfg.num_heads,
        cfg.num_layers,
    ).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.learning_rate, weight_decay=cfg.weight_decay)
    criterion = nn.L1Loss()
    metrics_path = output / "metrics.csv"
    best_val = float("inf")

    write_json(output / "config.json", {**asdict(cfg), "train_envs": envs, "device": str(device)})
    for epoch in range(1, cfg.epochs + 1):
        model.train()
        running = 0.0
        seen = 0
        for batch in tqdm(train_loader, desc=f"epoch {epoch}/{cfg.epochs}", leave=False):
            image = batch["image"].to(device)
            state = batch["state"].to(device)
            action = batch["action"].to(device)

            optimizer.zero_grad(set_to_none=True)
            pred = model(image, state)
            loss = criterion(pred, action)
            loss.backward()
            optimizer.step()
            running += float(loss.item()) * image.shape[0]
            seen += image.shape[0]

        train_l1 = running / max(seen, 1)
        val_l1 = evaluate(model, val_loader, criterion, device)
        append_metrics(metrics_path, {"epoch": epoch, "train_l1": train_l1, "val_l1": val_l1})

        checkpoint = {
            "model": model.state_dict(),
            "config": asdict(cfg),
            "train_envs": envs,
            "epoch": epoch,
            "val_l1": val_l1,
        }
        torch.save(checkpoint, output / "last.pt")
        if val_l1 < best_val:
            best_val = val_l1
            torch.save(checkpoint, output / "best.pt")

    plot_metrics(metrics_path, output / "loss_curve.png")
    print(f"best_val_l1={best_val:.4f} checkpoint={output / 'best.pt'}")


if __name__ == "__main__":
    main()
