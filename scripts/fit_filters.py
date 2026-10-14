"""Подгонка фильтров по парам «до/после» (свои кадры лежат в data/reference/, см. _load_pairs; в репозиторий не входят).

Подбираются все параметры движка, чтобы результат совпал с «после» по цветовой разнице ΔE (Lab):
кривые по каналам, насыщенность, красочность, HSL по восьми цветам, виньетка, чёткость, текстура, резкость, дымка, тени/света/белые/чёрные.
Результат пишется в app/services/presets_site.json.

Запуск:  uv run --group fit python scripts/fit_filters.py [имя фильтра ...]   (без аргументов — все)
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.core import adjust  # noqa: E402
from app.core.adjust import HSL_COLORS, IDENTITY_MIX, EditParams  # noqa: E402

REF = ROOT / "data" / "reference"
OUT = ROOT / "app" / "services" / "presets_site.json"
def _load_pairs() -> dict:
    """Пары «до/после» для подгонки: data/reference/pairs.json = {"Имя фильтра": {"id": "<id>", "source": "..."}}.
    Кадры лежат рядом: <id>.jpg («до») и <id>after.jpg («после»), одного размера. Папка data/ в репозиторий не входит."""
    f = REF / "pairs.json"
    return {n: (v["id"], v.get("source", "")) for n, v in json.loads(f.read_text(encoding="utf-8")).items()} if f.exists() else {}


PAIRS = _load_pairs()
XS = np.array([0.0, 0.04, 0.09, 0.15, 0.22, 0.3, 0.38, 0.46, 0.55, 0.64, 0.74, 0.84, 0.92, 1.0])
NC = len(XS)
# раскладка вектора параметров
I_CURVE, I_SAT, I_VIB, I_HSL = 0, 3 * NC, 3 * NC + 1, 3 * NC + 2
I_VIG = I_HSL + 24
NAMES_EXTRA = ["vignette", "clarity", "texture", "sharpen", "dehaze", "shadows", "highlights", "whites", "blacks"]
I_MIX = I_VIG + len(NAMES_EXTRA)
SPATIAL = [I_VIG + k for k, n in enumerate(NAMES_EXTRA) if n in ("vignette", "clarity", "texture", "sharpen", "dehaze")]  # зависят от соседних пикселей
POINTWISE = [i for i in range(I_VIG + len(NAMES_EXTRA) + 9) if i not in SPATIAL]
N = I_MIX + 9
IDENT = np.array(IDENTITY_MIX)
_diag = np.eye(3, dtype=bool).ravel()
LO = np.concatenate([np.zeros(3 * NC), [-1, -1], -0.8 * np.ones(24), [-0.6, -1, -1, 0, -1, -1, -1, -1, -1], np.where(_diag, 0.3, -1.0)])
HI = np.concatenate([np.ones(3 * NC), [1, 1], 0.8 * np.ones(24), [0.6, 1, 1, 1, 1, 1, 1, 1, 1], np.where(_diag, 1.8, 1.0)])


def label_mask(w: int, h: int) -> np.ndarray:
    """False там, где в кадр вшита плашка BEFORE/AFTER (внизу слева)."""
    m = np.ones((h, w), bool)
    m[int(h * 0.86):int(h * 0.99), :int(w * 0.28)] = False
    return m


def load(pid: str, width: int):
    b, a = (Image.open(REF / f"{pid}{s}.jpg").convert("RGB") for s in ("", "after"))
    h = round(b.height * width / b.width)
    f = lambda im: np.asarray(im.resize((width, h), Image.LANCZOS), np.float32) / 255
    return f(b), f(a), label_mask(width, h)


def to_lab(rgb: np.ndarray) -> np.ndarray:
    lin = adjust.srgb_to_linear(np.clip(rgb, 0, 1))
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]], np.float32)
    xyz = lin @ m.T / np.array([0.95047, 1.0, 1.08883], np.float32)
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def build(v: np.ndarray) -> EditParams:
    p = EditParams()
    for i, ch in enumerate("rgb"):
        ys = np.maximum.accumulate(np.clip(v[i * NC:(i + 1) * NC], 0, 1))  # монотонность
        p.curves[ch] = [[float(x), float(y)] for x, y in zip(XS, ys)]
    p.saturation, p.vibrance = float(v[I_SAT]), float(v[I_VIB])
    for k, col in enumerate(HSL_COLORS):
        p.hsl[col] = [float(x) for x in v[I_HSL + 3 * k:I_HSL + 3 * k + 3]]
    for k, name in enumerate(NAMES_EXTRA):
        setattr(p, name, float(v[I_VIG + k]))
    p.mix = [float(x) for x in v[I_MIX:I_MIX + 9]]
    return p


def pav(y: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Монотонная (неубывающая) регрессия по взвешенным точкам."""
    blocks = []
    for yi, wi in zip(y, w):
        blocks.append([yi, wi, 1])
        while len(blocks) > 1 and blocks[-2][0] > blocks[-1][0]:
            b, a = blocks.pop(), blocks.pop()
            ww = a[1] + b[1]
            blocks.append([(a[0] * a[1] + b[0] * b[1]) / ww, ww, a[2] + b[2]])
    return np.concatenate([[b[0]] * b[2] for b in blocks])


