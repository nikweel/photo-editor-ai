"""Неразрушающие правки: параметры отдельно от пикселей, применяются к исходнику заново при каждом изменении."""
from dataclasses import asdict, dataclass, field, fields
from functools import lru_cache

import numpy as np
from PIL import Image, ImageFilter

LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)
CHANNELS = ("rgb", "r", "g", "b")
_SPECIAL = {"curves", "lut", "lut_strength", "crop", "hsl", "mix"}
_GEOM_INT = {"rotate90", "flip_h", "flip_v"}
_GEOM_NAMES = _GEOM_INT | {"straighten"}
IDENTITY_CURVE = [[0.0, 0.0], [1.0, 1.0]]
# HSL по цветам: центры оттенков в градусах; между соседними центрами вес плавно переходит, веса в сумме дают 1
HSL_COLORS = ("red", "orange", "yellow", "green", "aqua", "blue", "purple", "magenta")
HSL_NODES = np.array([0, 30, 60, 120, 180, 240, 275, 315], np.float32)
HUE_SHIFT_DEG = 30.0   # полный ход ползунка «Оттенок» = ±30°


IDENTITY_MIX = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]  # строки: выход R, G, B; столбцы: вклад входных R, G, B


def _hsl() -> dict:
    return {c: [0.0, 0.0, 0.0] for c in HSL_COLORS}  # [оттенок, насыщенность, яркость], каждое -1..1


def _curves() -> dict:
    return {c: [p[:] for p in IDENTITY_CURVE] for c in CHANNELS}


@dataclass
class EditParams:
    exposure: float = 0.0     # EV, ступени экспозиции
    contrast: float = 0.0     # -1..1
    highlights: float = 0.0   # -1..1
    shadows: float = 0.0
    whites: float = 0.0
    blacks: float = 0.0
    temperature: float = 0.0  # -1 холоднее .. 1 теплее
    tint: float = 0.0         # -1 зеленее .. 1 пурпурнее
    vibrance: float = 0.0
    saturation: float = 0.0
    curves: dict = field(default_factory=_curves)  # канал -> точки [[x, y], ...] в 0..1
    lut: str = ""             # путь к .cube-фильтру
    lut_strength: float = 1.0
    hsl: dict = field(default_factory=_hsl)  # цвет по оттенкам
    mix: list = field(default_factory=lambda: list(IDENTITY_MIX))  # микшер каналов 3x3 (по строкам)
    texture: float = 0.0      # -1..1, мелкий локальный контраст
    dehaze: float = 0.0       # -1..1, убрать или добавить дымку
    sharpen: float = 0.0      # 0..1, резкость
    clarity: float = 0.0      # -1..1, локальный контраст средних тонов
    noise_color: float = 0.0  # 0..1, подавление цветового шума
    vignette: float = 0.0     # -1 затемнить края .. 1 осветлить
    grain: float = 0.0        # 0..1, плёночное зерно
    rotate90: int = 0         # поворот по часовой, в четвертях (0..3)
    flip_h: int = 0
    flip_v: int = 0
    straighten: float = 0.0   # градусы, -45..45
    crop: list = field(default_factory=lambda: [0.0, 0.0, 1.0, 1.0])  # x0, y0, x1, y1 в долях кадра после поворота

    def curve_is_identity(self) -> bool:
        return all(len(p) == 2 and p[0] == [0.0, 0.0] and p[1] == [1.0, 1.0] for p in self.curves.values())

    def has_geometry(self) -> bool:
        return bool(self.rotate90 % 4 or self.flip_h or self.flip_v or self.straighten or self.crop != [0.0, 0.0, 1.0, 1.0])

    def mix_is_identity(self) -> bool:
        return all(abs(a - b) < 1e-9 for a, b in zip(self.mix, IDENTITY_MIX))

    def hsl_is_identity(self) -> bool:
        return all(v == [0.0, 0.0, 0.0] for v in self.hsl.values())

    def color_is_identity(self) -> bool:
        return (self.curve_is_identity() and self.hsl_is_identity() and self.mix_is_identity() and not self.lut
                and all(getattr(self, f.name) == 0 for f in fields(self) if f.name not in _SPECIAL | _GEOM_NAMES))

    def is_identity(self) -> bool:
        return (self.curve_is_identity() and self.hsl_is_identity() and self.mix_is_identity() and not self.lut and not self.has_geometry()
                and all(getattr(self, f.name) == 0 for f in fields(self) if f.name not in _SPECIAL))

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "EditParams":
        p = cls()
        for f in fields(cls):
            if f.name in d and f.name not in _SPECIAL | _GEOM_INT:
                setattr(p, f.name, float(d[f.name]))
        p.lut = str(d.get("lut") or "")
        for k in _GEOM_INT:
            if k in d:
                setattr(p, k, int(d[k]) % 4 if k == "rotate90" else int(bool(d[k])))
        for col, v in (d.get("hsl") or {}).items():
            if col in HSL_COLORS and isinstance(v, (list, tuple)) and len(v) == 3:
                p.hsl[col] = [min(max(float(x), -1.0), 1.0) for x in v]
        m = d.get("mix")
        if isinstance(m, (list, tuple)) and len(m) == 9:
            p.mix = [min(max(float(x), -3.0), 3.0) for x in m]
        c = d.get("crop")
        if isinstance(c, (list, tuple)) and len(c) == 4:
            x0, y0, x1, y1 = (min(max(float(v), 0.0), 1.0) for v in c)
            if x1 - x0 >= 0.02 and y1 - y0 >= 0.02:  # кадр меньше 2% — явно испорченные данные
                p.crop = [x0, y0, x1, y1]
        for c, pts in (d.get("curves") or {}).items():
            if c in CHANNELS and len(pts) >= 2:
                p.curves[c] = [[float(x), float(y)] for x, y in pts]
        return p


