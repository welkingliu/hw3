# HW3: LeRobot ACT 跨环境泛化实验

本目录实现的是 PDF 中“题目二：基于 LeRobot 的 ACT 策略跨环境泛化挑战”的可运行代码框架。由于当前 `data/` 为空，代码默认使用一个轻量的 CALVIN-like 合成数据集来模拟环境 A/B/C/D 的视觉分布偏移、动作分块预测和 zero-shot 测试流程；拿到真实 CALVIN/LeRobot 数据后，可以替换 `src/act_hw3/synthetic_calvin.py` 中的数据集类。

## 任务划分

1. 基础策略训练：只使用环境 A 的数据训练 ACT 视觉-动作策略。
2. 多环境联合训练：混合环境 A、B、C 的数据，用相同网络结构和超参数重新训练。
3. Zero-shot 测试：把上面两个模型直接部署到未见过的环境 D，比较 Action L1 Loss 和 Success Rate。
4. 实验报告支撑：导出训练曲线、配置、模型权重和测试结果，便于写 PDF 报告。

## 作业要求与满足方式

| PDF 要求 | 本项目如何满足 |
| --- | --- |
| 使用 ACT 算法训练视觉-动作策略 | `src/act_hw3/model.py` 实现了 CNN 视觉编码 + Transformer Decoder 的 ACT-style action chunking 策略 |
| 环境 A 基础训练 | `python -m src.act_hw3.train --envs A --output runs/act_A` |
| 环境 A/B/C 联合训练 | `python -m src.act_hw3.train --envs A,B,C --output runs/act_ABC` |
| 环境 D zero-shot 测试 | `python -m src.act_hw3.evaluate --checkpoint runs/act_ABC/best.pt --env D` |
| 对比 Action L1 Loss / Success Rate | 测试结果写入 `runs/eval_*/results.json` |
| 记录训练曲线 | 每次训练导出 `metrics.csv` 和 `loss_curve.png` |
| README、环境配置、训练和测试命令 | 本文件、`requirements.txt`、`environment.yml` 和下方命令 |
| 模型权重 | 每次训练保存 `best.pt` 和 `last.pt`，可上传网盘并在报告中贴链接 |

## 快速开始

```bash
cd /Users/welkinliu/Desktop/hw3/code
python3 -m pip install -r requirements.txt
python3 run_experiment.py --epochs 8 --train-samples 800 --val-samples 200
```

如果本机有多个 Python 环境，可以指定已安装 PyTorch 的解释器：

```bash
HW3_PYTHON=/Users/welkinliu/miniconda3/bin/python3 python3 run_experiment.py --epochs 8
```

如果只想快速检查流程：

```bash
python3 run_experiment.py --epochs 1 --train-samples 64 --val-samples 32
```

单独训练和测试：

```bash
python3 -m src.act_hw3.train --envs A --output runs/act_A
python3 -m src.act_hw3.train --envs A,B,C --output runs/act_ABC
python3 -m src.act_hw3.evaluate --checkpoint runs/act_A/best.pt --env D --output runs/eval_A_to_D
python3 -m src.act_hw3.evaluate --checkpoint runs/act_ABC/best.pt --env D --output runs/eval_ABC_to_D
```

## 默认实验设置

| 项目 | 默认值 |
| --- | --- |
| Network Architecture | CNN image encoder + MLP state encoder + Transformer Decoder |
| Image Size | 32 x 32 |
| State Dim | 8 |
| Action Dim | 4 |
| Action Chunk Size | 8 |
| Batch Size | 64 |
| Learning Rate | 3e-4 |
| Optimizer | AdamW |
| Epochs | 8 |
| Loss Function | Action L1 Loss |
| Success Rate | 样本 Action L1 小于阈值 0.16 的比例 |

## 输出文件

训练后会生成：

- `runs/act_A/best.pt`：环境 A 基础模型最佳权重
- `runs/act_ABC/best.pt`：多环境联合模型最佳权重
- `runs/*/metrics.csv`：每轮训练和验证 Action L1
- `runs/*/loss_curve.png`：报告可直接引用的训练曲线
- `runs/eval_*/results.json`：环境 D 的 zero-shot 指标

## 可以改进的点

1. 接入真实 CALVIN/LeRobot 数据集，替换当前合成环境。
2. 加入真实仿真 rollout，而不是用 Action L1 阈值近似 Success Rate。
3. 使用 LeRobot 官方 ACT 模型和数据格式，以便和课程基线直接对齐。
4. 增加 WandB 或 SwanLab 日志记录，自动保存曲线和超参数表。
5. 做更多消融：chunk size、视觉增强、环境混合比例、冻结视觉编码器等。
6. 在报告中重点分析环境 D 的视觉分布偏移，以及 action chunking 对偏移的鲁棒性影响。
