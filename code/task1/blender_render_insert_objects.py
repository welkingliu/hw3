"""Render inserted mesh assets on a transparent background for compositing."""

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


def make_material(name: str, color: tuple[float, float, float, float], roughness: float = 0.7):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
    return material


def import_obj(path: Path, name: str):
    bpy.ops.wm.obj_import(filepath=str(path))
    imported = list(bpy.context.selected_objects)
    for obj in imported:
        obj.name = f"{name}_{obj.name}"
    return imported


def transform_group(objects, location, scale, rotation=(0, 0, 0)) -> None:
    empty = bpy.data.objects.new("asset_transform", None)
    bpy.context.collection.objects.link(empty)
    empty.location = location
    empty.scale = scale
    empty.rotation_euler = rotation
    for obj in objects:
        obj.parent = empty


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    clear_scene()

    treasure = import_obj(ASSETS / "object_B" / "13449_Treasure_Chest_v1_l1.obj", "object_B_treasure_chest")
    transform_group(treasure, location=(-0.42, 0.0, -0.50), scale=(0.018, 0.018, 0.018), rotation=(0, 0, math.radians(-18)))

    dragon = import_obj(ASSETS / "object_C" / "object_C.obj", "object_C_single_image_dragon")
    stone = make_material("object_C_reconstructed_stone", (0.46, 0.44, 0.39, 1.0), 0.9)
    for obj in dragon:
        obj.data.materials.clear()
        obj.data.materials.append(stone)
    transform_group(dragon, location=(0.38, 0.04, -0.50), scale=(0.42, 0.42, 0.42), rotation=(0, 0, math.radians(18)))

    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(45), 0, math.radians(-32)))
    sun = bpy.context.object
    sun.data.energy = 2.0
    bpy.ops.object.light_add(type="AREA", location=(0, -3, 4))
    fill = bpy.context.object
    fill.data.energy = 220
    fill.data.size = 5

    bpy.ops.object.camera_add(location=(0, -4.0, 1.2), rotation=(math.radians(75), 0, 0))
    camera = bpy.context.object
    bpy.context.scene.camera = camera
    camera.data.lens = 46

    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.samples = 96
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.view_settings.view_transform = "Filmic"
    bpy.context.scene.render.resolution_x = 900
    bpy.context.scene.render.resolution_y = 520
    bpy.context.scene.render.filepath = str(OUTPUT / "inserted_objects_transparent.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
