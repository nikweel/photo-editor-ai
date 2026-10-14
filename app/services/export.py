"""Экспорт результата: формат, качество, размер по длинной стороне, сохранение EXIF."""
import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from ..core import adjust
from ..core.adjust import EditParams
from ..core.imageio import from_array

log = logging.getLogger(__name__)
FORMATS = {"jpg": "JPEG", "png": "PNG", "webp": "WebP", "tif": "TIFF"}


@dataclass
class ExportOptions:
    fmt: str = "jpg"
    quality: int = 95
    long_side: int = 0       # 0 — исходный размер
    keep_exif: bool = True


def _exif_bytes(src: Path | None) -> bytes | None:
    """EXIF исходника без ориентации: поворот уже применён к пикселям."""
    try:
        ex = Image.open(src).getexif()
        if not ex:
            return None
        ex[274] = 1
        return ex.tobytes()
    except Exception:  # RAW и файлы без EXIF
        return None


def export_image(src: Path | None, img: np.ndarray, params: EditParams, dest: Path, o: ExportOptions) -> Path:
    """img — исходные пиксели (float 0..1); к ним применяются геометрия, цвет и детали из params."""
    im = from_array(adjust.render(img, params))
    if o.long_side and max(im.size) > o.long_side:
        k = o.long_side / max(im.size)
        im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    kw: dict = {}
    exif = _exif_bytes(src) if o.keep_exif and o.fmt in ("jpg", "webp", "tif") else None
    if exif:
        kw["exif"] = exif
    if o.fmt == "jpg":
        kw.update(quality=o.quality, optimize=True, subsampling=0 if o.quality >= 90 else 2)
    elif o.fmt == "webp":
        kw.update(quality=o.quality, method=4)
    elif o.fmt == "png":
        kw.update(compress_level=6)
    elif o.fmt == "tif":
        kw.update(compression="tiff_lzw")
    dest = Path(dest)
    im.save(dest, FORMATS[o.fmt], **kw)
    return dest