def srgb_to_linear(a: np.ndarray) -> np.ndarray:
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(a: np.ndarray) -> np.ndarray:
    a = np.clip(a, 0, None)
    return np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(a, 1 / 2.4) - 0.055)


def _shoulder(a: np.ndarray, knee: float = 0.8) -> np.ndarray:
    """Мягкое сжатие светов выше knee, чтобы осветление не давало резкого пересвета."""
    over = np.maximum(a - knee, 0)
    return np.where(a > knee, knee + (1 - knee) * (1 - np.exp(-over / (1 - knee))), a)


def curve_lut(points: list[list[float]], n: int = 1024) -> np.ndarray:
    """Монотонная кубическая интерполяция (Fritsch–Carlson): кривая гладкая и не даёт «ступенек» назад."""
    pts = sorted(points)
    x, y = np.array([p[0] for p in pts], np.float64), np.array([p[1] for p in pts], np.float64)
    xs = np.linspace(0, 1, n)
    if len(x) < 2:
        return xs.astype(np.float32)
    h, d = np.diff(x), np.diff(y) / np.maximum(np.diff(x), 1e-9)
    m = np.zeros(len(x))
    m[0], m[-1] = d[0], d[-1]
    for i in range(1, len(x) - 1):
        m[i] = 0 if d[i - 1] * d[i] <= 0 else 2 / (1 / d[i - 1] + 1 / d[i])  # гармоническое среднее наклонов
    i = np.clip(np.searchsorted(x, xs, side="right") - 1, 0, len(x) - 2)
    t = (xs - x[i]) / np.maximum(h[i], 1e-9)
    t = np.clip(t, 0, 1)
    h00, h10, h01, h11 = 2 * t**3 - 3 * t**2 + 1, t**3 - 2 * t**2 + t, -2 * t**3 + 3 * t**2, t**3 - t**2
    out = h00 * y[i] + h10 * h[i] * m[i] + h01 * y[i + 1] + h11 * h[i] * m[i + 1]
    out = np.where(xs < x[0], y[0], np.where(xs > x[-1], y[-1], out))
    return np.clip(out, 0, 1).astype(np.float32)


def _lut_apply(a: np.ndarray, lut: np.ndarray) -> np.ndarray:
    """Применение таблицы кривой по индексу ближайшей точки; таблица в 4096 точек даёт ошибку < 0,0002 и в разы быстрее np.interp."""
    n = len(lut) - 1
    return np.take(lut, (a * n + 0.5).astype(np.int32).clip(0, n))


