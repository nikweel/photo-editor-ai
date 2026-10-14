import numpy as np

from app.ai.exposure import heuristic_ev
from app.core import adjust
from app.core.adjust import EditParams


def flat(v):
    return np.full((32, 32, 3), v, np.float32)


def test_dark_image_gets_positive_ev():
    assert heuristic_ev(flat(0.1)) > 0.5


def test_bright_image_gets_negative_ev():
    assert heuristic_ev(flat(0.9)) < 0


def test_identity_returns_same():
    a = flat(0.4)
    assert adjust.apply(a, EditParams()) is a


def test_exposure_brightens_and_stays_in_range():
    out = adjust.apply(flat(0.3), EditParams(exposure=1.5))
    assert out.mean() > 0.3 and out.max() <= 1.0


def test_batch_creates_files(tmp_path):
    from PIL import Image
    from app.ai.registry import Engine
    from app.services.batch import BatchOptions, collect_files, run_batch

    Image.new("RGB", (64, 48), (30, 30, 30)).save(tmp_path / "a.jpg")
    (tmp_path / "bad.jpg").write_bytes(b"not an image")
    files = collect_files([tmp_path])
    ok, errs = run_batch(files, Engine("heuristic"), BatchOptions(tmp_path / "out"))
    assert ok == 1 and len(errs) == 1 and (tmp_path / "out" / "a_edit.jpg").exists()


def test_library_import_copy_and_persist(tmp_path):
    from PIL import Image
    from app.services.library import Library, import_files

    src = tmp_path / "s.jpg"
    Image.new("RGB", (40, 30), (90, 90, 90)).save(src)
    out = import_files([src], tmp_path / "dest", by_date=True)
    assert len(out) == 1 and out[0].exists() and out[0].parent.parent == tmp_path / "dest"
    assert import_files([src], tmp_path / "dest") == out  # повторный импорт не плодит копии
    lib = Library(tmp_path / "lib.json")
    assert lib.add(out) == out and lib.add(out) == []
    lib.get(out[0]).params = {"exposure": 1.0}
    lib.save()
    assert Library(tmp_path / "lib.json").get(out[0]).params["exposure"] == 1.0


def test_manual_params_and_curve():
    import numpy as np
    from app.core.adjust import EditParams, apply, curve_lut

    a = np.full((8, 8, 3), 0.5, np.float32)
    assert apply(a, EditParams(shadows=1.0)).mean() > 0.5
    assert apply(a, EditParams(saturation=-1.0)).std() < 1e-4
    p = EditParams()
    p.curves["rgb"] = [[0.0, 0.0], [0.5, 0.7], [1.0, 1.0]]
    assert apply(a, p).mean() > 0.68
    lut = curve_lut(p.curves["rgb"])
    assert np.all(np.diff(lut) >= -1e-6)  # монотонность
    assert EditParams.from_dict(p.to_dict()).curves["rgb"] == p.curves["rgb"]
    assert EditParams().is_identity()


def _cube(path, n=2, gain=1.0):
    rows = [f"{min(r * gain, 1)} {min(g * gain, 1)} {min(b * gain, 1)}" for b in range(n) for g in range(n) for r in range(n)]
    path.write_text(f"TITLE \"t\"\nLUT_3D_SIZE {n}\n" + "\n".join(rows).replace("1 ", "1.0 "), encoding="utf-8")


def test_cube_identity_and_bad(tmp_path):
    import numpy as np
    from app.core.lut import LutError, apply_lut

    c = tmp_path / "id.cube"
    _cube(c)
    a = np.random.rand(5, 6, 3).astype(np.float32)
    assert np.allclose(apply_lut(a, str(c)), a, atol=1e-5)
    bad = tmp_path / "bad.cube"
    bad.write_text("LUT_3D_SIZE 3\n0 0 0\n")
    try:
        apply_lut(a, str(bad))
        assert False
    except LutError:
        pass


