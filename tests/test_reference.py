"""Сверка фильтров с эталонными кадрами «после» (data/reference/, в репозиторий не входят — тест пропускается без них)."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
REF = ROOT / "data" / "reference"
SITE = ROOT / "app" / "services" / "presets_site.json"
pytestmark = pytest.mark.skipif(not (REF / "pairs.json").exists() or not SITE.exists(), reason="нет эталонных кадров")


def test_site_filters_match_reference_images():
    import fit_filters as F
    from app.core import adjust
    from app.services.filters import BUILTIN

    data = json.loads(SITE.read_text(encoding="utf-8"))
    assert data, "presets_site.json пуст"
    names = {f.name: f for f in BUILTIN}
    for name, d in data.items():
        assert name in names, f"фильтр {name} не подключён в приложении"
        before, after, mask = F.load(F.PAIRS[name][0], 640)
        out = adjust.apply(before, names[name].params)
        de = np.linalg.norm(F.to_lab(out) - F.to_lab(after), axis=-1)[mask]
        raw = np.linalg.norm(F.to_lab(before) - F.to_lab(after), axis=-1)[mask]
        recorded = d["quality"]["after"]["deltaE_mean"]
        assert de.mean() < max(recorded * 1.5, 3.5), (name, de.mean(), recorded)  # близко к записанному при подгонке
        assert de.mean() < raw.mean() * 0.4, name                                   # фильтр сильно приближает «до» к «после»
