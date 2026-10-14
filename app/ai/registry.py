"""Каталог ИИ-моделей и движки. Виды моделей:
  ev        — предсказывает поправку экспозиции в EV (вход "image" [1,3,224,224], выход [1,1]);
  enhancer  — изображение в изображение (вход NCHW float32 0..1, выход того же размера), например IAT.
Файл модели лежит в models/<file>. "Встроенная" эвристика работает без файла."""
import json
import logging
import re
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from ..core.imageio import from_array, to_array
from ..utils.paths import DATA_DIR, MODELS_DIR
from . import exposure

log = logging.getLogger(__name__)
ENHANCE_SIDE = 1024  # длинная сторона, на которой работает enhancer; детали переносятся картой усиления


RELEASE = "https://github.com/nikweel/photo-editor-ai/releases/download/models-v0.1/"
ALLOWED_PREFIXES = ("https://github.com/", "file://")  # file:// — для тестов


@dataclass(frozen=True)
class ModelSpec:
    id: str
    name: str
    kind: str          # "builtin" | "ev" | "enhancer"
    file: str = ""
    url: str = ""      # откуда скачать; пусто — положите файл в models/ вручную
    desc: str = ""
    size_bytes: int = 0   # ожидаемый размер и SHA-256: скачанный файл проверяется до подключения
    sha256: str = ""


BUILTIN_MODELS = {m.id: m for m in (
    ModelSpec("heuristic", "Встроенная (гистограмма)", "builtin", desc="Без нейросети, работает всегда"),
    ModelSpec("iat_exposure", "IAT — коррекция экспозиции", "enhancer", "iat_exposure.onnx", RELEASE + "iat_exposure.onnx",
              "Illumination-Adaptive Transformer, веса для исправления пере- и недоэкспозиции", 531698,
              "fbbf6b2ea3baa67316a2a94a88f1b197710afda1ecb34cd4d7b89ff1c1b95a79"),
    ModelSpec("iat_lowlight", "IAT — тёмные снимки", "enhancer", "iat_lowlight.onnx", RELEASE + "iat_lowlight.onnx",
              "Illumination-Adaptive Transformer, веса для съёмки при слабом свете (LOL)", 531698,
              "49f827779720c886d7ea99436d28effce10f905516cf3e81caca2969c2fc1e13"),
    ModelSpec("exposure_ev", "Своя модель EV", "ev", "exposure.onnx", desc="Ваша ONNX-модель по контракту выше"),
)}


CUSTOM_FILE = DATA_DIR / "custom_models.json"
CUSTOM_DIR = MODELS_DIR / "custom"


def models() -> dict[str, ModelSpec]:
    """Встроенные модели и добавленные пользователем (data/custom_models.json)."""
    out = dict(BUILTIN_MODELS)
    try:
        for d in json.loads(CUSTOM_FILE.read_text(encoding="utf-8")):
            out[d["id"]] = ModelSpec(**d)
    except Exception:
        pass
    return out


def _save_custom(specs: list[ModelSpec]) -> None:
    CUSTOM_FILE.parent.mkdir(parents=True, exist_ok=True)
    CUSTOM_FILE.write_text(json.dumps([asdict(m) for m in specs], ensure_ascii=False, indent=1), encoding="utf-8")


def _user_specs() -> list[ModelSpec]:
    return [m for m in models().values() if m.id.startswith("custom_")]