def test_filter_store(tmp_path):
    from app.core.adjust import EditParams
    from app.services.filters import BUILTIN, FilterStore, blend

    st = FilterStore(tmp_path / "p")
    f = st.save_user("Мой/стиль", EditParams(contrast=0.3))
    assert [x.name for x in st.user_filters()] == [f.name]
    st.export(f, tmp_path / "out.json")
    g = st.import_file(tmp_path / "out.json")
    assert g.kind == "filter" and len(st.user_filters()) == 2
    assert max(x.params.contrast for x in st.user_filters()) == 0.3
    c = tmp_path / "x.cube"
    _cube(c)
    r = st.import_file(c)
    assert r.kind == "lut" and any(x.params.lut for x in st.user_filters())
    (tmp_path / "evil.json").write_text('{"hello": 1}')
    try:
        st.import_file(tmp_path / "evil.json")
        assert False
    except ValueError:
        pass
    assert blend(BUILTIN[0].params, 0.5).contrast == BUILTIN[0].params.contrast * 0.5



def _scene(r, g, b, n=64):
    import numpy as np
    base = np.linspace(0.0, 1.0, n * n, dtype=np.float32).reshape(n, n)
    return np.clip(np.stack([base * r, base * g, base * b], -1), 0, 1)


def test_suggest_dark_bright_and_cast():
    from app.ai.auto import suggest
    from app.ai.registry import Engine

    e = Engine("heuristic")
    dark = _scene(0.2, 0.2, 0.2)
    assert suggest(e, dark, "exposure")["exposure"] > 0.5
    assert "temperature" not in suggest(e, dark, "exposure")
    bright = _scene(1, 1, 1) * 0.3 + 0.7  # светлый кадр с белыми — осветлять нельзя
    assert suggest(e, bright, "full")["exposure"] <= 0
    blue = _scene(0.6, 0.7, 1.0)
    assert suggest(e, blue, "full")["temperature"] > 0.02  # синий оттенок -> потеплее


def test_custom_model_add_detect_remove(tmp_path, monkeypatch):
    import numpy as np
    import onnx
    from onnx import TensorProto, helper
    import app.ai.registry as R

    monkeypatch.setattr(R, "CUSTOM_FILE", tmp_path / "c.json")
    monkeypatch.setattr(R, "CUSTOM_DIR", tmp_path / "custom")
    monkeypatch.setattr(R, "MODELS_DIR", tmp_path)

    def make(path, out_shape, op):
        x = helper.make_tensor_value_info("x", TensorProto.FLOAT, [1, 3, "h", "w"])
        y = helper.make_tensor_value_info("y", TensorProto.FLOAT, out_shape)
        node = helper.make_node(*op)
        m = helper.make_model(helper.make_graph([node], "g", [x], [y]), opset_imports=[helper.make_opsetid("", 13)])
        m.ir_version = 9  # новее, чем понимает onnxruntime из проекта
        onnx.save(m, path)

    make(tmp_path / "enh.onnx", [1, 3, "h", "w"], ("Identity", ["x"], ["y"]))
    spec = R.add_custom(tmp_path / "enh.onnx", "моя")
    assert spec.kind == "enhancer" and R.models()[spec.id].file.startswith("custom/") and R.is_available(spec.id)
    out = R.Engine(spec.id).enhance(np.full((20, 30, 3), 0.4, np.float32))
    assert out.shape == (20, 30, 3)
    (tmp_path / "bad.onnx").write_bytes(b"nope")
    try:
        R.add_custom(tmp_path / "bad.onnx", "bad")
        assert False
    except ValueError:
        pass
    R.remove_custom(spec.id)
    assert spec.id not in R.models()


def test_geometry_rotate_flip_crop_straighten():
    import numpy as np
    from app.core.adjust import EditParams, apply_geometry, render

    a = np.random.default_rng(0).random((40, 60, 3)).astype(np.float32)
    assert apply_geometry(a, EditParams(rotate90=1)).shape == (60, 40, 3)
    assert np.allclose(apply_geometry(a, EditParams(rotate90=1))[:, 0], a[-1, :])  # по часовой: нижняя строка становится левым столбцом
    assert np.allclose(apply_geometry(a, EditParams(flip_h=1)), a[:, ::-1])
    assert apply_geometry(a, EditParams(crop=[0.25, 0.0, 0.75, 0.5])).shape == (20, 30, 3)
    assert apply_geometry(a, EditParams(crop=[0.25, 0.0, 0.75, 0.5]), crop=False).shape == a.shape
    flat = np.full((100, 150, 3), 0.7, np.float32)
    st = apply_geometry(flat, EditParams(straighten=10))
    assert st.shape[0] < 100 and st.min() > 0.65  # пустые углы обрезаны, чёрных заливок нет
    assert render(a, EditParams(rotate90=2, exposure=0.5)).shape == a.shape


