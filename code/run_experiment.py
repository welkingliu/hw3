from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> None:
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)


def has_torch(python: str) -> bool:
    result = subprocess.run(
        [python, "-c", "import torch"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def resolve_python() -> str:
    override = os.environ.get("HW3_PYTHON")
    candidates = [
        override,
        sys.executable,
        shutil.which("python3"),
        str(Path.home() / "miniconda3" / "bin" / "python3"),
        str(Path.home() / "anaconda3" / "bin" / "python3"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists() and has_torch(candidate):
            return candidate
    raise RuntimeError("No Python interpreter with PyTorch found. Install requirements.txt or set HW3_PYTHON.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run HW3 ACT baseline, multi-env training, and D zero-shot tests.")
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--train-samples", type=int, default=800)
    parser.add_argument("--val-samples", type=int, default=200)
    parser.add_argument("--device", default="auto")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    python = resolve_python()
    common = [
        "--epochs",
        str(args.epochs),
        "--train-samples",
        str(args.train_samples),
        "--val-samples",
        str(args.val_samples),
        "--device",
        args.device,
    ]
    run([python, "-m", "src.act_hw3.train", "--envs", "A", "--output", str(root / "runs" / "act_A"), *common])
    run([python, "-m", "src.act_hw3.train", "--envs", "A,B,C", "--output", str(root / "runs" / "act_ABC"), *common])
    run(
        [
            python,
            "-m",
            "src.act_hw3.evaluate",
            "--checkpoint",
            str(root / "runs" / "act_A" / "best.pt"),
            "--env",
            "D",
            "--output",
            str(root / "runs" / "eval_A_to_D"),
            "--device",
            args.device,
        ]
    )
    run(
        [
            python,
            "-m",
            "src.act_hw3.evaluate",
            "--checkpoint",
            str(root / "runs" / "act_ABC" / "best.pt"),
            "--env",
            "D",
            "--output",
            str(root / "runs" / "eval_ABC_to_D"),
            "--device",
            args.device,
        ]
    )


if __name__ == "__main__":
    main()
