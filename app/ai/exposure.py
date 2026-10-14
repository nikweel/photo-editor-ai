"""Автоэкспозиция: ИИ-модель (ONNX) предсказывает поправку в EV; без модели работает эвристика по гистограмме.

Контракт модели models/exposure.onnx:
  вход  "image"  float32 [1, 3, 224, 224], sRGB 0..1 (уменьшенное изображение целиком)
  выход          float32 [1, 1] — поправка экспозиции в EV (ступенях)
"""
import logging

import numpy as np
from PIL import Image

from ..core.adjust import srgb_to_linear
from ..core.imageio import from_array, to_array
from ..utils.paths import MODELS_DIR

log = logging.getLogger(__name__)
MODEL_FILE = "exposure.onnx"
SIZE = 224
MAX_EV = 3.0


def heuristic_ev(img: np.ndarray) -> float:
    """Средний тон к 18% серого, но так, чтобы света (99-й перцентиль) не уходили в пересвет."""
    lum = srgb_to_linear(img) @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    mid = float(np.exp(np.mean(np.log(lum + 1e-4))))
    ev = float(np.log2(0.18 / max(mid, 1e-4)))
    hi = float(np.percentile(lum, 99))
    if hi > 1e-4:
        ev = min(ev, float(np.log2(1.0 / hi)))  # потолок: свет не должен превысить белый
    return float(np.clip(ev, -MAX_EV, MAX_EV))


class ExposureModel:
    def __init__(self, device: str = "auto"):
        self.session = None
        path = MODELS_DIR / MODEL_FILE
        if path.exists():
            try:
                import onnxruntime as ort

                have = ort.get_available_providers()
                prov = [p for p in ("CUDAExecutionProvider", "DmlExecutionProvider", "CoreMLExecutionProvider") if p in have]
                self.session = ort.InferenceSession(str(path), providers=[*prov, "CPUExecutionProvider"] if device != "cpu" else ["CPUExecutionProvider"])
            except Exception as e:  # битая модель или нет GPU -> откат на эвристику
                log.warning("Модель экспозиции не загружена, используем эвристику: %s", e)

    @property
    def name(self) -> str:
        return "ИИ-модель" if self.session else "эвристика"

    def predict_ev(self, img: np.ndarray) -> float:
        if self.session is None:
            return heuristic_ev(img)
        small = to_array(from_array(img).resize((SIZE, SIZE), Image.BICUBIC)).transpose(2, 0, 1)[None]
        ev = float(self.session.run(None, {"image": small})[0].reshape(-1)[0])
        return float(np.clip(ev, -MAX_EV, MAX_EV))