def test_detail_effects():
    import numpy as np
    from app.core.adjust import EditParams, apply

    rng = np.random.default_rng(1)
    a = np.clip(0.5 + rng.normal(0, 0.05, (80, 120, 3)), 0, 1).astype(np.float32)
    assert apply(a, EditParams(sharpen=1.0)).std() > a.std()
    v = apply(np.full((60, 90, 3), 0.6, np.float32), EditParams(vignette=-1.0))
    assert v[30, 45].mean() > v[0, 0].mean() + 0.2  # края темнее центра
    g = apply(np.full((60, 90, 3), 0.5, np.float32), EditParams(grain=1.0))
    assert g.std() > 0.01
    assert np.array_equal(apply(a, EditParams(grain=1.0)), apply(a, EditParams(grain=1.0)))  # зерно воспроизводимо
    nc = np.dstack([np.where(rng.random((50, 50)) > 0.5, 0.8, 0.2), np.full((50, 50), 0.5), np.full((50, 50), 0.5)]).astype(np.float32)
    assert apply(nc, EditParams(noise_color=1.0))[..., 0].std() < nc[..., 0].std()


def test_params_roundtrip_new_fields():
    from app.core.adjust import EditParams

    p = EditParams(rotate90=3, flip_v=1, straighten=-4.5, crop=[0.1, 0.2, 0.9, 0.8], sharpen=0.4, vignette=-0.3)
    q = EditParams.from_dict(p.to_dict())
    assert q.to_dict() == p.to_dict() and q.has_geometry() and not q.is_identity()
    bad = EditParams.from_dict({"crop": [0.5, 0.5, 0.51, 0.51], "rotate90": 7})
    assert bad.crop == [0.0, 0.0, 1.0, 1.0] and bad.rotate90 == 3


def test_library_rating_remove_and_export(tmp_path):
    from PIL import Image
    from app.core.adjust import EditParams
    from app.core.imageio import to_array
    from app.services.export import ExportOptions, export_image
    from app.services.library import Library

    src = tmp_path / "s.jpg"
    Image.new("RGB", (80, 40), (90, 100, 110)).save(src)
    lib = Library(tmp_path / "l.json")
    lib.add([src])
    lib.get(src).rating = 3
    lib.save()
    assert Library(tmp_path / "l.json").get(src).rating == 3
    lib.remove(src)
    assert lib.get(src) is None and src.exists()  # файл остаётся
    out = export_image(src, to_array(Image.open(src)), EditParams(rotate90=1, crop=[0, 0, 1, 0.5]), tmp_path / "o.png", ExportOptions("png"))
    assert Image.open(out).size == (40, 40)  # поворот 80x40 -> 40x80, затем верхняя половина
    out = export_image(src, to_array(Image.open(src)), EditParams(), tmp_path / "o.jpg", ExportOptions("jpg", 90, 40, True))
    assert max(Image.open(out).size) == 40


def test_batch_with_geometry_and_format(tmp_path):
    from PIL import Image
    from app.ai.registry import Engine
    from app.core.adjust import EditParams
    from app.services.batch import BatchOptions, run_batch

    Image.new("RGB", (60, 30), (40, 40, 40)).save(tmp_path / "a.jpg")
    o = BatchOptions(tmp_path / "out", "webp", 80, 0, True, 1.0, "exposure", 0.0, EditParams(rotate90=1))
    ok, errs = run_batch([tmp_path / "a.jpg"], Engine("heuristic"), o)
    assert ok == 1 and not errs and Image.open(tmp_path / "out" / "a_edit.webp").size == (30, 60)


