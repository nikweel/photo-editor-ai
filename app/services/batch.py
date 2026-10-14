"""Пакетная обработка: для каждого файла ИИ-автокоррекция + общие правки, сохранение в выходную папку."""
import copy
import logging
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from ..ai.auto import suggest
from ..ai.registry import Engine
from ..core import adjust
from ..core.adjust import EditParams
from ..core.imageio import SUPPORTED_EXT, open_image, to_array
from .export import ExportOptions, export_image

log = logging.getLogger(__name__)


@dataclass
class BatchOptions:
    out_dir: Path
    fmt: str = "jpg"            # jpg | png | webp | tif
    quality: int = 95
    long_side: int = 0          # 0 — исходный размер
    keep_exif: bool = True
    strength: float = 1.0       # 0..1, доля ИИ-поправки
    auto: str = "full"         # "" — без ИИ, "exposure" — только экспозиция, "full" — экспозиция и цвет
    contrast: float = 0.0       # общая правка поверх ИИ
    params: EditParams | None = None  # ручные настройки (например, с открытого фото), применяются ко всем
    suffix: str = "_edit"


def collect_files(paths: list[Path], recursive: bool = True) -> list[Path]:
    out: list[Path] = []
    for p in paths:
        if p.is_dir():
            it = p.rglob("*") if recursive else p.glob("*")
            out += sorted(f for f in it if f.suffix.lower() in SUPPORTED_EXT and f.is_file())
        elif p.suffix.lower() in SUPPORTED_EXT:
            out.append(p)
    return out


def _target(src: Path, o: BatchOptions) -> Path:
    t = o.out_dir / f"{src.stem}{o.suffix}.{o.fmt}"
    n = 1
    while t.exists():  # не перезаписываем чужие файлы
        t = o.out_dir / f"{src.stem}{o.suffix}_{n}.{o.fmt}"
        n += 1
    return t


def process_one(src: Path, engine: Engine, o: BatchOptions) -> Path:
    img = to_array(open_image(src))
    if o.auto:
        sug = {k: v * o.strength for k, v in suggest(engine, img, o.auto).items()}
        img = adjust.apply(img, EditParams(**sug))
    p = copy.deepcopy(o.params) if o.params is not None else EditParams()
    p.contrast = min(max(p.contrast + o.contrast, -1.0), 1.0)
    dst = _target(src, o)
    return export_image(src, img, p, dst, ExportOptions(o.fmt, o.quality, o.long_side, o.keep_exif))


def run_batch(files: list[Path], engine: Engine, o: BatchOptions,
              progress: Callable[[int, int, str], None] = lambda d, t, n: None,
              should_stop: Callable[[], bool] = lambda: False) -> tuple[int, list[tuple[Path, str]]]:
    """Возвращает (число обработанных, список ошибок). Битый файл не останавливает пакет."""
    o.out_dir.mkdir(parents=True, exist_ok=True)
    ok, errors = 0, []
    for i, f in enumerate(files):
        if should_stop():
            break
        progress(i, len(files), f.name)
        try:
            process_one(f, engine, o)
            ok += 1
        except Exception as e:
            log.warning("Пропущен %s: %s", f, e)
            errors.append((f, str(e)))
    progress(len(files), len(files), "")
    return ok, errors
