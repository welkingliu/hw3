from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path("/Users/welkinliu/Desktop/hw3")
SRC = ROOT / "data" / "fusion_assets" / "object_A_3dgs" / "outputs" / "object_A_3dgs" / "train" / "ours_7000" / "renders" / "00051.png"
OUT = ROOT / "outputs" / "task1_fusion" / "object_A_vase_cutout.png"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    image = Image.open(SRC).convert("RGBA")
    crop = image.crop((0, 42, image.width, 430))

    mask = Image.new("L", crop.size, 0)
    draw = ImageDraw.Draw(mask)
    # A hand-tuned soft mask around the vase/flower reconstruction. The final
    # insertion is small, so a feathered silhouette is enough for report figures.
    polygon = [
        (8, 70), (48, 55), (86, 75), (126, 30), (166, 44), (204, 28),
        (250, 62), (325, 88), (332, 198), (274, 242), (230, 258),
        (196, 340), (142, 360), (92, 314), (62, 246), (18, 210)
    ]
    draw.polygon(polygon, fill=255)
    draw.ellipse((74, 190, 250, 378), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(5))

    crop.putalpha(mask)
    crop.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