def test_moody_filters_match_style():
    """Dark & Moody по рецепту: темнее, света приглушены, тени проявлены (не чёрные пятна) и чуть матовые,
    цвет приглушён — зелёный сильнее всего, кожа остаётся тёплой, виньетка по краям."""
    import numpy as np
    from app.core import adjust
    from app.services.filters import BUILTIN, blend

    x = np.linspace(0.08, 0.92, 120, dtype=np.float32)
    grad = np.dstack([np.tile(x * m, (80, 1)) for m in (1.0, 0.85, 0.7)])
    lum = lambda a: a @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    moody = [f for f in BUILTIN if "Moody" in f.name and f.pack == "Dark & Moody"]  # подобранные по образцам проверяются отдельно
    assert len(moody) == 5
    for f in moody:
        out = adjust.render(grad, f.params)
        l = lum(out)
        assert l.mean() < lum(grad).mean() - 0.05, f.name                  # общий кадр темнее
        assert np.percentile(l, 95) < np.percentile(lum(grad), 95) - 0.05, f.name  # света приглушены
        assert np.percentile(l, 1) > 0.005, f.name                         # чёрные не обрезаны: матовая дымка в тенях
        hs = lambda c: float((c.max() - c.min()) / c.max())
        for name, rgb in (("зелень", [0.25, 0.6, 0.25]), ("небо", [0.3, 0.5, 0.85]), ("жёлтый", [0.85, 0.8, 0.3])):
            patch_in = np.tile(np.array(rgb, np.float32), (8, 8, 1))
            patch_out = adjust.apply(patch_in, f.params)[0, 0]
            if f.name != "Moody · Ч/Б":
                assert hs(patch_out) < hs(patch_in) * 0.9, (f.name, name)  # приглушённые зелёный, синий и жёлтый
        half = adjust.render(grad, blend(f.params, 0.5))
        assert l.mean() < lum(half).mean() < lum(grad).mean(), f.name      # сила работает плавно
    dm = next(f for f in moody if f.name == "Dark & Moody")
    sat1 = lambda c: float(c.max() - c.min())
    patch = lambda rgb: np.tile(np.array(rgb, np.float32), (8, 8, 1))
    green, skin = patch([0.25, 0.6, 0.25]), patch([0.85, 0.6, 0.45])
    g, k = adjust.apply(green, dm.params), adjust.apply(skin, dm.params)
    assert sat1(g[0, 0]) < sat1(green[0, 0]) * 0.6                         # зелёный сильно приглушён
    assert sat1(k[0, 0]) > sat1(skin[0, 0]) * 0.45 and k[0, 0, 0] > k[0, 0, 2]  # кожа теплее, не обесцвечена
    v = adjust.render(np.full((60, 90, 3), 0.6, np.float32), dm.params)
    assert v[30, 45].mean() > v[0, 0].mean() + 0.02                        # виньетка: края темнее центра


def test_hsl_per_color():
    import numpy as np
    from app.core.adjust import EditParams, apply

    def patch(rgb):
        return np.tile(np.array(rgb, np.float32), (12, 12, 1))

    green, orange, gray = patch([0.2, 0.7, 0.25]), patch([0.9, 0.55, 0.2]), patch([0.5, 0.5, 0.5])
    sat = lambda a: float((a.max(-1) - a.min(-1)).mean())
    p = EditParams()
    p.hsl["green"] = [0.0, -1.0, 0.0]  # полностью обесцветить зелёный
    assert sat(apply(green, p)) < 0.05 and abs(sat(apply(orange, p)) - sat(orange)) < 0.03 and np.allclose(apply(gray, p), gray, atol=1e-4)
    q = EditParams()
    q.hsl["orange"] = [0.0, 0.0, 1.0]  # осветлить оранжевый (кожа)
    assert apply(orange, q).max() > orange.max() + 0.03 and np.allclose(apply(green, q), green, atol=0.02)
    h = EditParams()
    h.hsl["red"] = [1.0, 0.0, 0.0]  # красный -> в сторону оранжевого: растёт зелёная составляющая
    red = patch([0.9, 0.1, 0.1])
    assert apply(red, h)[0, 0, 1] > red[0, 0, 1] + 0.1
    r = EditParams.from_dict(p.to_dict())
    assert r.hsl["green"] == [0.0, -1.0, 0.0] and not r.is_identity() and EditParams().is_identity()


