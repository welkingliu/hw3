# 任务一：基于 3DGS 与 AIGC 的多源资产生成与真实场景融合

## 1. 任务目标

本任务要求完成一个“真实场景重建 + 多源 3D 资产生成 + 场景融合渲染”的完整流程。具体来说，需要使用 3D Gaussian Splatting 对真实场景进行重建，同时准备三类来源不同的 3D 物体资产，并将它们以合理比例和空间位置插入同一个 3D 场景中，最终生成融合渲染结果。

本项目以城堡航拍视频 `castle.mov` 作为真实背景场景，使用 COLMAP 估计相机位姿，并使用 3D Gaussian Splatting 重建城堡岛屿场景。在此基础上，分别准备真实多视角重建物体 A、AIGC/文本生成风格物体 B，以及单图到 3D 生成物体 C，最后将这些资产统一到 Blender 合成场景中进行展示。

## 2. 任务要求与完成情况

| 作业要求 | 当前完成方式 | 完成情况 |
| --- | --- | --- |
| 背景场景重建 | 使用 `castle.mov` 抽帧，COLMAP 求位姿，3DGS 训练城堡场景 | 已完成 |
| 物体 A：真实多视角重建 | 使用 `object_A.mov` 抽帧，COLMAP 求位姿，3DGS 训练物体 A | 已完成 |
| 物体 B：文本到 3D 生成 | 当前使用宝箱 OBJ/MTL/贴图作为 AIGC 风格虚拟资产；曾尝试 threestudio，但 Colab 依赖编译失败 | 替代完成 |
| 物体 C：单图到 3D 生成 | 使用 `object_C.jpg` 作为单图输入，通过 image-to-3D 工具导出 `object_C.obj` | 已完成 |
| 场景融合与渲染 | 使用 Blender 渲染插入物体，并与城堡 3DGS 渲染结果进行空间合成 | 已完成 |
| 质量分析 | 对比多视角重建、AIGC mesh、单图生成 mesh 的优缺点 | 已完成 |

## 3. 数据与资产准备

### 3.1 背景场景：城堡 3DGS

背景场景来自 `data/castle.mov`。首先从视频中抽取关键帧：

- 视频帧率：25 fps
- 抽帧频率：约 3.125 fps
- 抽帧数量：185 张
- 图像尺寸：1600 x 900
- 输出目录：`data/castle_frames/`

随后使用 COLMAP 对抽帧图像进行特征提取、特征匹配和稀疏重建，得到相机内外参与稀疏点云：

```text
data/castle_colmap/
  images/
  sparse/0/
    cameras.bin
    images.bin
    points3D.bin
  database.db
```

最后在 Google Colab 的 NVIDIA GPU 环境中训练 3D Gaussian Splatting：

- 训练迭代数：7000
- 初始点数：88214
- 训练耗时：约 4 分 50 秒
- 训练集 L1：0.0196
- 训练集 PSNR：30.62 dB
- 训练结果：`data/castle_3dgs_output.zip`
- 3DGS 点云：`point_cloud/iteration_7000/point_cloud.ply`
- 点云大小：约 158 MB
- 渲染图数量：185 张

### 3.2 物体 A：真实多视角 3DGS 重建

物体 A 来自真实拍摄视频 `data/object_A.mov`。处理流程与背景场景一致：

```text
object_A.mov -> 抽帧 -> COLMAP -> 3DGS 训练
```

实验设置：

- 抽帧数量：102 张
- COLMAP 输出：`data/object_A_colmap/`
- 3DGS 输出：`data/object_A_3dgs_output.zip`
- 3DGS 点云：`point_cloud/iteration_7000/point_cloud.ply`
- 点云大小：约 47 MB
- 渲染图数量：102 张

物体 A 体现了真实多视角重建路线的特点：几何与纹理主要来自真实拍摄，因此外观可信度较高，但需要较完整的拍摄环绕视角以及稳定光照。

### 3.3 物体 B：AIGC / 文本生成风格宝箱资产

物体 B 选择与城堡场景风格一致的中世纪宝箱。当前使用的资产包括：

```text
data/13449_Treasure_Chest_v1_l1.obj
data/13449_Treasure_Chest_v1_l1.mtl
data/13449_Treasure_Chest_Diffuse.jpg
```

其中 OBJ 提供几何结构，MTL 提供材质定义，Diffuse 贴图提供木质与金属纹理。该资产在最终融合中作为虚拟生成类资产，与真实重建的城堡背景形成对比。

