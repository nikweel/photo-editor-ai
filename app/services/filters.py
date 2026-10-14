"""Фильтры (пресеты) и пакеты фильтров: встроенные, свои и загруженные из файла.

Файлы:
  .json  — один фильтр (format "photo-editor-ai-filter") или пакет фильтров (format "photo-editor-ai-pack");
  .cube  — 3D LUT, добавляется как фильтр в пакет «Мои фильтры».
Пользовательское лежит в data/presets/: отдельные фильтры — <имя>.json / <имя>.cube, пакеты — <имя>.pack.json.
Содержимое чужих файлов проверяется до сохранения; пути к LUT из JSON не принимаются (фильтр с LUT делается только из .cube)."""
import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from ..core.adjust import CHANNELS, IDENTITY_MIX, EditParams
from ..core.lut import load_cube
from ..utils.paths import DATA_DIR
from .builtin_filters import BASE_TYPES, CATEGORIES, PACKS, SITE_PACK, SITE_TYPES

PRESET_DIR = DATA_DIR / "presets"
FORMAT = "photo-editor-ai-filter"
PACK_FORMAT = "photo-editor-ai-pack"
MY_PACK = "Мои фильтры"
MAX_JSON = 5 * 1024 * 1024
MAX_PACK_FILTERS = 500
DEFAULT_CATEGORY = "Другое"


@dataclass
class Filter:
    name: str
    params: EditParams
    builtin: bool = False
    path: Path | None = None  # файл пользовательского фильтра или пакета, в котором он лежит
    pack: str = ""
    category: str = ""


@dataclass
class Pack:
    name: str
    filters: list[Filter] = field(default_factory=list)
    builtin: bool = False
    path: Path | None = None  # файл пакета (None у встроенных и у «Мои фильтры», который собирается из отдельных файлов)
    description: str = ""


@dataclass
class ImportResult:
    kind: str   # "filter" | "pack" | "lut"
    name: str
    count: int  # сколько фильтров добавлено


# ---------- встроенные пакеты ----------
SITE_FILE = Path(__file__).with_name("presets_site.json")


def _site_filters() -> list[Filter]:
    """Фильтры, подобранные по парам «до/после» (scripts/fit_filters.py). Сами файлы чужих пресетов не используются:
    это численное приближение вида по паре кадров."""
    try:
        data = json.loads(SITE_FILE.read_text(encoding="utf-8"))
        return [Filter(name, EditParams.from_dict(d["params"]), True, None, SITE_PACK[0], SITE_TYPES.get(name, "Кино")) for name, d in data.items()]
    except Exception:
        return []  # нет файла или он повреждён — остальные фильтры работают


def builtin_packs() -> list[Pack]:
    packs = []
    for name, desc, items, default_cat, types in PACKS:
        packs.append(Pack(name, [Filter(n, p, True, None, name, types.get(n, default_cat)) for n, p in items], True, None, desc))
    site = _site_filters()
    if site:
        packs.append(Pack(SITE_PACK[0], site, True, None, SITE_PACK[1]))
    return packs


BUILTIN_PACKS = builtin_packs()
BUILTIN = [f for pk in BUILTIN_PACKS for f in pk.filters]  # плоский список всех встроенных фильтров


def blend(f: EditParams, s: float) -> EditParams:
    """Фильтр с силой s (0..1): параметры и кривые смешиваются с «ничего не менять»."""
    out = EditParams.from_dict(f.to_dict())
    for k in ("exposure", "contrast", "highlights", "shadows", "whites", "blacks", "temperature", "tint", "vibrance", "saturation", "sharpen", "clarity",
              "noise_color", "vignette", "grain", "texture", "dehaze"):
        setattr(out, k, getattr(f, k) * s)
    for c in CHANNELS:
        out.curves[c] = [[x, x + (y - x) * s] for x, y in f.curves[c]]
    out.lut_strength = f.lut_strength * s
    out.hsl = {c: [v * s for v in vals] for c, vals in f.hsl.items()}
    out.mix = [i + (m - i) * s for m, i in zip(f.mix, IDENTITY_MIX)]
    return out


def _safe(name: str) -> str:
    return re.sub(r"[^\w\- ]", "_", name, flags=re.UNICODE).strip()[:60] or "filter"


def _clean(text, limit: int, default: str = "") -> str:
    t = str(text).strip() if isinstance(text, (str, int, float)) else ""
    return t[:limit] or default


def _params_from_json(d) -> EditParams:
    """Параметры из чужого JSON. Путь к LUT не принимаем: файл на диске мог бы указывать на что угодно."""
    if not isinstance(d, dict):
        raise ValueError("Некорректные параметры фильтра")
    p = EditParams.from_dict(d)
    p.lut = ""
    return p