def test_texture_and_dehaze():
    import numpy as np
    from app.core.adjust import EditParams, apply

    rng = np.random.default_rng(3)
    a = np.clip(0.5 + rng.normal(0, 0.04, (80, 120, 3)), 0, 1).astype(np.float32)
    assert apply(a, EditParams(texture=1.0)).std() > a.std()
    haze = np.clip(0.55 + 0.25 * np.tile(np.linspace(0, 1, 120, dtype=np.float32), (80, 1))[..., None] * np.ones(3, np.float32), 0, 1)
    assert apply(haze, EditParams(dehaze=1.0)).min() < haze.min() - 0.03  # дымка убрана: тёмное темнее
    assert apply(haze, EditParams(dehaze=-1.0)).min() > haze.min()         # добавлена: тёмное светлее




def test_channel_mixer():
    import numpy as np
    from app.core.adjust import EditParams, apply
    from app.services.filters import Filter, blend

    a = np.dstack([np.full((6, 6), v, np.float32) for v in (0.8, 0.4, 0.2)])
    assert EditParams().mix_is_identity() and EditParams().is_identity()
    p = EditParams(mix=[0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0])  # поменять местами R и G
    assert np.allclose(apply(a, p)[0, 0], [0.4, 0.8, 0.2], atol=1e-5) and not p.is_identity()
    q = EditParams.from_dict(p.to_dict())
    assert q.mix == p.mix
    half = blend(p, 0.5)  # полсилы: ровно посередине между исходным и результатом
    assert np.allclose(half.mix, [0.5, 0.5, 0, 0.5, 0.5, 0, 0, 0, 1])
    assert EditParams.from_dict({"mix": [1, 2, 3]}).mix_is_identity()  # мусор вместо матрицы игнорируется


SITE_NAMES = ("Moody · Тёплый беж", "Кино · Мягкий свет", "Кино · Тёмный янтарь", "Улица · Золотистый тон", "Улица · Светлый воздух", "Плёнка · Изумрудная трава")


def test_site_filters_are_sane():
    """Фильтры, подобранные по парам «до/после»: подключены, параметры корректны, результат конечен и в диапазоне.
    Точность относительно эталонов проверяет tests/test_reference.py."""
    import numpy as np
    from app.core import adjust
    from app.services.filters import BUILTIN, blend

    by = {f.name: f for f in BUILTIN}
    x = np.linspace(0, 1, 64, dtype=np.float32)
    ramp = np.dstack([np.tile(x * m, (16, 1)) for m in (1.0, 0.8, 0.6)])
    for n in SITE_NAMES:
        assert n in by, n
        p = by[n].params
        for ch in "rgb":
            ys = [q[1] for q in p.curves[ch]]
            assert all(b >= a for a, b in zip(ys, ys[1:])) and 0 <= min(ys) and max(ys) <= 1, (n, ch)
        out = adjust.render(ramp, p)
        assert np.isfinite(out).all() and out.min() >= 0 and out.max() <= 1, n
        black = adjust.render(np.zeros((8, 8, 3), np.float32), p)
        assert black.max() < 0.12, n                                    # чёрный остаётся тёмным
        half = adjust.render(ramp, blend(p, 0.5))
        assert np.abs(half - ramp).mean() < np.abs(out - ramp).mean() + 1e-6, n  # половинная сила ближе к исходнику


