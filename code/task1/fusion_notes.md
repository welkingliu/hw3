# Task 1 Fusion Notes

## Current Assets

- Background scene: `data/fusion_assets/castle_3dgs/outputs/castle_3dgs/point_cloud/iteration_7000/point_cloud.ply`
- Object A, real multi-view 3DGS: `data/fusion_assets/object_A_3dgs/outputs/object_A_3dgs/point_cloud/iteration_7000/point_cloud.ply`
- Object B, text/AIGC mesh asset: `data/fusion_assets/object_B/13449_Treasure_Chest_v1_l1.obj`
- Object C, single-image-to-3D mesh: `data/fusion_assets/object_C/object_C.obj`

## Fusion Strategy

The background and object A are represented as 3D Gaussian Splatting outputs, while objects B and C are mesh assets. For a stable final demonstration, use Blender as the unified composition space:

1. Use a rendered castle 3DGS frame as the scene backdrop/reference.
2. Import object B as textured OBJ using its MTL and diffuse texture.
3. Import object C OBJ and assign a stone material, because the generated OBJ has no MTL or texture.
4. Insert object A by using a rendered 3DGS view as a cutout, so the final composite visually contains all three required objects A/B/C.
5. Keep the 3DGS point clouds and rendered views as evidence of the original reconstruction pipeline.

This matches the report requirement to explain how heterogeneous representations are unified for fusion.

## Blender Command

```bash
blender --python /Users/welkinliu/Desktop/hw3/code/task1/blender_fusion_scene.py
```

Expected outputs:

- `outputs/task1_fusion/task1_fusion_scene.blend`
- `outputs/task1_fusion/task1_fusion_preview.png`
- `outputs/task1_fusion/task1_fusion_composite.png`

## Report Wording

Because 3DGS uses explicit Gaussian primitives and AIGC assets are exported as mesh files, direct renderer-level fusion requires a shared representation. In this project, the final demonstration uses Blender as a common composition and rendering platform: 3DGS renderings and point clouds provide the reconstructed real scene evidence, while OBJ assets are imported as mesh objects with appropriate materials. This makes the representation mismatch explicit and keeps the fusion workflow reproducible.
