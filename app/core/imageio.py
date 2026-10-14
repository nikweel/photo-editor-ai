"""Чтение и запись изображений: обычные форматы через Pillow, RAW камер через rawpy (LibRaw)."""
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

STANDARD_EXT = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp"}
RAW_EXT = {".cr2", ".cr3", ".nef", ".arw", ".dng", ".orf", ".raf", ".rw2", ".pef", ".srw"}
SUPPORTED_EXT = STANDARD_EXT | RAW_EXT


def open_image(path: Path) -> Image.Image:
    """RGB-изображение с учётом EXIF-ориентации."""
    path = Path(path)
    if path.suffix.lower() in RAW_EXT:
        import rawpy

        with rawpy.imread(str(path)) as raw:
            return Image.fromarray(raw.postprocess(use_camera_wb=True, output_bps=8)).convert("RGB")
    return ImageOps.exif_transpose(Image.open(path)).convert("RGB")


def to_array(im: Image.Image) -> np.ndarray:
    """float32 [H, W, 3] в диапазоне 0..1 (sRGB)."""
    return np.asarray(im.convert("RGB"), np.float32) / 255


def from_array(a: np.ndarray) -> Image.Image:
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))
