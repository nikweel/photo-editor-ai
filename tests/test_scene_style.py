"""Признаки сцены, экспозиционная «голова» и обучение «Моего стиля» (без Qt)."""
from types import SimpleNamespace

import numpy as np
from PIL import Image

from app.ai import scene, style


def _img(level: float, seed: int = 0) -> np.ndarray:
    r = np.random.default_rng(seed)
    return np.clip(r.uniform(0.4, 1, (48, 64, 3)) * level, 0, 1).astype(np.float32)


def test_stats_shape_and_brightness_order():
    dark, bright = scene.luminance_stats(_img(0.1)), scene.luminance_stats(_img(0.9))
    assert dark.shape == bright.shape == (scene.STAT_DIM,)
    assert dark[4] < bright[4]  # медиана log-яркости


def test_shift_exposure_matches_ev_and_clips():
    img = _img(0.2)
    up = scene.shift_exposure(img, 1.0)
    assert up.mean() > img.mean()
    assert np.allclose(scene.shift_exposure(img, 0.0), img, atol=1e-4)
    assert scene.shift_exposure(_img(1.0), 3.0).max() <= 1.0


def test_embed_input_layout():
    assert scene.embed_input(_img(0.5)).shape == (1, 3, 224, 224)


def test_style_learns_habit_and_roundtrips(tmp_path):
    rng = np.random.default_rng(0)
    X, Y = [], []
    for _ in range(40):
        b = rng.uniform(0.1, 0.8)
        X.append(style.style_features(_img(b, int(rng.integers(1e6)))))
        Y.append(style.edit_vector({"exposure": (0.4 - b) * 2, "shadows": 0.3}))
    m = style.StyleModel.fit(np.array(X), np.array(Y))
    assert m.gain > 0.5
    dark = m.predict(style.style_features(_img(0.12)))
    bright = m.predict(style.style_features(_img(0.75)))
    assert dark["exposure"] > 0.3 > bright["exposure"] and abs(dark["shadows"] - 0.3) < 0.1
    f = tmp_path / "style.json"
    style.save(m, f)
    m2 = style.load(f)
    assert m2 and abs(m2.predict(X[0])["exposure"] - m.predict(X[0])["exposure"]) < 1e-5
    assert style.load(tmp_path / "нет.json") is None


def test_style_train_from_entries(tmp_path):
    entries = []
    for i in range(15):
        p = tmp_path / f"фото{i}.jpg"
        Image.fromarray((_img(0.2 + 0.04 * i, i) * 255).astype(np.uint8)).save(p)
        entries.append(SimpleNamespace(path=str(p), params={"exposure": 1.05 - 0.1 * i}))
    entries.append(SimpleNamespace(path=str(tmp_path / "фото0.jpg"), params={}))  # без правок — не учитывается
    m = style.train(entries)
    assert m is not None and m.n == 15
    assert style.train(entries[:5]) is None  # мало правок


def test_scene_engine_end_to_end():
    """Модель сцены (если файлы лежат в models/) отвечает по контракту; иначе тест пропускается."""
    import pytest

    from app.ai.auto import suggest
    from app.ai.registry import Engine, is_available

    if not is_available("scene_exposure"):
        pytest.skip("нет models/exposure_scene.onnx и dinov2_small.onnx")
    eng = Engine("scene_exposure")
    dark = suggest(eng, _img(0.04), "exposure")
    bright = suggest(eng, np.clip(_img(1.0) * 1.0 + 0.3, 0, 1).astype(np.float32), "exposure")
    assert dark["exposure"] > bright["exposure"] and "verdict" in dark and dark["scene"] in scene.CLASSES


def test_parts_make_model_unavailable_until_all_files_present(tmp_path, monkeypatch):
    from app.ai import registry

    monkeypatch.setattr(registry, "MODELS_DIR", tmp_path)
    (tmp_path / "exposure_scene.onnx").write_bytes(b"x")
    assert not registry.is_available("scene_exposure")  # нет эмбеддера
    (tmp_path / "dinov2_small.onnx").write_bytes(b"x")
    assert registry.is_available("scene_exposure") and registry.total_size("scene_exposure") == 0
