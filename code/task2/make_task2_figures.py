from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path("/Users/welkinliu/Desktop/hw3")
RUNS = ROOT / "code" / "runs"
OUT = ROOT / "outputs" / "task2_report"


def read_metrics(name: str) -> list[dict[str, float]]:
    rows_by_epoch: dict[int, dict[str, float]] = {}
    with (RUNS / name / "metrics.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            epoch = int(row["epoch"])
            # Keep the last value for each epoch. This removes earlier smoke-test
            # rows if the same output directory was reused.
            rows_by_epoch[epoch] = {
                "epoch": epoch,
                "train_l1": float(row["train_l1"]),
                "val_l1": float(row["val_l1"]),
            }
    return [rows_by_epoch[k] for k in sorted(rows_by_epoch)]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    metrics = {"ACT-A": read_metrics("act_A"), "ACT-ABC": read_metrics("act_ABC")}

    plt.figure(figsize=(7.2, 4.4))
    for label, rows in metrics.items():
        epochs = [r["epoch"] for r in rows]
        vals = [r["val_l1"] for r in rows]
        plt.plot(epochs, vals, marker="o", label=f"{label} val Action L1")
    plt.xlabel("Epoch")
    plt.ylabel("Validation Action L1")
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT / "task2_val_loss_compare.png", dpi=180)
    plt.close()

    eval_a = json.loads((RUNS / "eval_A_to_D" / "results.json").read_text())
    eval_abc = json.loads((RUNS / "eval_ABC_to_D" / "results.json").read_text())

    plt.figure(figsize=(6.2, 4.0))
    names = ["ACT-A", "ACT-ABC"]
    action_l1 = [eval_a["action_l1"], eval_abc["action_l1"]]
    bars = plt.bar(names, action_l1, color=["#4C78A8", "#59A14F"])
    plt.ylabel("Zero-shot Action L1 on Env D")
    plt.grid(axis="y", alpha=0.25)
    for bar, value in zip(bars, action_l1):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{value:.4f}", ha="center", va="bottom")
    plt.tight_layout()
    plt.savefig(OUT / "task2_zero_shot_l1.png", dpi=180)
    plt.close()

    summary = {
        "act_A_final": metrics["ACT-A"][-1],
        "act_ABC_final": metrics["ACT-ABC"][-1],
        "eval_A_to_D": eval_a,
        "eval_ABC_to_D": eval_abc,
    }
    (OUT / "task2_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
