"""Признаки кадра для оценки экспозиции с учётом сцены (без Qt).

Вектор признаков = эмбеддинг DINOv2-small (что на кадре: ночь, портрет, закат…) + статистика яркости (насколько кадр светлый).
Обученная «голова» (небольшая нейросеть, models/exposure_scene.onnx) по ним предсказывает, на сколько EV кадр нужно
подправить, и класс сцены. Так тёмный ночной пейзаж остаётся тёмным, а портрет в темноте — осветляется.
"""
import numpy as np
from PIL import Image

from ..core.adjust import srgb_to_linear
from ..core.imageio import from_array

LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)
CLASSES = ("night", "dusk", "portrait", "landscape", "street", "closeup", "backlit")
CLASS_RU = {"night": "ночная сцена", "dusk": "закат/сумерки", "portrait": "портрет", "landscape": "пейзаж", "street": "улица/город",
            "closeup": "крупный план/интерьер", "backlit": "контровой свет"}
EMB_DIM = 384
STAT_DIM = 22
FEATURE_DIM = EMB_DIM + STAT_DIM
_MEAN = np.array([0.485, 0.456, 0.406], np.float32)
_STD = np.array([0.229, 0.224, 0.225], np.float32)
_PCT = (1, 5, 10, 25, 50, 75, 90, 95, 99)


def luminance_stats(img: np.ndarray) -> np.ndarray:
    """22 числа о яркости кадра (float32 RGB 0..1, sRGB). Всё считается в линейном свете и в EV от 18% серого."""
    small = from_array(img)
    small.thumbnail((192, 192))
    a = np.asarray(small, np.float32) / 255.0
    lum = srgb_to_linear(a) @ LUMA
    ev = np.log2(lum + 1e-3)
    h, w = lum.shape
    centre = ev[h // 4 : 3 * h // 4, w // 4 : 3 * w // 4]
    border = np.concatenate([ev[: h // 4].ravel(), ev[3 * h // 4 :].ravel(), ev[:, : w // 4].ravel(), ev[:, 3 * w // 4 :].ravel()])
    sat = a.max(-1) - a.min(-1)
    f = [*np.percentile(ev, _PCT), float(np.mean(ev)), float(np.std(ev)), float(np.mean(lum)), float(np.log2(lum.mean() + 1e-3))]
    f += [float((lum < 0.02).mean()), float((lum < 0.05).mean()), float((lum > 0.9).mean()), float((lum > 0.98).mean())]
    f += [float(centre.mean() - border.mean()), float(ev[: h // 2].mean() - ev[h // 2 :].mean()), float(sat.mean()), float(np.percentile(sat, 90)), float(a.mean(0).mean(0)[0] - a.mean(0).mean(0)[2])]
    out = np.asarray(f, np.float32)
    assert out.shape[0] == STAT_DIM, out.shape
    return out


def embed_input(img: np.ndarray) -> np.ndarray:
    """Кадр -> тензор [1,3,224,224] для DINOv2 (целиком, без обрезки, с нормализацией ImageNet)."""
    r = from_array(img).resize((224, 224), Image.BICUBIC)
    a = (np.asarray(r, np.float32) / 255.0 - _MEAN) / _STD
    return a.transpose(2, 0, 1)[None].astype(np.float32)


def features(embedder, img: np.ndarray) -> np.ndarray:
    """embedder — onnxruntime-сессия DINOv2 (вход pixel_values, выход emb)."""
    emb = embedder.run(None, {"pixel_values": embed_input(img)})[0].reshape(-1)
    return np.concatenate([emb, luminance_stats(img)]).astype(np.float32)


def shift_exposure(img: np.ndarray, ev: float) -> np.ndarray:
    """Имитация съёмки с другой экспозицией: сдвиг в линейном свете с обрезкой (пересвет не восстановить, как и на камере)."""
    from ..core.adjust import linear_to_srgb

    return np.clip(linear_to_srgb(np.clip(srgb_to_linear(img) * float(2.0**ev), 0, 1)), 0, 1).astype(np.float32)
