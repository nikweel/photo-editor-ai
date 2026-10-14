"""Каталог фотографий (как в Lightroom): список снимков и их правки хранятся в data/library.json,
сами файлы либо остаются на месте, либо копируются при импорте."""
import hashlib
import json
import logging
import shutil
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from PIL import Image

from ..core.imageio import RAW_EXT, open_preview
from ..utils.paths import DATA_DIR

log = logging.getLogger(__name__)
LIB_FILE = DATA_DIR / "library.json"
THUMB_DIR = DATA_DIR / "cache" / "thumbs"
THUMB_SIDE = 192


@dataclass
class Entry:
    path: str
    params: dict = field(default_factory=dict)  # EditParams.to_dict()
    rating: int = 0                              # 0..5 звёзд


class Library:
    def __init__(self, file: Path = LIB_FILE):
        self.file = file
        self.entries: list[Entry] = []
        try:
            self.entries = [Entry(e["path"], e.get("params") or {k: e[k] for k in ("exposure", "contrast") if k in e}, int(e.get("rating", 0)))
                            for e in json.loads(file.read_text(encoding="utf-8"))]
        except Exception:
            pass

    def save(self) -> None:
        try:
            self.file.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.file.with_suffix(".tmp")
            tmp.write_text(json.dumps([asdict(e) for e in self.entries], ensure_ascii=False), encoding="utf-8")
            tmp.replace(self.file)
        except OSError as e:
            log.warning("Каталог не сохранён: %s", e)

    def get(self, path: Path) -> Entry | None:
        return next((e for e in self.entries if e.path == str(path)), None)

    def add(self, paths: list[Path]) -> list[Path]:
        """Добавляет только новые файлы, возвращает их."""
        have = {e.path for e in self.entries}
        new = [p for p in paths if str(p) not in have]
        self.entries += [Entry(str(p)) for p in new]
        self.save()
        return new

    def remove(self, path: Path) -> None:
        """Убирает из каталога; сам файл не трогаем."""
        self.entries = [e for e in self.entries if e.path != str(path)]
        self.save()

    def remove_missing(self) -> None:
        self.entries = [e for e in self.entries if Path(e.path).exists()]


def capture_date(path: Path) -> datetime:
    """Дата съёмки из EXIF, иначе время изменения файла."""
    try:
        if path.suffix.lower() not in RAW_EXT:
            raw = Image.open(path).getexif().get_ifd(0x8769).get(0x9003) or Image.open(path).getexif().get(306)
            if raw:
                return datetime.strptime(str(raw), "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    return datetime.fromtimestamp(path.stat().st_mtime)


def import_files(files: list[Path], dest: Path | None, by_date: bool = True,
                 progress: Callable[[int, int], None] = lambda d, t: None,
                 should_stop: Callable[[], bool] = lambda: False) -> list[Path]:
    """dest=None — файлы остаются на месте; иначе копируются в dest[/ГГГГ-ММ-ДД]. Чужие файлы не перезаписываются."""
    out: list[Path] = []
    for i, f in enumerate(files):
        if should_stop():
            break
        progress(i, len(files))
        if dest is None:
            out.append(f)
            continue
        try:
            d = dest / capture_date(f).strftime("%Y-%m-%d") if by_date else dest
            d.mkdir(parents=True, exist_ok=True)
            t, n = d / f.name, 1
            while t.exists():
                if t.stat().st_size == f.stat().st_size:  # такой же файл уже импортирован
                    break
                t, n = d / f"{f.stem}_{n}{f.suffix}", n + 1
            if not t.exists():
                shutil.copy2(f, t)
            out.append(t)
        except OSError as e:
            log.warning("Не скопирован %s: %s", f, e)
    progress(len(files), len(files))
    return out


def thumb_for(path: Path, side: int = THUMB_SIDE) -> Path | None:
    """Миниатюра из кэша (создаётся при первом обращении)."""
    try:
        key = hashlib.sha1(f"{path}|{path.stat().st_mtime_ns}|{side}".encode()).hexdigest()
        t = THUMB_DIR / f"{key}.jpg"
        if not t.exists():
            im, _ = open_preview(path, side * 2)  # JPEG декодируется уже уменьшенным
            im.thumbnail((side, side))
            THUMB_DIR.mkdir(parents=True, exist_ok=True)
            im.save(t, quality=85)
        return t
    except Exception as e:
        log.warning("Нет миниатюры %s: %s", path, e)
        return None
