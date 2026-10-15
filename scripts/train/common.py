"""Общее для обучения и бенчмарка: список кадров, разбиение train/test по имени файла, набор сдвигов экспозиции."""
import csv
import hashlib
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
DATA = ROOT / "data" / "train" / "commons"


def dino_path() -> Path:
    from app.utils.paths import MODELS_DIR

    return MODELS_DIR / "dinov2_small.onnx"


def images():
    """[(относительный путь, класс сцены)] из attribution.csv."""
    with open(DATA / "attribution.csv", encoding="utf-8") as f:
        return [(r["file"], r["class"]) for r in csv.DictReader(f) if (DATA / r["file"]).exists()]


def is_test(name: str) -> bool:
    """Фиксированное разбиение по хэшу имени: ~20% кадров никогда не участвуют в обучении."""
    return int(hashlib.md5(name.encode()).hexdigest(), 16) % 5 == 0


def load(name: str, side: int = 512) -> np.ndarray:
    from PIL import Image

    from app.core.imageio import to_array

    im = Image.open(DATA / name)
    im.draft("RGB", (side, side))
    im = im.convert("RGB")
    im.thumbnail((side, side))
    return to_array(im)


def session(threads: int = 4):
    import onnxruntime as ort

    o = ort.SessionOptions()
    o.intra_op_num_threads = threads
    return ort.InferenceSession(dino_path().read_bytes(), o, providers=["CPUExecutionProvider"])


def shifts(rng: np.random.Generator, n: int = 10) -> np.ndarray:
    """40% почти нулевых сдвигов (кадр уже хорош — не трогать), остальные равномерно ±2.5 EV."""
    near = rng.normal(0, 0.12, int(n * 0.4))
    wide = rng.uniform(-2.5, 2.5, n - len(near))
    return np.concatenate([near, wide]).astype(np.float32)
