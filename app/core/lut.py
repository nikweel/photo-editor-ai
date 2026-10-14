"""3D LUT в формате .cube (стандарт для фильтров Lightroom, Luminar, DaVinci и др.)."""
from functools import lru_cache
from pathlib import Path

import numpy as np

MAX_SIZE = 65
MAX_BYTES = 64 * 1024 * 1024


class LutError(ValueError):
    pass


@lru_cache(maxsize=8)
def load_cube(path: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(таблица [N, N, N, 3] с осями [b][g][r], domain_min, domain_max)."""
    p = Path(path)
    if p.stat().st_size > MAX_BYTES:
        raise LutError("Файл слишком большой")
    size, dmin, dmax, rows = 0, np.zeros(3, np.float32), np.ones(3, np.float32), []
    for line in p.read_text(encoding="utf-8", errors="strict").splitlines():
        parts = line.split("#")[0].split()
        if not parts:
            continue
        key = parts[0].upper()
        if key == "LUT_3D_SIZE":
            size = int(parts[1])
        elif key == "LUT_1D_SIZE":
            raise LutError("1D-LUT не поддерживается, нужен 3D (.cube с LUT_3D_SIZE)")
        elif key == "DOMAIN_MIN":
            dmin = np.array(parts[1:4], np.float32)
        elif key == "DOMAIN_MAX":
            dmax = np.array(parts[1:4], np.float32)
        elif key in ("TITLE", "LUT_3D_INPUT_RANGE") or not (parts[0][0].isdigit() or parts[0][0] in "-+."):
            continue
        else:
            rows.append([float(v) for v in parts[:3]])
    if not 2 <= size <= MAX_SIZE or len(rows) != size**3:
        raise LutError("Неверный .cube: размер таблицы не совпадает с данными")
    return np.array(rows, np.float32).reshape(size, size, size, 3), dmin, dmax


def apply_lut(img: np.ndarray, path: str, strength: float = 1.0) -> np.ndarray:
    """Тетраэдры не нужны: обычная трилинейная интерполяция, по кускам строк ради памяти."""
    table, dmin, dmax = load_cube(path)
    n = table.shape[0]
    out = np.empty_like(img)
    for y0 in range(0, img.shape[0], 256):
        a = (np.clip(img[y0:y0 + 256], 0, 1) - dmin) / np.maximum(dmax - dmin, 1e-6) * (n - 1)
        a = np.clip(a, 0, n - 1)
        i0 = np.minimum(a.astype(np.int32), n - 2)
        f = a - i0
        r0, g0, b0 = i0[..., 0], i0[..., 1], i0[..., 2]
        fr, fg, fb = f[..., 0:1], f[..., 1:2], f[..., 2:3]
        res = 0
        for db in (0, 1):
            for dg in (0, 1):
                for dr in (0, 1):
                    w = (fr if dr else 1 - fr) * (fg if dg else 1 - fg) * (fb if db else 1 - fb)
                    res = res + w * table[b0 + db, g0 + dg, r0 + dr]
        out[y0:y0 + 256] = res
    out = np.clip(out, 0, 1)
    return img + (out - img) * strength if strength < 1 else out