def inspect_onnx(path: Path) -> tuple[str, str]:
    """Определяет вид модели и проверяет её тестовым прогоном. Возвращает (kind, описание); ValueError с понятным текстом, если не подходит."""
    import onnxruntime as ort

    try:
        sess = ort.InferenceSession(Path(path).read_bytes(), providers=["CPUExecutionProvider"])  # байты, а не путь: см. _session
    except Exception as e:
        raise ValueError(f"Файл не открывается как ONNX-модель: {e}") from None
    ins, outs = sess.get_inputs(), sess.get_outputs()
    shp = ins[0].shape
    if len(ins) != 1 or len(shp) != 4 or shp[1] not in (3, "3") or "float" not in ins[0].type:
        raise ValueError(f"Нужен один вход float32 формы [1, 3, H, W] (RGB 0..1), у модели: {[(i.name, i.shape, i.type) for i in ins]}")
    hw = [d if isinstance(d, int) else 64 for d in shp[2:]]
    try:
        out = sess.run(None, {ins[0].name: np.zeros((1, 3, *hw), np.float32) + 0.3})[0]
    except Exception as e:
        raise ValueError(f"Тестовый прогон не удался: {e}") from None
    if out.size == 1:
        return "ev", "предсказывает поправку экспозиции (EV)"
    if out.ndim == 4 and out.shape[1] == 3 and out.shape[2:] == tuple(hw):
        return "enhancer", "изображение в изображение"
    raise ValueError(f"Выход модели {tuple(out.shape)} не подходит: нужно одно число (EV) или картинка [1, 3, H, W] того же размера")


def add_custom(path: Path, name: str) -> ModelSpec:
    kind, what = inspect_onnx(path)
    CUSTOM_DIR.mkdir(parents=True, exist_ok=True)
    base = re.sub(r"[^\w\-]", "_", Path(name).stem, flags=re.UNICODE)[:40] or "model"
    n, mid = 1, f"custom_{base}"
    while mid in models():
        n, mid = n + 1, f"custom_{base}_{n}"
    dest = CUSTOM_DIR / f"{mid}.onnx"
    shutil.copyfile(path, dest)
    spec = ModelSpec(mid, name, kind, f"custom/{dest.name}", desc=f"Своя модель: {what}")
    _save_custom([*_user_specs(), spec])
    return spec


def remove_custom(model_id: str) -> None:
    keep = [m for m in _user_specs() if m.id != model_id]
    gone = next((m for m in _user_specs() if m.id == model_id), None)
    if gone:
        (MODELS_DIR / gone.file).unlink(missing_ok=True)
        _save_custom(keep)


def fetch_verified(url: str, dest: Path, size: int, sha256: str, progress=lambda f, m: None) -> Path:
    """Скачать файл во временный и подключить только после проверки размера и SHA-256 (повреждённый или подменённый файл отбрасывается)."""
    import hashlib
    import urllib.request

    if not url.startswith(ALLOWED_PREFIXES):
        raise ValueError("Загрузка разрешена только с github.com")
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    h, done = hashlib.sha256(), 0
    try:
        with urllib.request.urlopen(url, timeout=30) as r, open(tmp, "wb") as f:
            total = int(r.headers.get("Content-Length") or size or 0)
            while chunk := r.read(64 * 1024):
                f.write(chunk)
                h.update(chunk)
                done += len(chunk)
                if total:
                    progress(min(done / total, 1.0), f"{done / 1e6:.1f} / {total / 1e6:.1f} МБ")
        if (size and done != size) or (sha256 and h.hexdigest() != sha256.lower()):
            raise ValueError("Файл повреждён или не совпадает с ожидаемым (размер или контрольная сумма)")
        tmp.replace(dest)
    finally:
        tmp.unlink(missing_ok=True)
    return dest


def download_model(model_id: str, progress=lambda f, m: None) -> Path:
    spec = models()[model_id]
    if not spec.url:
        raise ValueError("Для этой модели нет адреса загрузки: положите файл в папку models/")
    return fetch_verified(spec.url, MODELS_DIR / spec.file, spec.size_bytes, spec.sha256, progress)


def is_available(model_id: str) -> bool:
    s = models()[model_id]
    return s.kind == "builtin" or (MODELS_DIR / s.file).exists()