def initial(before, after, mask) -> np.ndarray:
    """Старт: кривые по каналам из средних значений «после» по значению «до» (монотонно), остальное — ноль."""
    v = np.zeros(N)
    v[I_MIX:I_MIX + 9] = IDENT
    nb = 64
    cov = []
    for c in range(3):
        bins = np.minimum((before[..., c][mask] * nb).astype(int), nb - 1)
        s = np.bincount(bins, after[..., c][mask], nb)
        n = np.bincount(bins, minlength=nb)
        ok = n >= 100
        x, y = (np.arange(nb)[ok] + 0.5) / nb, pav(s[ok] / n[ok], n[ok])
        k = min(6, len(x) - 1)
        up = float(np.clip((y[-1] - y[-1 - k]) / (x[-1] - x[-1 - k]), 0, 1))
        lo = float(np.clip((y[k] - y[0]) / (x[k] - x[0]), 0, 1))
        node = np.where(XS < x[0], np.maximum(0, y[0] - lo * (x[0] - XS)),
                        np.where(XS > x[-1], np.minimum(1, y[-1] + up * (XS - x[-1])), np.interp(XS, x, y)))
        v[c * NC:(c + 1) * NC] = np.maximum.accumulate(np.clip(node, 0, 1))
        cov.append(x[-1])
    for i, x in enumerate(XS):  # узлы далеко за пределами снятого диапазона — догадка: каналы сводим к среднему, чтобы света не окрашивались
        far = [x > cov[c] + 0.12 for c in range(3)]
        if any(far):
            m = np.mean([v[c * NC + i] for c in range(3)])
            for c in range(3):
                if far[c]:
                    v[c * NC + i] = m
    return np.clip(v, LO, HI)


def sample_idx(mask: np.ndarray, n: int, seed: int = 0) -> np.ndarray:
    """Фиксированная выборка пикселей для функции ошибки: матрица производных оптимизатора растёт как число пикселей × параметры,
    поэтому всех пикселей брать нельзя (на 640 px это ~3 ГБ на процесс). Само изображение обрабатывается целиком (детали зависят от соседей)."""
    idx = np.flatnonzero(mask.ravel())
    if len(idx) > n:
        idx = np.sort(np.random.default_rng(seed).choice(idx, n, replace=False))
    return idx


def residuals(v, before, lab_sel, idx, free, base, w):
    full = base.copy()
    full[free] = v
    out = adjust.apply(before, build(full))
    lab_out = to_lab(out).reshape(-1, 3)
    d = ((lab_out if idx is None else lab_out[idx]) - lab_sel) * w
    reg = []
    for c in range(3):
        reg.append(14 * np.diff(full[c * NC:(c + 1) * NC], 2))             # гладкость кривых
    reg.append(3 * full[I_HSL:I_HSL + 24] + 0.0)                           # HSL — только если данные требуют
    reg.append(3 * full[[I_SAT, I_VIB]] * 0.3)
    reg.append(3 * full[I_VIG:I_VIG + len(NAMES_EXTRA)] * 0.6)
    reg.append(2 * (full[I_MIX:I_MIX + 9] - IDENT))                       # микшер — только если данные требуют
    return np.concatenate([d.ravel()] + [r.ravel() for r in reg])


