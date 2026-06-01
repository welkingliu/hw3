# HW3 项目提交说明

本项目包含两个部分：任务一“基于 3DGS 与 AIGC 的多源资产生成与真实场景融合”，以及任务二“基于 LeRobot/ACT 思路的跨环境泛化实验”。代码部分已整理在 GitHub，其余数据、模型输出、报告和中间结果按本地文件夹结构打包上传。

## 提交链接

- 代码仓库：[welkingliu/hw3](https://github.com/welkingliu/hw3)
- 任务一 Colab 实验链接：[Google Colab](https://colab.research.google.com/drive/1atesKpu2s_A05TU83BiJZCTbRBlL9yPj?usp=sharing)
- 其余数据与结果压缩包：[Google Drive](https://drive.google.com/file/d/1CeHkV0-cjR9GA_yywfSS-aUAXDBpmSSq/view?usp=sharing)
- 打包说明：Google Drive 中的文件夹位置与本地项目保持一致，主要包含 `data/`、`outputs/`、`code/runs/` 等非代码或实验输出材料。

## 项目结构说明

```text
hw3/
├── code/                 # 代码部分，对应 GitHub 仓库
│   ├── task1/            # 任务一：帧提取、Blender 融合、报告生成
│   ├── task2/            # 任务二：实验图表与 Word 报告生成
│   ├── src/act_hw3/      # 任务二 ACT 风格模型、数据集、训练与测试代码
│   ├── runs/             # 任务二训练权重、曲线、评估结果
│   ├── run_experiment.py # 任务二一键实验入口
│   ├── requirements.txt  # Python 依赖
│   └── environment.yml   # Conda 环境说明
├── data/                 # 原始视频、COLMAP 数据、3DGS 输出、OBJ/贴图资产
├── outputs/              # 最终融合图、实验图表、Word 报告
└── 提交说明.md            # 本文件
```

## 任务一：3DGS 与多源资产融合

任务一的目标是从真实视频中重建背景场景，并融合多个来源不同的三维资产，形成最终场景结果。

### 模块应用

| 模块 | 主要文件 | 作用 | 输出结果 |
|---|---|---|---|
| 视频帧提取 | `code/task1/extract_frames.py` | 从 `castle.mov` 和 `object_A.mov` 中抽取图像帧，供 COLMAP 和 3DGS 使用 | `data/castle_frames/`、`data/object_A_frames/` |
| COLMAP 数据准备 | `data/castle_colmap/`、`data/object_A_colmap/` | 保存相机参数、稀疏点云和图像匹配结果 | `sparse/0/cameras.bin`、`images.bin`、`points3D.bin` |
| 背景 3DGS 重建 | Colab + 3DGS 官方训练脚本 | 对城堡视频背景进行 3D Gaussian Splatting 重建 | `data/castle_3dgs_output.zip`、`data/fusion_assets/castle_3dgs/` |
| Object A 重建 | Colab + 3DGS 官方训练脚本 | 对真实拍摄的花瓶/花束物体进行 3DGS 重建 | `data/object_A_3dgs_output.zip`、`data/fusion_assets/object_A_3dgs/` |
| Object B 资产 | `data/13449_Treasure_Chest_v1_l1.obj`、`.mtl`、`.jpg` | 使用宝箱 OBJ、MTL 和贴图作为可融合虚拟资产 | `data/fusion_assets/object_B/` |
| Object C 资产 | `data/object_C.jpg`、`data/object_C.obj` | 使用单图生成/下载的石龙 OBJ 作为第三个虚拟资产 | `data/fusion_assets/object_C/` |
| Blender 渲染 | `code/task1/blender_render_insert_objects.py` | 导入 OBJ 资产，设置材质、相机和透明背景渲染 | `outputs/task1_fusion/inserted_objects_transparent.png` |
| Object A 前景处理 | `code/task1/create_object_A_cutout.py` | 从 Object A 的 3DGS 渲染图中裁切花瓶主体 | `outputs/task1_fusion/object_A_vase_cutout.png` |
| 最终合成 | `code/task1/composite_fusion.py` | 将城堡 3DGS 背景、Object A、Object B、Object C 进行图像级融合 | `outputs/task1_fusion/task1_fusion_composite.png` |
| 报告生成 | `code/task1/build_task1_word.py` | 自动生成任务一 Word 实验报告 | `outputs/task1_report/任务一_3DGS与AIGC多源资产融合报告.docx` |

### 输出结果

- 背景城堡场景完成 3DGS 训练，训练 7000 次迭代，最终训练 PSNR 约为 `30.62`，L1 约为 `0.0196`。
- Object A 花瓶/花束完成 3DGS 重建，并作为真实物体资产参与最终融合。
- Object B 宝箱 OBJ 成功读取 MTL 和 diffuse 贴图，可作为带纹理 mesh 插入场景。
- Object C 石龙 OBJ 没有 MTL 和贴图引用，因此在 Blender 中使用灰色石材材质进行补充。
- 最终融合图位于：`outputs/task1_fusion/task1_fusion_composite.png`。
- 任务一完整实验报告位于：`outputs/task1_report/任务一_3DGS与AIGC多源资产融合报告.docx`。

### 说明与改进点

- 原计划 Object B 使用 threestudio/SDS 文本生成 3D，但 Colab 环境中 `nerfacc`、`nvdiffrast` 等依赖编译失败，因此当前采用可融合的宝箱 mesh 资产替代完成多源资产融合流程。
- 当前融合主要是 Blender 渲染与图像合成层面的融合，已经体现多源资产放置、遮挡关系和阴影效果；后续可进一步改为统一三维坐标系下的真实 3DGS 场景级融合。
- Object C 当前只有几何 OBJ，没有材质贴图，后续可补充 MTL、纹理贴图或重新导出 GLB，以提升真实感。

## 任务二：ACT 跨环境泛化实验

任务二的目标是验证 ACT 风格策略在不同训练环境下的泛化能力：实验一只使用环境 A 训练，实验二使用环境 A/B/C 混合训练，然后统一在环境 D 中进行零样本测试。

### 模块应用

| 模块 | 主要文件 | 作用 | 输出结果 |
|---|---|---|---|
| 配置管理 | `code/src/act_hw3/config.py` | 保存训练参数、模型参数、数据规模和测试阈值 | 实验配置 JSON |
| 合成数据集 | `code/src/act_hw3/synthetic_calvin.py` | 构造 CALVIN 风格的多环境视觉差异和动作序列数据 | A/B/C/D 环境样本 |
| ACT 风格模型 | `code/src/act_hw3/model.py` | 使用视觉编码器、状态编码器和 Transformer decoder 预测动作 chunk | 策略网络权重 |
| 训练流程 | `code/src/act_hw3/train.py` | 分别训练 A-only 与 ABC-mixed 两组模型 | `code/runs/act_A/`、`code/runs/act_ABC/` |
| 测试流程 | `code/src/act_hw3/evaluate.py` | 在未见过的环境 D 上计算 Action L1 和 Success Rate | `code/runs/eval_A_to_D/`、`code/runs/eval_ABC_to_D/` |
| 一键入口 | `code/run_experiment.py` | 统一运行训练、评估和结果保存 | 完整实验输出 |
| 图表生成 | `code/task2/make_task2_figures.py` | 生成验证损失曲线和零样本 L1 对比图 | `outputs/task2_report/*.png` |
| 报告生成 | `code/task2/build_task2_word.py` | 自动生成任务二 Word 实验报告 | `outputs/task2_report/任务二_ACT跨环境泛化实验报告.docx` |

### 输出结果

| 实验 | 训练环境 | 测试环境 | Final Train L1 | Final Val L1 | Zero-shot Action L1 | Success Rate |
|---|---|---|---:|---:|---:|---:|
| 实验一 | A | D | 0.0210 | 0.0140 | 0.0143 | 100% |
| 实验二 | A/B/C | D | 0.0113 | 0.0071 | 0.0076 | 100% |

主要结论：

- A/B/C 混合训练相比只用 A 训练，在环境 D 上的 zero-shot Action L1 从 `0.0143` 降到 `0.0076`，下降约 `46.6%`。
- 两组实验在当前阈值 `0.16` 下 Success Rate 都为 `100%`，但混合训练的动作误差更低，说明跨环境鲁棒性更好。
- 任务二图表输出位于 `outputs/task2_report/`，包括验证损失对比图和零样本 L1 对比图。
- 任务二完整实验报告位于：`outputs/task2_report/任务二_ACT跨环境泛化实验报告.docx`。

### 说明与改进点

- 当前任务二使用轻量级 ACT 风格实现和合成 CALVIN-like 数据，能够验证“单环境训练”和“多环境混合训练”的泛化差异。
- Success Rate 由 Action L1 阈值近似得到，不是真实机器人仿真器中的完整 rollout 成功率。
- 后续可替换为官方 LeRobot/CALVIN 数据集和真实仿真环境，并用官方 ACT 训练脚本复现实验，以获得更严格的机器人策略评估结果。

## 最终材料对应关系

| 材料 | 位置 | 说明 |
|---|---|---|
| 代码 | GitHub `welkingliu/hw3`，本地 `code/` | 任务一脚本、任务二训练与评估代码 |
| 任务一 Colab | Google Colab 链接 | 3DGS 训练和相关在线实验过程 |
| 原始数据 | Google Drive 压缩包，本地 `data/` | 视频、帧、COLMAP、OBJ、贴图、3DGS 输出 |
| 任务一结果 | `outputs/task1_fusion/`、`outputs/task1_report/` | 融合图、Blender 文件、任务一 Word 报告 |
| 任务二结果 | `code/runs/`、`outputs/task2_report/` | 模型权重、训练指标、评估 JSON、图表、任务二 Word 报告 |

## 运行方式简述

任务一主要通过 Colab 完成 3DGS 训练，本地使用 Blender 和 Python 脚本完成资产导入、渲染和最终合成。任务二可在 `code/` 目录下安装依赖后，通过 `run_experiment.py` 完成训练与评估，再使用 `task2/` 中的脚本生成图表和报告。

由于数据、模型权重和 3DGS 输出文件较大，这些内容未全部放入代码仓库，而是通过 Google Drive 压缩包提交，并保持与本地项目相同的文件夹位置，便于复现和检查。
