"""Сравнение «до | «после» с сайта | наш результат | разница ×4» для фильтров из presets_site.json.
Картинки сохраняются в data/reference/compare/. Запуск: python scripts/compare_filters.py"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent))
import fit_filters as F  # noqa: E402
from app.core import adjust  # noqa: E402
from app.core.adjust import EditParams  # noqa: E402

OUT = F.REF / "compare"


def main():
    data = json.loads(F.OUT.read_text(encoding="utf-8"))
    OUT.mkdir(exist_ok=True)
    for name, d in data.items():
        pid = F.PAIRS[name][0]
        b, a, m = F.load(pid, 480)
        ours = adjust.apply(b, EditParams.from_dict(d["params"]))
        diff = np.clip(np.abs(ours - a) * 4, 0, 1)
        diff[~m] = 0
        tiles = [b, a, ours, diff]
        sheet = Image.new("RGB", (480 * 4, b.shape[0]))
        for i, t in enumerate(tiles):
            sheet.paste(Image.fromarray((np.clip(t, 0, 1) * 255).astype(np.uint8)), (i * 480, 0))
        safe = "".join(ch if ch.isalnum() else "_" for ch in name)
        sheet.save(OUT / f"{safe}.png")
        q = d["quality"]["after"]
        print(f"{name}: ΔE среднее {q['deltaE_mean']:.2f}, p95 {q['deltaE_p95']:.2f} | тени {q['deltaE_shadows']:.2f} · средние {q['deltaE_mids']:.2f} · света {q['deltaE_highlights']:.2f}")


if __name__ == "__main__":
    main()