def apply(img: np.ndarray, p: EditParams) -> np.ndarray:
    """img: float32 [H, W, 3] sRGB 0..1 -> результат того же вида."""
    if p.color_is_identity():
        return img
    out = img
    if p.temperature or p.tint or p.exposure:  # перевод в линейный свет и обратно дорог, поэтому — только если нужен
        lin = srgb_to_linear(img)
        if p.temperature or p.tint:  # баланс белого в линейном свете
            lin = lin * np.array([1 + 0.35 * p.temperature, 1 - 0.2 * p.tint, 1 - 0.35 * p.temperature], np.float32)
        if p.exposure:
            lin = lin * 2.0 ** p.exposure
            if p.exposure > 0:
                lin = _shoulder(lin)
        out = linear_to_srgb(lin)
    if p.highlights or p.shadows or p.whites or p.blacks:  # тоновые маски по яркости
        L = np.clip(out @ LUMA, 0, 1)[..., None]
        add = p.shadows * (1 - L) ** 2 + p.highlights * L**2 * 0.8 + p.whites * L**4 + p.blacks * (1 - L) ** 4 * 0.8
        out = out + add * 0.35
    if p.contrast:
        out = (out - 0.5) * (1 + p.contrast) + 0.5
    if not p.mix_is_identity():  # микшер каналов: цвет «перетекает» между каналами (как Channel Mixer в Photoshop)
        out = np.clip(out, 0, 1) @ np.array(p.mix, np.float32).reshape(3, 3).T
        out = np.clip(out, 0, 1)
    if p.saturation or p.vibrance:
        out = np.clip(out, 0, 1)
        gray = (out @ LUMA)[..., None]
        sat = (_cmax(out) - _cmin(out))[..., None]
        k = 1 + p.saturation + p.vibrance * (1 - sat)  # вибранс усиливает в основном бледные цвета
        out = gray + (out - gray) * np.clip(k, 0, 3)
    out = np.clip(out, 0, 1).astype(np.float32)
    if not p.hsl_is_identity():
        out = _apply_hsl(out, p.hsl)
    if not p.curve_is_identity():
        out = _lut_apply(out, curve_lut(p.curves["rgb"], 4096)) if p.curves["rgb"] != IDENTITY_CURVE else out
        for i, c in enumerate("rgb"):
            if p.curves[c] != IDENTITY_CURVE:
                out[..., i] = _lut_apply(out[..., i], curve_lut(p.curves[c], 4096))
    if p.lut:
        try:
            from .lut import apply_lut

            out = apply_lut(out, p.lut, p.lut_strength)
        except Exception:  # файл фильтра удалён или повреждён — остальные правки всё равно показываем
            pass
    return _details(out, p)


def _cmax(a: np.ndarray) -> np.ndarray:
    """Максимум по каналам. Редукция numpy по оси длиной 3 медленная; поэлементное сравнение трёх каналов в разы быстрее."""
    return np.maximum(np.maximum(a[..., 0], a[..., 1]), a[..., 2])


def _cmin(a: np.ndarray) -> np.ndarray:
    return np.minimum(np.minimum(a[..., 0], a[..., 1]), a[..., 2])


def _rgb_to_hsv(a: np.ndarray):
    """HSV: оттенок в градусах [0, 360), насыщенность и яркость 0..1. Без лишних временных массивов."""
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = _cmax(a), _cmin(a)
    d = mx - mn
    safe = np.where(d > 1e-6, d, np.float32(1.0))
    h = np.where(mx == r, (g - b) / safe, np.where(mx == g, (b - r) / safe + 2, (r - g) / safe + 4))
    h = (h % 6) * np.float32(60.0)
    h[d <= 1e-6] = 0
    s = d / np.maximum(mx, np.float32(1e-6))
    return h.astype(np.float32, copy=False), s.astype(np.float32, copy=False), mx


def _hsv_to_rgb(h: np.ndarray, s: np.ndarray, v: np.ndarray) -> np.ndarray:
    h6 = (h % 360.0) / np.float32(60.0)
    vs = v * s
    out = np.empty(h.shape + (3,), np.float32)
    for c, n in enumerate((5, 3, 1)):  # R, G, B: общая формула HSV без ветвлений
        k = (n + h6) % 6
        out[..., c] = v - vs * np.clip(np.minimum(k, 4 - k), 0, 1)
    return out


