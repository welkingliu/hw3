# 任务一要求核对表

| 要求 | 状态 | 证据 |
| --- | --- | --- |
| 真实背景 3DGS 重建 | 完成 | `data/castle_3dgs_output.zip` |
| 物体 A 多视角 3DGS 重建 | 完成 | `data/object_A_3dgs_output.zip` |
| 物体 B 文本到 3D | 替代完成 | `data/13449_Treasure_Chest_v1_l1.obj` 等宝箱 mesh 资产；threestudio 依赖失败写入改进点 |
| 物体 C 单图到 3D | 完成 | `data/object_C.jpg` + `data/object_C.obj` |
| 融合渲染 | 完成 | `outputs/task1_fusion/task1_fusion_composite.png` |
| 报告可视化图 | 完成 | 3DGS renders、物体 B/C、融合图 |
| 代码与流程说明 | 完成 | `code/task1/` |
| 模型权重 | 完成 | 两个 3DGS output zip |

## 最建议放进 PDF 的图

1. `data/castle_frames/frame_00092.jpg`：背景输入帧示例
2. `data/fusion_assets/castle_3dgs/outputs/castle_3dgs/train/ours_7000/renders/00092.png`：背景 3DGS 渲染结果
3. `data/fusion_assets/object_A_3dgs/outputs/object_A_3dgs/train/ours_7000/renders/00051.png`：物体 A 渲染结果
4. `data/13449_Treasure_Chest_Diffuse.jpg`：物体 B 纹理
5. `data/object_C.jpg`：物体 C 单图输入
6. `outputs/task1_fusion/task1_fusion_composite.png`：最终融合结果，包含花瓶 A、宝箱 B、龙雕 C

## 需要在报告里诚实说明的点

- 物体 B 未通过本地成功运行 threestudio 生成，而是使用了可融合的宝箱 mesh 资产作为替代。
- 物体 C 的 OBJ 没有 MTL 和纹理，因此融合时手动赋予石质材质。
- 当前最终融合是 Blender/图像合成层面的异构资产融合，不是将所有 3DGS 与 mesh 完全转换到同一个高斯 renderer 中。
