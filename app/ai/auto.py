"""Умная автокоррекция. Нейросеть-enhancer сама по себе склонна пересвечивать (особенно модель для тёмных кадров),
поэтому из её результата берётся только «что она хочет изменить» (EV и баланс цвета), а итог усредняется с оценкой
по гистограмме и ограничивается защитой светов. Возвращаются обычные редактируемые параметры, а не готовые пиксели."""
import numpy as np
from PIL import Image

from ..core.adjust import LUMA, srgb_to_linear
from ..core.imageio import from_array, to_array
from . import exposure
from .registry import Engine

MAX_SIDE = 1024        # анализ на уменьшенной копии
MAX_EV = 2.5
TARGET_MEDIAN = 0.30   # линейная яркость медианы, выше которой снимок не осветляем (~sRGB 0.58)
HEADROOM_EV = 0.3      # допустимый небольшой пересвет сверх 99,5-го перцентиля: свет сглаживает «плечо» в apply()
MAX_TEMP, MAX_TINT = 0.4, 0.3


def _small(img: np.ndarray) -> np.ndarray:
    h, w, _ = img.shape
    k = min(1.0, MAX_SIDE / max(h, w))
    return img if k == 1 else to_array(from_array(img).resize((max(1, round(w * k)), max(1, round(h * k))), Image.BILINEAR))


def _ev_cap(lin_lum: np.ndarray) -> float:
    """Максимум EV, при котором света не уйдут в белое."""
    p = float(np.percentile(lin_lum, 99.5))
    cap = float(np.log2(1.0 / max(p, 1e-3))) + HEADROOM_EV
    med = float(np.median(lin_lum))
    return min(cap, float(np.log2(TARGET_MEDIAN / max(med, 1e-4))))


def _gains_to_wb(g: np.ndarray) -> tuple[float, float]:
    """Коэффициенты по каналам -> (температура, оттенок) в терминах core.adjust (R*=1+.35T, B*=1-.35T, G*=1-.2tint)."""
    q = g[0] / max(g[2], 1e-4)
    temp = (q - 1) / (0.35 * (q + 1))
    tint = (1 - g[1] / max((g[0] + g[2]) / 2, 1e-4)) / 0.2
    return float(np.clip(temp, -MAX_TEMP, MAX_TEMP)), float(np.clip(tint, -MAX_TINT, MAX_TINT))


def _gray_world_gains(lin: np.ndarray) -> np.ndarray:
    """Серый мир по средним тонам (без почти чёрных и почти белых пикселей, они искажают оценку)."""
    lum = lin @ LUMA
    m = (lum > 0.03) & (lum < 0.7)
    px = lin[m] if m.sum() > 100 else lin.reshape(-1, 3)
    mean = px.mean(0)
    return mean.mean() / np.maximum(mean, 1e-4)


def _verdict(ev: float, kind: str) -> str:
    name = scene_ru(kind)
    if ev <= -0.3:
        return f"{name}: кадр пересвечен, притемняю на {abs(ev):.1f} EV"
    if ev >= 0.3:
        return f"{name}: кадр тёмный, осветляю на {ev:.1f} EV"
    return f"{name}: экспозиция в порядке" + (", темнота задумана — оставляю" if kind == "night" else "")


def scene_ru(kind: str) -> str:
    from .scene import CLASS_RU

    return CLASS_RU.get(kind, kind).capitalize()


def suggest(engine: Engine, img: np.ndarray, mode: str = "full") -> dict:
    """mode: "exposure" — только экспозиция; "full" — экспозиция и цвет. Результат: {параметр EditParams: значение}."""
    s = _small(img)
    lin = srgb_to_linear(s)
    lum = lin @ LUMA
    ev = exposure.heuristic_ev(s)
    gains = _gray_world_gains(lin)
    if engine.is_enhancer:
        enh_lin = srgb_to_linear(engine.enhance(s))
        med_o, med_e = float(np.median(lum)), float(np.median(enh_lin @ LUMA))
        ev_model = float(np.log2(max(med_e, 1e-4) / max(med_o, 1e-4)))
        ev = (ev + ev_model) / 2  # ИИ и гистограмма «голосуют» вместе — выбросы одного гасятся другим
        ratio = np.median(enh_lin.reshape(-1, 3), 0) / np.maximum(np.median(lin.reshape(-1, 3), 0), 1e-4)
        ratio = ratio / max(float(np.exp(np.log(np.maximum(ratio, 1e-4)).mean())), 1e-4)  # убираем часть, ответственную за яркость
        gains = np.sqrt(gains * ratio)  # цвет: среднее геометрическое оценки модели и серого мира
    kind = None
    if engine.spec.kind == "scene":
        ev, kind, conf = engine.scene_analyze(s)  # модель сама решает, что кадр пересвечен, тёмный по замыслу или тёмный по ошибке
    ev = float(np.clip(min(ev, _ev_cap(lum)) if ev > 0 else ev, -MAX_EV, MAX_EV))
    out = {"exposure": 0.0 if abs(ev) < 0.1 else ev}
    if kind:
        out["scene"] = kind
        out["verdict"] = _verdict(ev, kind)
    if mode == "full":
        temp, tint = _gains_to_wb(gains)
        k_wb = 0.25 if kind in ("night", "dusk") else 0.5  # цветные огни ночью и закатный свет — не ошибка баланса белого
        out["temperature"], out["tint"] = (temp * k_wb, tint * k_wb) if abs(temp) > 0.03 or abs(tint) > 0.03 else (0.0, 0.0)
        sat = float(np.mean(s.max(-1) - s.min(-1)))
        out["vibrance"] = float(np.clip((0.28 - sat) * 0.8, 0, 0.25))
    return out
