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


def open_preview(path: Path, max_side: int) -> tuple[Image.Image, tuple[int, int]]:
    """Уменьшенная копия для показа и миниатюр: (картинка не меньше max_side по длинной стороне, размер оригинала в пикселях).
    JPEG декодируется сразу в уменьшенном виде (масштабирование в самом декодере): в 3–5 раз быстрее и без оригинала в памяти.
    Остальные форматы читаются как обычно."""
    path = Path(path)
    if path.suffix.lower() in RAW_EXT:
        im = open_image(path)  # для RAW берётся встроенный просмотр или быстрая проявка; полного размера не знаем заранее
        return im, im.size
    im = Image.open(path)
    full = im.size
    orient = im.getexif().get(274, 1)
    if orient in (5, 6, 7, 8):  # повёрнутый кадр: ширина и высота меняются местами
        full = (full[1], full[0])
    if im.format == "JPEG" and max(im.size) > max_side:
        k = max_side / max(im.size)
        im.draft("RGB", (max(1, round(im.size[0] * k)), max(1, round(im.size[1] * k))))  # декодер выберет масштаб 1/2, 1/4 или 1/8, не меньше запрошенного
    return ImageOps.exif_transpose(im).convert("RGB"), full


def to_array(im: Image.Image) -> np.ndarray:
    """float32 [H, W, 3] в диапазоне 0..1 (sRGB)."""
    return np.asarray(im.convert("RGB"), np.float32) / 255


def from_array(a: np.ndarray) -> Image.Image:
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))
