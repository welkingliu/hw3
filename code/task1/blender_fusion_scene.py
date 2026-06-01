"""Create a simple HW3 fusion scene in Blender.

Run with:
    blender --python /Users/welkinliu/Desktop/hw3/code/task1/blender_fusion_scene.py
"""

from __future__ import annotations

import math
from pathlib import Path

import bpy


ROOT = Path("/Users/welkinliu/Desktop/hw3")
ASSETS = ROOT / "data" / "fusion_assets"
OUTPUT = ROOT / "outputs" / "task1_fusion"


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def make_material(name: str, color: tuple[float, float, float, float], roughness: float = 0.6):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
    return material


def import_obj(path: Path, name: str):
    bpy.ops.wm.obj_import(filepath=str(path))
    imported = bpy.context.selected_objects
    for obj in imported:
        obj.name = f"{name}_{obj.name}"
    return imported


def create_background_plane(image_path: Path) -> None:
    material = bpy.data.materials.new("Castle 3DGS render backdrop")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(image_path))
    material.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 1.0

    bpy.ops.mesh.primitive_plane_add(size=9.6, location=(0, 2.9, 2.45), rotation=(math.radians(72), 0, 0))
    plane = bpy.context.object
    plane.name = "castle_3dgs_render_backdrop"
    plane.scale.y = 0.5625
    plane.data.materials.append(material)


def add_ground() -> None:
    mat = make_material("island grass placement patch", (0.34, 0.45, 0.24, 1.0), 0.95)
    bpy.ops.mesh.primitive_plane_add(size=2.6, location=(0, 0.55, 0.0), rotation=(0, 0, math.radians(-7)))
    ground = bpy.context.object
    ground.name = "small_grass_patch_for_inserted_assets"
    ground.scale.y = 0.72
    ground.data.materials.append(mat)


def transform_group(objects, location, scale, rotation=(0, 0, 0)) -> None:
    empty = bpy.data.objects.new("asset_transform", None)
    bpy.context.collection.objects.link(empty)
    empty.location = location
    empty.scale = scale
    empty.rotation_euler = rotation
    for obj in objects:
        obj.parent = empty


def setup_camera() -> None:
    bpy.ops.object.light_add(type="SUN", location=(0, -2.0, 6.0), rotation=(math.radians(35), 0, math.radians(-25)))
    sun = bpy.context.object
    sun.name = "scene_sun_match_castle"
    sun.data.energy = 1.8

    bpy.ops.object.light_add(type="AREA", location=(0, -2.6, 4.2))
    light = bpy.context.object
    light.name = "soft_fill_light"
    light.data.energy = 180
    light.data.size = 4

    bpy.ops.object.camera_add(location=(0, -4.6, 2.0), rotation=(math.radians(66), 0, 0))
    camera = bpy.context.object
    bpy.context.scene.camera = camera
    camera.name = "fusion_camera"
    camera.data.lens = 42


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    clear_scene()

    create_background_plane(ASSETS / "castle_3dgs" / "outputs" / "castle_3dgs" / "train" / "ours_7000" / "renders" / "00092.png")
    add_ground()

    treasure = import_obj(ASSETS / "object_B" / "13449_Treasure_Chest_v1_l1.obj", "object_B_treasure_chest")
    transform_group(treasure, location=(-0.36, 0.42, 0.018), scale=(0.013, 0.013, 0.013), rotation=(0, 0, math.radians(-20)))

    dragon = import_obj(ASSETS / "object_C" / "object_C.obj", "object_C_single_image_dragon")
    stone = make_material("object_C_reconstructed_stone", (0.45, 0.43, 0.38, 1.0), 0.92)
    for obj in dragon:
        obj.data.materials.clear()
        obj.data.materials.append(stone)
    transform_group(dragon, location=(0.45, 0.48, 0.018), scale=(0.34, 0.34, 0.34), rotation=(0, 0, math.radians(18)))

    setup_camera()
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.samples = 64
    bpy.context.scene.render.resolution_x = 1600
    bpy.context.scene.render.resolution_y = 900

    blend_path = OUTPUT / "task1_fusion_scene.blend"
    render_path = OUTPUT / "task1_fusion_preview.png"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    bpy.context.scene.render.filepath = str(render_path)
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