def test_filter_packs_roundtrip(tmp_path):
    """Пакеты: сохранение в свой пакет, экспорт и импорт целого пакета, удаление, защита от встроенных и от чужих LUT-путей."""
    import json
    from app.core.adjust import EditParams
    from app.services.filters import BUILTIN_PACKS, FilterStore, MY_PACK, PACK_FORMAT

    st = FilterStore(tmp_path / "p")
    a = st.save_user("Один", EditParams(contrast=0.2), "Свадьба", "Портрет")
    b = st.save_user("Два", EditParams(saturation=0.3), "Свадьба", "Улица")
    c = st.save_user("Один", EditParams(exposure=0.5), "Свадьба", "Портрет")  # то же имя в пакете -> «Один 2»
    assert (a.pack, b.pack, c.name) == ("Свадьба", "Свадьба", "Один 2")
    assert st.pack_names() == [MY_PACK, "Свадьба"]
    pk = next(x for x in st.user_packs() if x.name == "Свадьба")
    assert [f.name for f in pk.filters] == ["Один", "Два", "Один 2"] and {f.category for f in pk.filters} == {"Портрет", "Улица"}
    try:  # встроенные пакеты менять нельзя
        st.save_user("Х", EditParams(), BUILTIN_PACKS[0].name)
        assert False
    except ValueError:
        pass
    out = tmp_path / "wed.pack.json"
    assert st.export_pack(pk, out) == 3
    other = FilterStore(tmp_path / "q")  # «другой компьютер»
    res = other.import_file(out)
    assert (res.kind, res.name, res.count) == ("pack", "Свадьба", 3)
    assert other.import_file(out).name == "Свадьба (2)"  # повторный импорт не затирает пакет
    assert len(other.user_packs()) == 2
    # чужой файл: путь к LUT не принимается, мусорные записи пропускаются, лишнее обрезается
    evil = {"format": PACK_FORMAT, "name": "Чужой", "filters": [{"name": "ok", "params": {"contrast": 0.1, "lut": "/etc/passwd"}},
                                                                {"name": 5, "params": "мусор"}, {"params": {}}]}
    (tmp_path / "evil.pack.json").write_text(json.dumps(evil), encoding="utf-8")
    other.import_file(tmp_path / "evil.pack.json")
    ev = next(x for x in other.user_packs() if x.name == "Чужой")
    assert ev.filters and all(not f.params.lut for f in ev.filters)
    (tmp_path / "empty.pack.json").write_text(json.dumps({"format": PACK_FORMAT, "name": "Пусто", "filters": []}))
    try:
        other.import_file(tmp_path / "empty.pack.json")
        assert False
    except ValueError:
        pass
    # удаление: запись из пакета, последний фильтр убирает файл; пакет целиком
    for f in [x for x in other.user_packs() if x.name == "Свадьба"][0].filters:
        other.delete(f)
    assert not any(x.name == "Свадьба" for x in other.user_packs())
    other.delete_pack(next(x for x in other.user_packs() if x.name == "Чужой"))
    assert not any(x.name == "Чужой" for x in other.user_packs())


def test_builtin_packs_catalog():
    """Встроенные пакеты: достаточно фильтров по жанрам, имена уникальны, типы заполнены, каждый фильтр меняет картинку и не ломает её."""
    import numpy as np
    from app.core import adjust
    from app.services.filters import BUILTIN, BUILTIN_PACKS, CATEGORIES

    names = [f.name for f in BUILTIN]
    assert len(names) == len(set(names)) and len(names) >= 55
    pack_names = {p.name for p in BUILTIN_PACKS}
    assert {"Портрет", "Пейзаж", "Чёрно-белые", "Еда", "Улица и город", "Плёнка и винтаж", "Dark & Moody", "Базовые"} <= pack_names
    assert all(f.category in CATEGORIES for f in BUILTIN)  # у каждого фильтра известный тип
    assert {f.category for f in BUILTIN} >= {"Портрет", "Пейзаж", "Ч/Б", "Еда", "Улица", "Плёнка", "Кино"}
    rng = np.random.default_rng(5)
    img = np.clip(0.45 + 0.25 * rng.standard_normal((48, 64, 3)), 0, 1).astype(np.float32)
    for f in BUILTIN:
        out = adjust.render(img, f.params)
        assert np.isfinite(out).all() and 0 <= out.min() and out.max() <= 1, f.name
        assert np.abs(out - img).mean() > 0.005, f.name  # фильтр заметно что-то делает
    bw = [f for f in BUILTIN if f.pack == "Чёрно-белые" and "Сепия" not in f.name and "Холодный" not in f.name]
    for f in bw:  # чистое чёрно-белое: каналы равны
        o = adjust.apply(img, f.params)
        assert np.abs(o[..., 0] - o[..., 1]).max() < 0.02, f.name



