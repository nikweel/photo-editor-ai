"""Скачивает небольшой набор разнообразных фото с Wikimedia Commons для обучения оценки экспозиции по сцене.

Берутся только JPEG со свободными лицензиями (Public Domain, CC0, CC BY — без ShareAlike и NC). Рядом с кадрами пишется
attribution.csv (автор, лицензия, ссылка на страницу файла). Данные кладутся в data/train/commons/ и в репозиторий не входят.
Запрашиваются стандартные размеры миниатюр (960 px) и соблюдается пауза между запросами, как просят правила Wikimedia.

Запуск:  python scripts/train/fetch_commons.py [--per-category 120] [--pilot]
"""
import argparse
import csv
import json
import random
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "train" / "commons"
UA = "PhotoEditorAI-research/0.1 (https://github.com/nikweel/photo-editor-ai; nikweel@gmail.com)"
API = "https://commons.wikimedia.org/w/api.php"
# класс сцены -> категории Commons. Класс нужен, чтобы показывать пользователю, что распознано, и проверять качество по типам сцен
CLASSES = {
    "night": ["Night photography", "Featured night photography", "Night cityscapes", "Night sky", "Low light photography"],
    "dusk": ["Dusk", "Twilight", "Sunsets", "Sunrises"],
    "portrait": ["Portrait photographs", "Quality images of people"],
    "landscape": ["Forests", "Mountains", "Beaches"],
    "street": ["Street photography"],
    "closeup": ["Macro photographs", "Food", "Indoor", "Bokeh"],
    "backlit": ["Backlighting", "Silhouettes"],
}
OK_LICENSE = re.compile(r"^(CC0|Public domain|PD|CC[ -]BY[ -](\d\.\d|\d))", re.I)
BAD_LICENSE = re.compile(r"(SA|NC|ND)", re.I)


def call(**params):
    params.update(format="json", formatversion="2")
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)


def members(category: str, limit: int):
    """Файлы категории с данными о лицензии и ссылкой на миниатюру 960 px (не больше limit штук, до фильтрации)."""
    out, cont = [], {}
    while len(out) < limit:
        d = call(action="query", generator="categorymembers", gcmtitle="Category:" + category, gcmtype="file", gcmlimit=50, prop="imageinfo",
                 iiprop="url|size|mime|extmetadata", iiurlwidth=960, **cont)
        out += d.get("query", {}).get("pages", [])
        if "continue" not in d:
            break
        cont = d["continue"]
        time.sleep(0.4)
    return out


def usable(page: dict) -> dict | None:
    info = (page.get("imageinfo") or [{}])[0]
    meta = info.get("extmetadata", {})
    lic = (meta.get("LicenseShortName", {}).get("value") or "").strip()
    if info.get("mime") != "image/jpeg" or info.get("width", 0) < 1200 or not OK_LICENSE.match(lic) or BAD_LICENSE.search(lic):
        return None
    if not info.get("thumburl"):
        return None
    author = re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value") or "").strip()[:120]
    return {"title": page["title"], "license": lic, "author": author, "page": info.get("descriptionurl", ""), "thumb": info["thumburl"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-category", type=int, default=120, help="сколько кадров брать из каждой категории")
    ap.add_argument("--pool", type=int, default=400, help="сколько файлов категории просматривать до фильтра")
    ap.add_argument("--pilot", action="store_true", help="пробный прогон: по 3 кадра из категории")
    a = ap.parse_args()
    per = 3 if a.pilot else a.per_category
    pool = 100 if a.pilot else a.pool
    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / "attribution.csv"
    seen = {r["title"] for r in csv.DictReader(open(csv_path, encoding="utf-8"))} if csv_path.exists() else set()
    new_file = not csv_path.exists()
    rng = random.Random(7)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, ["file", "class", "category", "title", "license", "author", "page"])
        if new_file:
            w.writeheader()
        total = 0
        for cls, cats in CLASSES.items():
            for cat in cats:
                try:
                    cand = [u for p in members(cat, pool) if (u := usable(p)) and u["title"] not in seen]
                except Exception as e:
                    print(f"  {cat}: ошибка запроса ({e}), пропуск", flush=True)
                    continue
                rng.shuffle(cand)
                got = 0
                for u in cand:
                    if got >= per:
                        break
                    name = re.sub(r"[^0-9A-Za-z]+", "_", u["title"].removeprefix("File:"))[:70] + ".jpg"
                    dest = OUT / cls / name
                    dest.parent.mkdir(exist_ok=True)
                    try:
                        req = urllib.request.Request(u["thumb"], headers={"User-Agent": UA})
                        with urllib.request.urlopen(req, timeout=60) as r:
                            data = r.read()
                        if len(data) < 20_000:
                            continue
                        dest.write_bytes(data)
                    except Exception as e:
                        print(f"    пропуск {name}: {e}", flush=True)
                        time.sleep(2)
                        continue
                    w.writerow({"file": f"{cls}/{name}", "class": cls, "category": cat, "title": u["title"], "license": u["license"], "author": u["author"], "page": u["page"]})
                    f.flush()
                    seen.add(u["title"])
                    got += 1
                    total += 1
                    time.sleep(0.5)
                print(f"  {cls:9} {cat:34} +{got}  (подходящих лицензий среди просмотренных: {len(cand)})", flush=True)
    print("всего новых кадров:", total, "→", OUT)


if __name__ == "__main__":
    sys.exit(main())