_HSL_RES = 1440  # шагов по кругу оттенков (0,25°): правки по цвету зависят только от оттенка, поэтому считаются один раз на таблицу


def _hue_tables(hsl: dict):
    """Таблицы добавок оттенка, насыщенности и яркости по оттенку. Вес цвета i — «шапка» между соседними центрами по кругу:
    веса соседних цветов в сумме дают 1."""
    nodes = HSL_NODES
    hh = (np.arange(_HSL_RES, dtype=np.float32) + 0.5) * np.float32(360.0 / _HSL_RES)
    idx = np.clip(np.searchsorted(nodes, hh, side="right") - 1, 0, len(nodes) - 1)
    lo, hi = nodes[idx], np.where(idx + 1 < len(nodes), nodes[np.minimum(idx + 1, len(nodes) - 1)], 360.0)
    t = np.clip((hh - lo) / np.maximum(hi - lo, 1e-6), 0, 1)
    tab = np.zeros((3, _HSL_RES), np.float32)
    for i, col in enumerate(HSL_COLORS):
        vals = hsl[col]
        if not any(vals):
            continue
        w = np.where(idx == i, 1 - t, 0.0) + np.where((idx + 1) % len(nodes) == i, t, 0.0)
        for k in range(3):
            tab[k] += w * vals[k]
    return tab


def _apply_hsl(a: np.ndarray, hsl: dict) -> np.ndarray:
    """Оттенок, насыщенность и яркость по восьми цветам. Серые пиксели не затрагиваются: правка растёт вместе с насыщенностью пикселя."""
    h, s, v = _rgb_to_hsv(a)
    tab = _hue_tables(hsl)
    bi = np.minimum((h * np.float32(_HSL_RES / 360.0)).astype(np.int32), _HSL_RES - 1)
    dh, ds, dv = tab[0][bi], tab[1][bi], tab[2][bi]
    chroma = np.clip(s * 2.0, 0, 1)  # почти серое не получает чужой оттенок и яркость
    h2 = h + dh * np.float32(HUE_SHIFT_DEG) * chroma
    s2 = np.clip(s * (1 + ds), 0, 1)
    v2 = np.clip(v * (1 + dv * 0.5 * chroma), 0, 1)
    return np.clip(_hsv_to_rgb(h2, s2, v2), 0, 1)