def test_model_download_verified(tmp_path):
    """Загрузка модели: принимается только файл с верными размером и SHA-256; чужие адреса запрещены; мусор не остаётся на диске."""
    import hashlib
    from app.ai.registry import BUILTIN_MODELS, fetch_verified

    src = tmp_path / "m.onnx"
    src.write_bytes(b"model-bytes" * 100)
    good = hashlib.sha256(src.read_bytes()).hexdigest()
    dest = tmp_path / "out" / "m.onnx"
    assert fetch_verified(src.as_uri(), dest, src.stat().st_size, good, lambda f, m: None).read_bytes() == src.read_bytes()
    for bad_size, bad_hash in ((1, good), (src.stat().st_size, "0" * 64)):
        bad = tmp_path / "out" / "bad.onnx"
        try:
            fetch_verified(src.as_uri(), bad, bad_size, bad_hash)
            assert False
        except ValueError:
            pass
        assert not bad.exists() and not bad.with_suffix(".onnx.part").exists()
    try:
        fetch_verified("http://example.com/x.onnx", tmp_path / "y.onnx", 0, "")
        assert False
    except ValueError:
        pass
    for m in BUILTIN_MODELS.values():  # у встроенных моделей из релиза заданы адрес с github.com, размер и контрольная сумма
        if m.url:
            assert m.url.startswith("https://github.com/") and m.size_bytes > 0 and len(m.sha256) == 64


def test_gpu_failure_falls_back_to_cpu(tmp_path, monkeypatch):
    """Видеокарта «есть» в списке провайдеров, но сессия на ней не создаётся или падает в работе (так ведёт себя DirectML на машине
    без подходящего устройства): ИИ обязан тихо перейти на процессор."""
    import numpy as np
    import onnx
    import onnxruntime as ort
    from onnx import TensorProto, helper
    import app.ai.registry as R

    x = helper.make_tensor_value_info("x", TensorProto.FLOAT, [1, 3, "h", "w"])
    y = helper.make_tensor_value_info("y", TensorProto.FLOAT, [1, 3, "h", "w"])
    m = helper.make_model(helper.make_graph([helper.make_node("Identity", ["x"], ["y"])], "g", [x], [y]), opset_imports=[helper.make_opsetid("", 13)])
    m.ir_version = 9
    onnx.save(m, tmp_path / "id.onnx")
    monkeypatch.setattr(R, "MODELS_DIR", tmp_path)
    monkeypatch.setattr(R, "BUILTIN_MODELS", {**R.BUILTIN_MODELS, "gpu_test": R.ModelSpec("gpu_test", "t", "enhancer", "id.onnx")})
    real, calls = ort.InferenceSession, []
    monkeypatch.setattr(ort, "get_available_providers", lambda: ["DmlExecutionProvider", "CPUExecutionProvider"])
    img = np.full((16, 24, 3), 0.4, np.float32)

    def broken_init(path, providers=None, **kw):  # DirectML не может создать сессию
        calls.append(tuple(providers))
        if "DmlExecutionProvider" in providers:
            raise RuntimeError("No devices detected that match the filter criteria")
        return real(path, providers=providers, **kw)

    monkeypatch.setattr(ort, "InferenceSession", broken_init)
    out = R.Engine("gpu_test").enhance(img)
    assert out.shape == img.shape and ("DmlExecutionProvider", "CPUExecutionProvider") in calls and ("CPUExecutionProvider",) in calls

    class BrokenRun:  # сессия создалась, но расчёт на GPU падает
        def __init__(self, inner): self.inner = inner
        def run(self, *a, **k): raise RuntimeError("DML failed")
        def get_inputs(self): return self.inner.get_inputs()

    monkeypatch.setattr(ort, "InferenceSession", lambda path, providers=None, **kw: real(path, providers=providers, **kw))
    e = R.Engine("gpu_test")
    e.session = BrokenRun(e.session)
    assert e.enhance(img).shape == img.shape and e._cpu  # после сбоя работает на процессоре