def _session(spec: ModelSpec, device: str):
    """Сессия ONNX Runtime. GPU-провайдер (CUDA, DirectML, CoreML) пробуется первым, но любая проблема с ним — нет подходящего
    устройства, неподдерживаемая операция — не должна ломать ИИ: тихо переходим на процессор."""
    import onnxruntime as ort

    # Модель читаем сами и отдаём ONNX Runtime байты: на Windows он не открывает файл по пути с кириллицей и другими
    # не-ANSI символами (например, у пользователя с русским именем профиля) — «No mapping for the Unicode character…».
    path = (MODELS_DIR / spec.file).read_bytes()
    have = ort.get_available_providers()
    gpu = [p for p in ("CUDAExecutionProvider", "DmlExecutionProvider", "CoreMLExecutionProvider") if p in have]
    if device != "cpu" and gpu:
        try:
            return ort.InferenceSession(path, providers=[*gpu, "CPUExecutionProvider"])
        except Exception as e:
            log.warning("GPU (%s) недоступен для модели %s, используем процессор: %s", gpu, spec.id, e)
    return ort.InferenceSession(path, providers=["CPUExecutionProvider"])


class Engine:
    """auto_ev() — для моделей-предсказателей EV; enhance() — для enhancer (None, если не поддерживает)."""

    def __init__(self, model_id: str = "heuristic", device: str = "auto"):
        self.spec = models()[model_id]
        self.session = None
        self.fixed_hw = None
        self._cpu = device == "cpu"  # уже на процессоре — запасного варианта нет
        if self.spec.kind != "builtin":
            self.session = _session(self.spec, device)  # ошибка загрузки (даже на процессоре) пробрасывается: пользователь выбрал именно эту модель
            shp = self.session.get_inputs()[0].shape
            self.fixed_hw = (shp[2], shp[3]) if isinstance(shp[2], int) and isinstance(shp[3], int) else None  # модель с жёстким размером входа

    def _run(self, feed: dict):
        """Расчёт на текущем устройстве; если GPU споткнулся прямо в работе, один раз пересоздаём сессию на процессоре и повторяем."""
        try:
            return self.session.run(None, feed)
        except Exception as e:
            if self._cpu:
                raise
            log.warning("Ошибка расчёта на GPU, переходим на процессор: %s", e)
            self.session, self._cpu = _session(self.spec, "cpu"), True
            return self.session.run(None, feed)

    @property
    def is_enhancer(self) -> bool:
        return self.spec.kind == "enhancer"

    def auto_ev(self, img: np.ndarray) -> float:
        if self.spec.kind == "ev":
            side = self.fixed_hw or (exposure.SIZE, exposure.SIZE)
            small = to_array(from_array(img).resize((side[1], side[0]), Image.BICUBIC)).transpose(2, 0, 1)[None]
            ev = float(self._run({self.session.get_inputs()[0].name: small})[0].reshape(-1)[0])
            return float(np.clip(ev, -exposure.MAX_EV, exposure.MAX_EV))
        return exposure.heuristic_ev(img)

    def enhance(self, img: np.ndarray) -> np.ndarray:
        """Результат enhancer того же размера, что img. Работает на уменьшенной копии, затем переносит
        поправку (отношение результата к исходнику) на полный размер."""
        h, w, _ = img.shape
        k = min(1.0, ENHANCE_SIDE / max(h, w))
        sw, sh = max(8, round(w * k / 8) * 8), max(8, round(h * k / 8) * 8)  # кратно 8 для трансформера
        if self.fixed_hw:
            sh, sw = self.fixed_hw
        small = img if (sw, sh) == (w, h) else to_array(from_array(img).resize((sw, sh), Image.LANCZOS))
        x = small.transpose(2, 0, 1)[None].astype(np.float32)
        y = self._run({self.session.get_inputs()[0].name: x})[0][0].transpose(1, 2, 0)
        y = np.clip(y, 0, 1)
        if (sw, sh) == (w, h):
            return y.astype(np.float32)
        gain = to_array(from_array(np.clip((y + 0.02) / (small + 0.02) / 8, 0, 1)).resize((w, h), Image.BICUBIC)) * 8
        return np.clip(img * gain, 0, 1).astype(np.float32)