def _blur(a: np.ndarray, radius: float) -> np.ndarray:
    """Гауссово размытие (PIL, быстро и на больших кадрах); точность 8 бит достаточна для слоя деталей.
    Большой радиус (чёткость, дымка) даёт только низкие частоты, поэтому считается на уменьшенной копии."""
    im = Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))  # 2D — режим L, 3D — RGB
    f = int(radius // 6)  # во сколько раз уменьшать: радиус после уменьшения остаётся ≥ ~6 px
    if f >= 2:
        small = im.reduce(f).filter(ImageFilter.GaussianBlur(max(radius / f, 0.3)))
        return np.asarray(small.resize(im.size, Image.BILINEAR), np.float32) / 255
    return np.asarray(im.filter(ImageFilter.GaussianBlur(max(radius, 0.3))), np.float32) / 255


@lru_cache(maxsize=4)
def _vignette_mask(h: int, w: int) -> np.ndarray:
    """Маска виньетки (0 в центре, 1 по углам); не зависит от силы, поэтому кэшируется по размеру кадра."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx / max(w - 1, 1) - 0.5) * 2) ** 2 + ((yy / max(h - 1, 1) - 0.5) * 2) ** 2) / np.sqrt(2)
    m = np.clip((d - 0.35) / 0.65, 0, 1)
    return (m * m * (3 - 2 * m))[..., None].astype(np.float32)


@lru_cache(maxsize=4)
def _grain_noise(h: int, w: int) -> np.ndarray:
    """Воспроизводимое зерно; размер зерна как на превью 1600 px."""
    k = min(1.0, 1600 / max(h, w))
    n = np.random.default_rng(1234).standard_normal((max(2, round(h * k)), max(2, round(w * k)))).astype(np.float32)
    return np.asarray(Image.fromarray(n, "F").resize((w, h), Image.BILINEAR), np.float32)[..., None]


def _details(out: np.ndarray, p: EditParams) -> np.ndarray:
    """Резкость, локальный контраст, цветовой шум, виньетка, зерно. Радиусы заданы долей длинной стороны,
    поэтому превью и полный кадр выглядят одинаково."""
    if not (p.sharpen or p.clarity or p.texture or p.dehaze or p.noise_color or p.vignette or p.grain):
        return out
    h, w, _ = out.shape
    side = max(h, w)
    if p.noise_color:
        y = (out @ LUMA)[..., None]
        chroma = _blur(np.clip(out - y + 0.5, 0, 1), side * 0.004) - 0.5  # смещение 0.5: размытие работает с неотрицательными значениями
        out = y + (out - y) * (1 - p.noise_color) + chroma * p.noise_color
    if p.dehaze:
        if p.dehaze > 0:  # убираем «вуаль»: чем светлее тёмный канал в окрестности, тем больше дымки
            veil = _blur(_cmin(out), side * 0.03)[..., None] * p.dehaze * 0.6  # один канал: размытие втрое дешевле
            out = (out - veil) / np.maximum(1 - veil, 0.2)
        else:
            v = -p.dehaze * 0.3
            out = out * (1 - v) + v * 0.85
        out = np.clip(out, 0, 1)
    if p.texture:
        out = out + (out - _blur(out, max(side * 0.004, 0.8))) * p.texture * 1.2
    if p.clarity:
        lum = np.clip(out @ LUMA, 0, 1)[..., None]
        mid = 1 - np.abs(2 * lum - 1) ** 2  # маска средних тонов: света и тени не «плавятся»
        out = out + (out - _blur(out, side * 0.02)) * p.clarity * 0.9 * mid
    if p.sharpen:
        out = out + (out - _blur(out, max(side * 0.0012, 0.6))) * p.sharpen * 1.6
    if p.vignette:
        m = _vignette_mask(h, w)
        out = out * (1 + p.vignette * m) if p.vignette < 0 else out + (1 - out) * p.vignette * m * 0.8
    if p.grain:
        out = out + _grain_noise(h, w) * p.grain * 0.06
    return np.clip(out, 0, 1).astype(np.float32)


def apply_geometry(img: np.ndarray, p: EditParams, crop: bool = True) -> np.ndarray:
    """Поворот на 90°, отражения, выравнивание горизонта (с обрезкой пустых углов) и кадрирование."""
    if not p.has_geometry():
        return img
    out = np.rot90(img, -(p.rotate90 % 4)) if p.rotate90 % 4 else img  # по часовой стрелке
    if p.flip_h:
        out = out[:, ::-1]
    if p.flip_v:
        out = out[::-1]
    if p.straighten:
        h, w, _ = out.shape
        im = Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)).rotate(-p.straighten, Image.BICUBIC)
        t = np.radians(abs(p.straighten))
        c, s_ = np.cos(t), np.sin(t)
        k = min(w / (w * c + h * s_), h / (w * s_ + h * c))  # наибольший вписанный прямоугольник тех же пропорций
        cw, ch = max(1, int(w * k)), max(1, int(h * k))
        x0, y0 = (w - cw) // 2, (h - ch) // 2
        out = np.asarray(im, np.float32)[y0:y0 + ch, x0:x0 + cw] / 255
    if crop and p.crop != [0.0, 0.0, 1.0, 1.0]:
        h, w, _ = out.shape
        x0, y0, x1, y1 = p.crop
        out = out[int(round(y0 * h)):max(int(round(y1 * h)), int(round(y0 * h)) + 1), int(round(x0 * w)):max(int(round(x1 * w)), int(round(x0 * w)) + 1)]
    return np.ascontiguousarray(out, dtype=np.float32)


def render(img: np.ndarray, p: EditParams) -> np.ndarray:
    """Полный результат: геометрия, затем цвет и детали."""
    return apply(apply_geometry(img, p), p)
