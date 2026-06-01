from __future__ import annotations

import csv
import json
import random
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import torch


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def device_from_arg(name: str) -> torch.device:
    if name == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(name)


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def append_metrics(path: Path, row: dict[str, float | int | str]) -> None:
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def plot_metrics(csv_path: Path, output_path: Path) -> None:
    rows: list[dict[str, str]] = []
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        rows.extend(csv.DictReader(f))
    if not rows:
        return

    epochs = [int(row["epoch"]) for row in rows]
    train = [float(row["train_l1"]) for row in rows]
    val = [float(row["val_l1"]) for row in rows]

    plt.figure(figsize=(6, 4))
    plt.plot(epochs, train, marker="o", label="train Action L1")
    plt.plot(epochs, val, marker="s", label="val Action L1")
    plt.xlabel("Epoch")
    plt.ylabel("L1 loss")
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()
