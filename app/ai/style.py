"""«Мой стиль»: приложение учится на правках пользователя в каталоге и предлагает похожие настройки для новых кадров (без Qt).

Признаки кадра — статистика яркости и среднего цвета исходника (до правок), ответ — значения ползунков, которые выставил пользователь.
Модель — гребневая регрессия (ridge) с сильной регуляризацией: на 30–100 кадрах она не запоминает, а ловит привычки
(«тёмные кадры подтягиваю на +0,7 EV, тени открываю, добавляю тепла»). Качество честно оценивается перекрёстной проверкой (leave-one-out).
"""
import json
import logging
from pathlib import Path

import numpy as np

from ..core.adjust import EditParams
from ..core.imageio import open_preview, to_array
from ..utils.paths import DATA_DIR
from .scene import luminance_stats

log = logging.getLogger(__name__)
STYLE_FILE = DATA_DIR / "style.json"
KEYS = ("exposure", "contrast", "highlights", "shadows", "whites", "blacks", "temperature", "tint", "vibrance", "saturation", "texture", "dehaze", "clarity", "vignette")
MIN_PHOTOS = 12  # меньше — выводов делать рано
ALPHA = 12.0     # сила регуляризации (на стандартизованных признаках)


def style_features(img: np.ndarray) -> np.ndarray:
    return np.concatenate([luminance_stats(img), img.reshape(-1, 3).mean(0)]).astype(np.float32)


def edit_vector(params: dict) -> np.ndarray:
    p = EditParams.from_dict(params)
    return np.array([getattr(p, k) for k in KEYS], np.float32)


def is_edited(params: dict) -> bool:
    return bool(params) and bool(np.any(np.abs(edit_vector(params)) > 1e-6))


class StyleModel:
    def __init__(self, mean=None, std=None, beta=None, bias=None, n=0, gain=0.0):
        self.mean, self.std, self.beta, self.bias, self.n, self.gain = mean, std, beta, bias, n, gain  # gain — доля объяснённой дисперсии (LOO)

    @staticmethod
    def _solve(Z: np.ndarray, Y: np.ndarray):
        bias = Y.mean(0)
        beta = np.linalg.solve(Z.T @ Z + ALPHA * np.eye(Z.shape[1]), Z.T @ (Y - bias))
        return beta, bias

    @classmethod
    def fit(cls, X: np.ndarray, Y: np.ndarray) -> "StyleModel":
        mean, std = X.mean(0), X.std(0) + 1e-6
        Z = (X - mean) / std
        beta, bias = cls._solve(Z, Y)
        # leave-one-out: насколько модель лучше, чем «всегда средние настройки пользователя»
        err_m = err_b = 0.0
        for i in range(len(X)):
            keep = np.arange(len(X)) != i
            b, c = cls._solve(Z[keep], Y[keep])
            err_m += float(((Z[i] @ b + c - Y[i]) ** 2).sum())
            err_b += float(((Y[keep].mean(0) - Y[i]) ** 2).sum())
        gain = 1 - err_m / err_b if err_b > 1e-9 else 0.0
        return cls(mean, std, beta, bias, len(X), float(gain))

    def predict(self, feats: np.ndarray) -> dict:
        y = ((feats - self.mean) / self.std) @ self.beta + self.bias
        return {k: float(v) for k, v in zip(KEYS, y)}

    def to_json(self) -> dict:
        return {"n": self.n, "gain": self.gain, "mean": self.mean.tolist(), "std": self.std.tolist(), "beta": self.beta.tolist(), "bias": self.bias.tolist(), "keys": list(KEYS)}

    @classmethod
    def from_json(cls, d: dict) -> "StyleModel":
        if list(d.get("keys", [])) != list(KEYS):
            raise ValueError("Модель стиля сохранена для другого набора параметров")
        return cls(np.array(d["mean"], np.float32), np.array(d["std"], np.float32), np.array(d["beta"], np.float32), np.array(d["bias"], np.float32), int(d["n"]), float(d["gain"]))


def save(model: StyleModel, file: Path = STYLE_FILE) -> None:
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps(model.to_json()), encoding="utf-8")


def load(file: Path = STYLE_FILE) -> StyleModel | None:
    try:
        return StyleModel.from_json(json.loads(file.read_text(encoding="utf-8")))
    except (OSError, ValueError, KeyError):
        return None


def train(entries, progress=lambda i, n: None, max_photos: int = 300, side: int = 256) -> StyleModel | None:
    """Учится на правленых кадрах каталога (entries — объекты с path и params). None, если правленых мало или файлы недоступны."""
    edited = [e for e in entries if is_edited(e.params) and Path(e.path).exists()][-max_photos:]
    X, Y = [], []
    for i, e in enumerate(edited):
        progress(i, len(edited))
        try:
            im, _ = open_preview(Path(e.path), side)
            X.append(style_features(to_array(im)))
            Y.append(edit_vector(e.params))
        except Exception as ex:
            log.warning("Пропуск %s: %s", e.path, ex)
    if len(X) < MIN_PHOTOS:
        return None
    return StyleModel.fit(np.array(X), np.array(Y))