def stats(out, after, mask):
    de = np.linalg.norm(to_lab(out) - to_lab(after), axis=-1)[mask]
    lum = (after @ np.array([0.2126, 0.7152, 0.0722], np.float32))[mask]
    q = lambda sel: float(de[sel].mean()) if sel.any() else float("nan")
    return {"deltaE_mean": float(de.mean()), "deltaE_p95": float(np.percentile(de, 95)), "deltaE_shadows": q(lum < 0.25),
            "deltaE_mids": q((lum >= 0.25) & (lum < 0.7)), "deltaE_highlights": q(lum >= 0.7)}


def fit_one(name: str) -> dict:
    """Этапы: 1) кривые, цвет, микшер на выборке (360 px); 2а) все поточечные параметры на выборке (640 px);
    2б) пространственные параметры на целой картинке; 2в) короткая общая доводка."""
    pid, src = PAIRS[name]
    b0, a0, m0 = load(pid, 360)
    v = initial(b0, a0, m0)
    idx0 = sample_idx(m0, 30000)
    bsel0 = b0.reshape(-1, 3)[idx0][None]               # выборка пикселей как «картинка 1×n»: поточечные параметры от соседей не зависят
    lab0 = to_lab(a0).reshape(-1, 3)[idx0]
    free = np.concatenate([np.arange(0, I_HSL), np.arange(I_MIX, N)])
    kw = dict(loss="soft_l1", f_scale=3.0, diff_step=1e-2)
    r = least_squares(residuals, v[free], bounds=(LO[free], HI[free]), args=(bsel0, lab0, None, free, v.copy(), 1 / np.sqrt(len(idx0))), max_nfev=60, **kw)
    v[free] = r.x
    b1, a1, m1 = load(pid, 640)                         # детали зависят от разрешения, поэтому дальше работаем на 640 px
    idx1 = sample_idx(m1, 60000, seed=1)
    bsel1 = b1.reshape(-1, 3)[idx1][None]
    lab1 = to_lab(a1).reshape(-1, 3)[idx1]
    w1 = 1 / np.sqrt(len(idx1))
    free = np.array(POINTWISE)
    r = least_squares(residuals, v[free], bounds=(LO[free], HI[free]), args=(bsel1, lab1, None, free, v.copy(), w1), max_nfev=90, **kw)
    v[free] = r.x
    free = np.array(SPATIAL)                            # виньетка, чёткость, текстура, резкость, дымка — на целой картинке
    r = least_squares(residuals, v[free], bounds=(LO[free], HI[free]), args=(b1, lab1, idx1, free, v.copy(), w1), max_nfev=35, **kw)
    v[free] = r.x
    free = np.arange(N)                                 # короткая общая доводка
    r = least_squares(residuals, v, bounds=(LO, HI), args=(b1, lab1, idx1, free, v.copy(), w1), max_nfev=8, **kw)
    v = r.x
    p = build(v)
    bf, af, mf = load(pid, 1024)                        # проверка на большем размере, чем подгоняли
    res = {"before": stats(bf, af, mf), "after": stats(adjust.apply(bf, p), af, mf)}
    print(f"{name}: ΔE {res['before']['deltaE_mean']:.2f} -> {res['after']['deltaE_mean']:.2f}  (p95 {res['after']['deltaE_p95']:.2f})", flush=True)
    return {"name": name, "source": src, "params": p.to_dict(), "quality": res}


def main():
    names = sys.argv[1:] or list(PAIRS)
    with ProcessPoolExecutor(max_workers=min(len(names), 2)) as ex:  # не больше двух процессов: память, см. sample_idx
        results = list(ex.map(fit_one, names))
    data = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    for r in results:
        data[r["name"]] = r
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print("записано:", OUT)


if __name__ == "__main__":
    main()