原计划使用 threestudio 基于 SDS Loss 完成文本到 3D 生成，但在 Colab 环境中 `nerfacc` 与 `nvdiffrast` 等 CUDA 扩展编译失败。因此当前版本采用可导入 Blender 的宝箱 mesh 资产作为替代实现。在后续改进中，可以使用稳定的 AutoDL / CUDA + Python 3.10 环境重新运行 threestudio，并用 prompt 直接生成宝箱资产：

```text
a medieval treasure chest, wooden box with golden metal decorations,
detailed texture, isolated object, game asset
```

### 3.4 物体 C：单图到 3D 生成

物体 C 使用单张图像 `data/object_C.jpg` 作为输入。该图像为白色背景下的石质龙雕像，具有完整物体轮廓和清晰纹理，适合 image-to-3D 工具处理。

生成结果：

```text
data/object_C.obj
```

检查结果显示，`object_C.obj` 主要包含顶点与面信息，没有引用 MTL 材质文件，也没有贴图坐标或纹理。因此在融合阶段为其重新赋予灰色石质材质。

## 4. 方法流程

### 4.1 视频抽帧

对真实视频素材进行均匀抽帧，降低重复帧数量并控制 COLMAP 计算量。背景场景使用较低抽帧率以控制训练规模，物体 A 使用较高抽帧率以保留近距离物体细节。

### 4.2 COLMAP 位姿估计

COLMAP 用于从多视角图片中恢复相机参数和稀疏点云。其输出是 3DGS 训练的前置条件，包括：

- `cameras.bin`：相机内参
- `images.bin`：图像位姿
- `points3D.bin`：稀疏三维点

### 4.3 3D Gaussian Splatting 训练

3DGS 使用 COLMAP 的稀疏点云作为初始化，将场景表示为大量带颜色、不透明度和协方差的 3D Gaussian primitives。相比传统 mesh，3DGS 在新视角合成中能较好保留真实图像纹理。

背景城堡和物体 A 均采用该流程完成重建。

### 4.4 Mesh 资产导入与材质处理

物体 B 和物体 C 均为 mesh 表示。其中：

- 物体 B：OBJ + MTL + JPG，保留原始木质/金属纹理。
- 物体 C：OBJ，无 MTL 和贴图，因此在 Blender 中赋予石质材质。

### 4.5 场景融合策略

本项目中同时存在两种不同的 3D 表示：

- 3DGS：背景城堡、物体 A
- Mesh：物体 B、物体 C

由于 3DGS 与 mesh 的底层表示和渲染方式不同，直接在同一个 3DGS renderer 中融合存在工程难度。当前采用 Blender 与图像合成作为统一展示平台：使用 3DGS 渲染结果作为真实背景参考，将物体 A 的 3DGS 渲染视图作为前景资产插入场景，同时将 mesh 资产 B/C 以合理尺度、位置和光照合成到城堡岛屿区域，并保留 3DGS 点云与渲染结果作为真实重建证据。

最终融合图：

```text
outputs/task1_fusion/task1_fusion_composite.png
```

对应融合脚本：

```text
code/task1/blender_render_insert_objects.py
code/task1/composite_fusion.py
```

## 5. 实验结果

### 5.1 背景 3DGS 重建结果

城堡背景经过 7000 次迭代训练后，能够生成较稳定的新视角渲染图。城堡主体、桥、岛屿草地与水面轮廓均被重建出来。由于输入视频为航拍场景，水面存在反光和动态波纹，因此水域细节相比城堡主体更容易出现模糊或浮动。

代表性输出：

```text
data/fusion_assets/castle_3dgs/outputs/castle_3dgs/train/ours_7000/renders/00092.png
```

### 5.2 物体 A 重建结果

物体 A 使用真实多视角视频进行重建，生成了独立的 3DGS 点云和 102 张渲染图。该路线的优点是真实感较好，缺点是需要额外拍摄并且对相机运动、光照和背景纹理有要求。

### 5.3 物体 B 生成结果

宝箱资产具有完整的 OBJ 几何、MTL 材质与 diffuse 纹理，能够在 Blender 中正常显示木质箱体和金属包边。该物体与城堡背景风格一致，适合作为虚拟插入资产。

### 5.4 物体 C 生成结果

物体 C 由单张龙雕像图片生成 OBJ mesh。其几何结构能够表达龙头、翅膀和雕像轮廓，但由于导出的 OBJ 不包含材质与纹理，最终使用手动石质材质替代。该结果体现了单图到 3D 方法的特点：输入简单，但背面细节和材质质量容易依赖模型先验。

### 5.5 场景融合结果

