from __future__ import annotations

import argparse
from pathlib import Path

import imageio.v3 as iio
from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract frames from a video for COLMAP/3DGS.")
    parser.add_argument("--video", required=True, help="Input video path, e.g. data/castle.mov")
    parser.add_argument("--output", required=True, help="Output image folder")
    parser.add_argument("--fps", type=float, default=3.0, help="Target frame sampling rate")
    parser.add_argument("--max-size", type=int, default=1600, help="Resize longest side to this size")
    parser.add_argument("--start", type=float, default=0.0, help="Start time in seconds")
    parser.add_argument("--duration", type=float, default=0.0, help="Duration in seconds; 0 means full video")
    return parser.parse_args()


def resize_keep_aspect(frame, max_size: int) -> Image.Image:
    image = Image.fromarray(frame)
    width, height = image.size
    scale = min(1.0, max_size / max(width, height))
    if scale < 1.0:
        image = image.resize((round(width * scale), round(height * scale)), Image.Resampling.LANCZOS)
    return image


def main() -> None:
    args = parse_args()
    video = Path(args.video)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    props = iio.improps(video)
    meta = iio.immeta(video)
    source_fps = float(meta.get("fps", 30.0))
    step = max(1, round(source_fps / args.fps))
    start_frame = round(args.start * source_fps)
    end_frame = None if args.duration <= 0 else start_frame + round(args.duration * source_fps)

    saved = 0
    for index, frame in enumerate(iio.imiter(video)):
        if index < start_frame:
            continue
        if end_frame is not None and index >= end_frame:
            break
        if (index - start_frame) % step != 0:
            continue
        image = resize_keep_aspect(frame, args.max_size)
        image.save(output / f"frame_{saved:05d}.jpg", quality=95)
        saved += 1

    print(f"video={video}")
    print(f"source_fps={source_fps:.3f}")
    print(f"source_shape={props.shape}")
    print(f"target_fps≈{source_fps / step:.3f}")
    print(f"saved_frames={saved}")
    print(f"output={output}")


if __name__ == "__main__":
    main()
