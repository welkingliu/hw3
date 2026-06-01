from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path("/Users/welkinliu/Desktop/hw3")
OUTPUT = ROOT / "outputs" / "task1_fusion"
BACKGROUND = ROOT / "data" / "fusion_assets" / "castle_3dgs" / "outputs" / "castle_3dgs" / "train" / "ours_7000" / "renders" / "00092.png"
OBJECTS = OUTPUT / "inserted_objects_transparent.png"
OBJECT_A = OUTPUT / "object_A_vase_cutout.png"


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    bg = Image.open(BACKGROUND).convert("RGBA")
    obj = Image.open(OBJECTS).convert("RGBA")
    bbox = obj.getchannel("A").getbbox()
    if bbox:
        pad = 18
        bbox = (
            max(0, bbox[0] - pad),
            max(0, bbox[1] - pad),
            min(obj.width, bbox[2] + pad),
            min(obj.height, bbox[3] + pad),
        )
        obj = obj.crop(bbox)

    target_width = 92
    scale = target_width / obj.width
    obj = obj.resize((target_width, round(obj.height * scale)), Image.Resampling.LANCZOS)

    x = 500
    y = 258

    shadow = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    draw.ellipse((x + 10, y + obj.height - 18, x + target_width - 4, y + obj.height - 3), fill=(0, 0, 0, 55))
    shadow = shadow.filter(ImageFilter.GaussianBlur(5))
    bg.alpha_composite(shadow)
    bg.alpha_composite(obj, (x, y))

    if OBJECT_A.exists():
        vase = Image.open(OBJECT_A).convert("RGBA")
        vase_width = 76
        scale = vase_width / vase.width
        vase = vase.resize((vase_width, round(vase.height * scale)), Image.Resampling.LANCZOS)
        vx, vy = 418, 274
        vase_shadow = Image.new("RGBA", bg.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(vase_shadow)
        draw.ellipse((vx + 18, vy + vase.height - 13, vx + vase_width - 14, vy + vase.height - 2), fill=(0, 0, 0, 45))
        vase_shadow = vase_shadow.filter(ImageFilter.GaussianBlur(4))
        bg.alpha_composite(vase_shadow)
        bg.alpha_composite(vase, (vx, vy))

    out = OUTPUT / "task1_fusion_composite.png"
    bg.convert("RGB").save(out, quality=95)
    print(out)


if __name__ == "__main__":
    main()