最终融合结果将花瓶 A、宝箱 B 和龙雕 C 插入到城堡岛屿草地区域：

```text
outputs/task1_fusion/task1_fusion_composite.png
```

该图展示了不同来源资产在同一视觉场景中的融合效果。相比初始 Blender 平面预览，最终版本去除了突兀的桌面平面，并补充了物体 A 的 3DGS 渲染前景，使 A/B/C 三个要求中的物体都出现在最终场景中，视觉上更接近“插入真实场景”的要求。

## 6. 三种资产生成方式对比

| 方法 | 输入 | 输出 | 几何准确性 | 纹理质量 | 计算成本 | 优点 | 缺点 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 多视角 3DGS 重建 | 视频/多张照片 | 3DGS 点云 | 高 | 高 | 较高 | 真实感强，细节来自真实图像 | 需要拍摄多视角，依赖 COLMAP 成功 |
| 文本/AIGC mesh 资产 | Prompt 或生成资产 | OBJ/GLB mesh | 中 | 中到高 | 中到高 | 创造性强，不需要真实物体 | 几何可能不稳定，依赖生成模型 |
| 单图到 3D | 单张图片 | OBJ mesh | 中 | 低到中 | 中 | 输入最简单 | 背面细节依赖先验，常缺材质/贴图 |

## 7. 问题与改进点

1. **threestudio 环境未完全跑通**  
   在 Colab 中安装 threestudio 时，`nerfacc` 与 `nvdiffrast` CUDA 扩展编译失败。后续可以使用 AutoDL、Python 3.10、固定 CUDA/PyTorch 版本重新配置环境，以完成严格意义上的 SDS text-to-3D 训练。

2. **3DGS 与 mesh 表示未完全统一**  
   当前采用 Blender/图像合成的方式展示融合结果。更进一步的做法是将 mesh 采样为点云并转换为 Gaussian 表示，或使用支持 mesh + 3DGS 混合渲染的自定义 renderer。

3. **物体 C 缺少材质贴图**  
   `object_C.obj` 没有 MTL 与纹理文件，因此最终使用手动石质材质。后续可选择能导出 textured OBJ/GLB 的 image-to-3D 工具，提升物体 C 的真实感。

4. **背景水面重建存在动态干扰**  
   航拍视频中的水面反光和波纹属于非静态区域，会降低 COLMAP 与 3DGS 的稳定性。后续可裁剪水面区域，或选择更多围绕城堡主体的稳定视角。

5. **融合尺度与光照仍可优化**  
   当前融合图已经控制了物体尺度和位置，但仍可通过阴影匹配、颜色校正、深度遮挡和相机标定进一步提升真实感。

## 8. 可提交材料清单

| 材料 | 路径 |
| --- | --- |
| 背景视频 | `data/castle.mov` |
| 背景抽帧 | `data/castle_frames/` |
| 背景 COLMAP | `data/castle_colmap/` |
| 背景 3DGS 权重与点云 | `data/castle_3dgs_output.zip` |
| 物体 A 视频 | `data/object_A.mov` |
| 物体 A COLMAP | `data/object_A_colmap/` |
| 物体 A 3DGS 权重与点云 | `data/object_A_3dgs_output.zip` |
| 物体 B mesh | `data/13449_Treasure_Chest_v1_l1.obj` |
| 物体 B 材质 | `data/13449_Treasure_Chest_v1_l1.mtl` |
| 物体 B 贴图 | `data/13449_Treasure_Chest_Diffuse.jpg` |
| 物体 C 单图输入 | `data/object_C.jpg` |
| 物体 C 生成 mesh | `data/object_C.obj` |
| 物体 A 前景裁切 | `outputs/task1_fusion/object_A_vase_cutout.png` |
| A/B/C 融合结果 | `outputs/task1_fusion/task1_fusion_composite.png` |
| 融合脚本 | `code/task1/blender_render_insert_objects.py` |

## 9. 总结

本项目完成了基于 3DGS 与 AIGC 的多源资产融合实验。背景城堡和物体 A 通过真实视频和多视角重建获得，体现了真实场景 3DGS 的高保真新视角合成能力；物体 B 使用带材质贴图的宝箱 mesh 作为虚拟生成类资产；物体 C 使用单张图像生成 OBJ mesh，并通过手动材质补全进行融合。最终结果展示了不同来源、不同表示形式的 3D 资产在同一城堡场景中的组合效果，同时也暴露了 3DGS 与 mesh 表示统一、text-to-3D 环境配置、材质一致性等后续改进方向。