def _entry_json(name: str, category: str, params: EditParams) -> dict:
    d = params.to_dict()
    d.pop("lut", None)
    d.pop("lut_strength", None)
    return {"name": name, "category": category, "params": d}


class FilterStore:
    def __init__(self, folder: Path = PRESET_DIR):
        self.dir = folder

    # ---------- чтение ----------
    def _load_json(self, path: Path) -> dict:
        if path.stat().st_size > MAX_JSON:
            raise ValueError("Файл слишком большой")
        d = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(d, dict):
            raise ValueError("Это не файл Photo Editor AI")
        return d

    def _read_pack(self, path: Path) -> Pack:
        d = self._load_json(path)
        if d.get("format") != PACK_FORMAT or not isinstance(d.get("filters"), list):
            raise ValueError("Это не файл пакета фильтров Photo Editor AI")
        name = _clean(d.get("name"), 80, path.name.removesuffix(".pack.json"))
        pk = Pack(name, [], False, path, _clean(d.get("description"), 300))
        for e in d["filters"][:MAX_PACK_FILTERS]:
            try:
                pk.filters.append(Filter(_clean(e["name"], 80, "Фильтр"), _params_from_json(e.get("params")), False, path, name, _clean(e.get("category"), 40, DEFAULT_CATEGORY)))
            except Exception:
                continue  # одна повреждённая запись не должна ломать пакет
        return pk

    def user_packs(self) -> list[Pack]:
        """Пакеты пользователя: файлы *.pack.json и пакет «Мои фильтры» из отдельных .json/.cube."""
        packs, loose = [], []
        for f in sorted(self.dir.glob("*")) if self.dir.exists() else []:
            try:
                if f.name.endswith(".pack.json"):
                    packs.append(self._read_pack(f))
                elif f.suffix == ".json":
                    d = self._load_json(f)
                    if d.get("format") != FORMAT:
                        continue
                    loose.append(Filter(f.stem, _params_from_json(d.get("params")), False, f, MY_PACK, _clean(d.get("category"), 40, DEFAULT_CATEGORY)))
                elif f.suffix == ".cube":
                    loose.append(Filter(f.stem, EditParams(lut=str(f)), False, f, MY_PACK, "Другое"))
            except Exception:
                continue  # битый файл не должен ломать список
        return ([Pack(MY_PACK, loose, False, None, "Ваши отдельные фильтры и LUT")] if loose else []) + packs

    def packs(self) -> list[Pack]:
        return BUILTIN_PACKS + self.user_packs()

    def user_filters(self) -> list[Filter]:
        return [f for pk in self.user_packs() for f in pk.filters]

    def all(self) -> list[Filter]:
        return [f for pk in self.packs() for f in pk.filters]

    def pack_names(self) -> list[str]:
        """Имена пакетов пользователя, куда можно добавлять фильтры (всегда включая «Мои фильтры»)."""
        names = [p.name for p in self.user_packs() if p.name != MY_PACK]
        return [MY_PACK] + names

    # ---------- запись ----------
    def _free(self, name: str, ext: str) -> Path:
        self.dir.mkdir(parents=True, exist_ok=True)
        t, n = self.dir / f"{_safe(name)}{ext}", 2
        while t.exists():
            t, n = self.dir / f"{_safe(name)} {n}{ext}", n + 1
        return t

    def _unique_pack_name(self, name: str) -> str:
        taken = {p.name for p in self.packs()} | {MY_PACK}
        base, n, cand = name, 2, name
        while cand in taken:
            cand, n = f"{base} ({n})", n + 1
        return cand

    def _write_pack(self, path: Path, name: str, description: str, entries: list[dict]) -> None:
        path.write_text(json.dumps({"format": PACK_FORMAT, "version": 1, "name": name, "description": description, "filters": entries},
                                   ensure_ascii=False, indent=1), encoding="utf-8")

    def save_user(self, name: str, params: EditParams, pack: str = MY_PACK, category: str = DEFAULT_CATEGORY) -> Filter:
        """Сохранить фильтр в свой пакет. Пакета ещё нет — создаётся; встроенные пакеты менять нельзя."""
        name, pack, category = _clean(name, 80, "Фильтр"), _clean(pack, 80, MY_PACK), _clean(category, 40, DEFAULT_CATEGORY)
        p = EditParams.from_dict(params.to_dict())
        p.lut = ""
        if pack in {b.name for b in BUILTIN_PACKS}:
            raise ValueError(f"Пакет «{pack}» встроенный — выберите свой пакет или создайте новый")
        if pack == MY_PACK:
            t = self._free(name, ".json")
            t.write_text(json.dumps({"format": FORMAT, "version": 1, "name": name, "category": category, "params": p.to_dict()}, ensure_ascii=False, indent=1),
                         encoding="utf-8")
            return Filter(t.stem, p, False, t, MY_PACK, category)
        target = next((x for x in self.user_packs() if x.name == pack and x.path), None)
        if target is None:
            path, entries, desc = self._free(pack, ".pack.json"), [], ""
        else:
            path, entries, desc = target.path, [_entry_json(f.name, f.category, f.params) for f in target.filters], target.description
        used = {e["name"] for e in entries}
        uniq, n = name, 2
        while uniq in used:
            uniq, n = f"{name} {n}", n + 1
        entries.append(_entry_json(uniq, category, p))
        self._write_pack(path, pack, desc, entries)
        return Filter(uniq, p, False, path, pack, category)

    def import_file(self, src: Path) -> ImportResult:
        """Загрузить фильтр, пакет или LUT; содержимое проверяется до копирования."""
        src = Path(src)
        ext = src.suffix.lower()
        if ext == ".cube":
            load_cube.cache_clear()
            load_cube(str(src))  # LutError, если файл неверный
            t = self._free(src.stem, ".cube")
            shutil.copyfile(src, t)
            return ImportResult("lut", t.stem, 1)
        if ext != ".json":
            raise ValueError("Поддерживаются файлы .json (фильтр или пакет) и .cube")
        d = self._load_json(src)
        if d.get("format") == PACK_FORMAT:
            tmp = self._read_pack(src)  # проверка и очистка
            if not tmp.filters:
                raise ValueError("В пакете нет ни одного корректного фильтра")
            name = self._unique_pack_name(tmp.name)
            path = self._free(name, ".pack.json")
            self._write_pack(path, name, tmp.description, [_entry_json(f.name, f.category, f.params) for f in tmp.filters])
            return ImportResult("pack", name, len(tmp.filters))
        if d.get("format") == FORMAT:
            p = _params_from_json(d.get("params"))
            name = _clean(d.get("name"), 80, src.stem)
            t = self._free(name, ".json")
            t.write_text(json.dumps({"format": FORMAT, "version": 1, "name": name, "category": _clean(d.get("category"), 40, DEFAULT_CATEGORY),
                                     "params": p.to_dict()}, ensure_ascii=False, indent=1), encoding="utf-8")
            return ImportResult("filter", t.stem, 1)
        raise ValueError("Это не файл фильтра или пакета Photo Editor AI")

    def export(self, f: Filter, dest: Path) -> None:
        if f.path and f.path.suffix == ".cube":
            shutil.copyfile(f.path, dest)
        else:
            dest.write_text(json.dumps({"format": FORMAT, "version": 1, **_entry_json(f.name, f.category, f.params)}, ensure_ascii=False, indent=1),
                            encoding="utf-8")

    def export_pack(self, pack: Pack, dest: Path) -> int:
        """Пакет одним файлом. Фильтры на основе LUT (.cube) в пакет не входят: путь к файлу на другом компьютере не сработает."""
        entries = [_entry_json(f.name, f.category, f.params) for f in pack.filters if not f.params.lut]
        self._write_pack(Path(dest), pack.name, pack.description, entries)
        return len(entries)

    def delete(self, f: Filter) -> None:
        """Удалить свой фильтр: отдельный файл или запись из файла пакета (пустой пакет удаляется целиком)."""
        if f.builtin or not f.path:
            return
        if f.path.name.endswith(".pack.json"):
            pk = self._read_pack(f.path)
            entries = [_entry_json(x.name, x.category, x.params) for x in pk.filters if x.name != f.name]
            if entries:
                self._write_pack(f.path, pk.name, pk.description, entries)
            else:
                f.path.unlink(missing_ok=True)
        else:
            f.path.unlink(missing_ok=True)

    def delete_pack(self, pack: Pack) -> None:
        if not pack.builtin and pack.path:
            pack.path.unlink(missing_ok=True)


def category_order(names) -> list[str]:
    """Типы в привычном порядке: сначала известные, потом остальные по алфавиту."""
    known = [c for c in CATEGORIES if c in names]
    return known + sorted(n for n in names if n not in CATEGORIES)


__all__ = ["Filter", "Pack", "ImportResult", "FilterStore", "blend", "BUILTIN", "BUILTIN_PACKS", "CATEGORIES", "MY_PACK", "BASE_TYPES", "category_order"]