def test_model_in_non_ascii_path(tmp_path, monkeypatch):
    """Путь к модели с кириллицей (русское имя профиля на Windows): модель грузится из байтов, а не по пути."""
    import numpy as np
    import onnx
    from onnx import TensorProto, helper
    import app.ai.registry as R

    folder = tmp_path / "Николай" / "модели"
    folder.mkdir(parents=True)
    x = helper.make_tensor_value_info("x", TensorProto.FLOAT, [1, 3, "h", "w"])
    y = helper.make_tensor_value_info("y", TensorProto.FLOAT, [1, 3, "h", "w"])
    m = helper.make_model(helper.make_graph([helper.make_node("Identity", ["x"], ["y"])], "g", [x], [y]), opset_imports=[helper.make_opsetid("", 13)])
    m.ir_version = 9
    onnx.save(m, folder / "моя_модель.onnx")
    assert R.inspect_onnx(folder / "моя_модель.onnx")[0] == "enhancer"
    monkeypatch.setattr(R, "MODELS_DIR", folder)
    monkeypatch.setattr(R, "BUILTIN_MODELS", {**R.BUILTIN_MODELS, "ru_path": R.ModelSpec("ru_path", "t", "enhancer", "моя_модель.onnx")})
    assert R.Engine("ru_path").enhance(np.full((16, 24, 3), 0.5, np.float32)).shape == (16, 24, 3)


def test_banded_pointwise_is_identical_to_whole(monkeypatch):
    """Расчёт полосами в потоках даёт тот же результат бит в бит, что и расчёт целиком (пиксели друг от друга не зависят)."""
    import numpy as np
    from app.core import adjust
    from app.services.filters import BUILTIN, blend

    img = np.random.default_rng(2).random((301, 257, 3)).astype(np.float32)  # размеры не кратны числу полос
    for f in (x for x in BUILTIN if x.name in ("Dark & Moody", "Кино · Тёмный янтарь", "Контрастный Ч/Б (красный фильтр)", "Яркий")):
        p = blend(f.params, 0.7)
        tabs = adjust._tables(p)
        monkeypatch.setattr(adjust, "_bands", lambda px: 1)
        whole = adjust._run_pointwise(img, p, tabs)
        monkeypatch.setattr(adjust, "_bands", lambda px: 37)
        banded = adjust._run_pointwise(img, p, tabs)
        assert np.array_equal(whole, banded), f.name
        assert np.array_equal(adjust.apply(img, p), adjust._details(banded, p)), f.name


def test_open_preview_draft_and_orientation(tmp_path, monkeypatch):
    """Быстрый предпросмотр: JPEG декодируется уменьшенным, но не меньше запрошенного; размер оригинала и поворот по EXIF сохранены."""
    import numpy as np
    from PIL import Image
    from app.core.imageio import open_preview
    import app.services.library as L
    from app.services.library import thumb_for

    monkeypatch.setattr(L, "THUMB_DIR", tmp_path / "thumbs")  # кэш миниатюр — во временную папку, не в данные пользователя
    big = Image.fromarray((np.random.default_rng(0).random((900, 1600, 3)) * 255).astype(np.uint8))
    p = tmp_path / "a.jpg"
    big.save(p, quality=90)
    im, full = open_preview(p, 400)
    assert full == (1600, 900) and max(im.size) >= 400 and max(im.size) < 1600  # уменьшено декодером, но не ниже запрошенного
    im, full = open_preview(p, 5000)
    assert im.size == (1600, 900)  # больше оригинала не раздуваем
    ex = big.getexif()
    ex[274] = 6  # снимок снят «на боку»: хранится 1600x900, показывать нужно 900x1600
    q = tmp_path / "rot.jpg"
    big.save(q, exif=ex.tobytes())
    im, full = open_preview(q, 5000)
    assert full == (900, 1600) and im.size == (900, 1600)
    png = tmp_path / "b.png"
    big.save(png)
    assert open_preview(png, 200)[1] == (1600, 900)
    t = thumb_for(p)
    assert t is not None and max(Image.open(t).size) <= 192
