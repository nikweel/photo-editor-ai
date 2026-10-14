"""Встроенные пакеты фильтров. Каждый фильтр — набор параметров движка (кривые, HSL, микшер и т. д.) с типом (категорией).
Фильтры, подобранные численно по парам «до/после», лежат отдельно в presets_site.json (см. scripts/fit_filters.py)."""
from ..core.adjust import EditParams

CATEGORIES = ["Портрет", "Пейзаж", "Улица", "Еда", "Ч/Б", "Кино", "Плёнка", "Тёмные (Moody)", "Яркие", "Базовые"]


def _p(**kw) -> EditParams:
    curve = kw.pop("curve", None)
    channels = kw.pop("channels", {})  # кривые по каналам: {"r": [...], "g": [...], "b": [...]}
    hsl = kw.pop("hsl", {})            # цвет по оттенкам: {"green": [оттенок, насыщенность, яркость], ...}
    mix = kw.pop("mix", None)          # микшер каналов (9 чисел по строкам)
    p = EditParams(**kw)
    for col, v in hsl.items():
        p.hsl[col] = list(v)
    if curve:
        p.curves["rgb"] = curve
    p.curves.update(channels)
    if mix:
        p.mix = list(mix)
    return p


def _bw(r: float, g: float, b: float) -> list[float]:
    """Микшер для чёрно-белого: вклад красного, зелёного и синего каналов в серый (как цветной светофильтр на плёнке)."""
    return [r, g, b] * 3


def _f(name: str, params: EditParams, _builtin: bool = True):
    return name, params


BASE = [
    _f("Яркий", _p(contrast=0.15, vibrance=0.35, saturation=0.1), True),
    _f("Тёплый закат", _p(temperature=0.35, tint=0.05, contrast=0.1, highlights=-0.2, vibrance=0.2), True),
    _f("Холодный", _p(temperature=-0.3, vibrance=0.1, contrast=0.05), True),
    _f("Матовый", _p(contrast=-0.1, saturation=-0.15, curve=[[0.0, 0.08], [1.0, 0.95]]), True),
    _f("Драматичный", _p(contrast=0.35, highlights=-0.3, shadows=0.15, blacks=-0.2, saturation=-0.1, clarity=0.35, vignette=-0.3), True),
    _f("Плёнка", _p(temperature=0.1, saturation=-0.1, grain=0.35, vignette=-0.15, curve=[[0.0, 0.05], [0.25, 0.2], [0.75, 0.8], [1.0, 0.96]]), True),
    _f("Мягкий портрет", _p(contrast=-0.1, highlights=-0.15, shadows=0.2, vibrance=0.15), True),
    _f("Чёрно-белый", _p(saturation=-1.0, contrast=0.2), True),
]

MOODY = [
    # Dark & Moody — по рецепту Lightroom: экспозиция -0.3…-0.8, контраст +15…+30, света -20…-45, тени +10…+25, белые -15…-30, чёрные -20…-40;
    # S-кривая с чуть приподнятой чёрной точкой (матовая дымка в тенях); HSL: кожа тёплая и светлая, зелёный и жёлтый сильно приглушены,
    # синий уходит в бирюзу; текстура +10, чёткость +10, дымка +8, виньетка -25.
    _f("Dark & Moody", _p(exposure=-0.5, contrast=0.22, saturation=-0.22, highlights=-0.32, shadows=0.18, whites=-0.22, blacks=-0.3,
                              texture=0.1, clarity=0.1, dehaze=0.08, vignette=-0.25, grain=0.08,
                              curve=[[0.0, 0.05], [0.25, 0.2], [0.75, 0.78], [1.0, 1.0]],
                              hsl={"red": [0.0, -0.1, -0.05], "orange": [0.07, -0.15, 0.1], "yellow": [-0.15, -0.5, -0.1],
                                   "green": [-0.28, -0.6, -0.2], "aqua": [0.1, -0.4, -0.15], "blue": [0.1, -0.4, -0.15],
                                   "purple": [0.0, -0.2, -0.1], "magenta": [0.0, -0.2, -0.05]}), True),
    _f("Moody · Кино", _p(exposure=-0.35, contrast=0.25, saturation=-0.32, highlights=-0.3, shadows=0.12, whites=-0.2, blacks=-0.25,
                              texture=0.08, clarity=0.1, dehaze=0.05, vignette=-0.25, grain=0.15,
                              curve=[[0.0, 0.04], [0.25, 0.2], [0.75, 0.79], [1.0, 1.0]],
                              channels={"r": [[0.0, 0.0], [0.3, 0.25], [0.7, 0.77], [1.0, 1.0]],              # тёплые света, красный в тенях приглушён
                                        "b": [[0.0, 0.05], [0.3, 0.33], [0.7, 0.65], [1.0, 0.93]]},           # бирюзовые тени
                              hsl={"orange": [0.06, -0.1, 0.12], "yellow": [-0.12, -0.4, -0.1], "green": [-0.2, -0.45, -0.15],
                                   "aqua": [0.12, -0.4, -0.1], "blue": [0.18, -0.5, -0.15]}), True),   # синий уходит в бирюзу и приглушается
    _f("Moody · Лес", _p(exposure=-0.45, contrast=0.25, saturation=-0.28, highlights=-0.3, shadows=0.15, whites=-0.2, blacks=-0.3,
                             texture=0.12, clarity=0.12, dehaze=0.1, vignette=-0.3, grain=0.08, temperature=-0.05, tint=-0.1,
                             curve=[[0.0, 0.04], [0.25, 0.19], [0.75, 0.77], [1.0, 0.99]],
                             hsl={"orange": [0.04, -0.2, 0.08], "yellow": [-0.2, -0.55, -0.12], "green": [-0.35, -0.5, -0.25],
                                  "aqua": [0.1, -0.35, -0.15], "blue": [0.08, -0.4, -0.15]}), True),
    _f("Moody · Портрет", _p(exposure=-0.35, contrast=0.2, saturation=-0.22, highlights=-0.25, shadows=0.2, whites=-0.18, blacks=-0.25,
                                 texture=0.06, clarity=0.05, vignette=-0.25, grain=0.06, temperature=0.06,
                                 curve=[[0.0, 0.05], [0.25, 0.21], [0.75, 0.78], [1.0, 1.0]],
                                 hsl={"red": [0.0, -0.1, -0.05], "orange": [0.08, -0.12, 0.15], "yellow": [-0.15, -0.5, -0.1],
                                      "green": [-0.3, -0.7, -0.2], "aqua": [0.1, -0.5, -0.15], "blue": [0.1, -0.5, -0.15]}), True),  # кожа светлее и теплее
    _f("Moody · Ч/Б", _p(exposure=-0.3, saturation=-1.0, contrast=0.3, highlights=-0.3, shadows=0.12, whites=-0.2, blacks=-0.3,
                             texture=0.12, clarity=0.2, dehaze=0.08, vignette=-0.3, grain=0.25,
                             curve=[[0.0, 0.04], [0.25, 0.19], [0.75, 0.79], [1.0, 1.0]]), True),
]

PORTRAIT = [
    _f("Мягкая кожа", _p(exposure=0.1, contrast=-0.08, highlights=-0.15, shadows=0.12, clarity=-0.2, texture=-0.15, vibrance=0.05, tint=0.02,
                         hsl={"red": [0, -0.05, 0.05], "orange": [0.02, -0.05, 0.1]})),
    _f("Тёплый портрет", _p(temperature=0.14, tint=0.02, exposure=0.1, contrast=0.08, highlights=-0.2, shadows=0.1, vibrance=0.1, vignette=-0.12,
                           hsl={"orange": [0.03, -0.08, 0.1], "yellow": [-0.05, -0.2, 0]})),
    _f("Светлый воздушный", _p(exposure=0.4, contrast=-0.1, highlights=-0.25, whites=0.15, shadows=0.35, blacks=0.15, saturation=-0.08,
                               curve=[[0.0, 0.03], [0.5, 0.56], [1.0, 1.0]])),
    _f("Глубокий (Low Key)", _p(exposure=-0.4, contrast=0.3, highlights=-0.2, shadows=-0.2, blacks=-0.25, clarity=0.15, vignette=-0.4,
                                curve=[[0.0, 0.0], [0.25, 0.16], [0.75, 0.8], [1.0, 1.0]])),
    _f("Студийный контраст", _p(contrast=0.28, clarity=0.25, sharpen=0.25, highlights=-0.15, whites=0.1, blacks=-0.1, vibrance=-0.05, vignette=-0.1)),
    _f("Золотой час", _p(temperature=0.3, tint=0.04, exposure=0.05, contrast=0.12, highlights=-0.25, shadows=0.15, vignette=-0.18,
                         curve=[[0.0, 0.03], [0.5, 0.52], [1.0, 0.98]],
                         hsl={"orange": [0.04, 0.08, 0.08], "yellow": [-0.05, 0.1, 0], "blue": [0.05, -0.2, -0.1]})),
    _f("Нежный пастель", _p(exposure=0.2, contrast=-0.18, saturation=-0.12, highlights=-0.1, shadows=0.25, blacks=0.25, temperature=0.04, tint=0.03,
                            vibrance=0.1, curve=[[0.0, 0.07], [0.5, 0.52], [1.0, 0.97]])),
    _f("Кино-портрет", _p(temperature=0.05, contrast=0.18, saturation=-0.1, clarity=0.1, vignette=-0.2,
                          channels={"r": [[0.0, 0.0], [0.3, 0.27], [0.7, 0.76], [1.0, 1.0]], "b": [[0.0, 0.05], [0.3, 0.34], [0.7, 0.66], [1.0, 0.94]]},
                          hsl={"orange": [0.03, -0.05, 0.1], "blue": [0.1, -0.15, -0.1]})),
    _f("Дневной свет", _p(exposure=0.12, contrast=0.06, vibrance=0.12, highlights=-0.12, shadows=0.1, clarity=0.1, sharpen=0.15)),
    _f("Стальной холод", _p(temperature=-0.14, saturation=-0.12, contrast=0.18, clarity=0.2, vignette=-0.2, hsl={"orange": [0, -0.15, 0.05]})),
]

LANDSCAPE = [
    _f("Яркий пейзаж", _p(contrast=0.2, vibrance=0.45, saturation=0.2, clarity=0.3, dehaze=0.15, highlights=-0.3, shadows=0.25, whites=0.1, blacks=-0.1, sharpen=0.3)),
    _f("Сочный лес", _p(contrast=0.18, vibrance=0.3, saturation=0.1, clarity=0.25, dehaze=0.12, shadows=0.2, temperature=-0.02,
                        hsl={"green": [-0.05, 0.45, -0.15], "yellow": [-0.1, 0.3, 0], "aqua": [0.05, 0.2, 0]})),
    _f("Золотой час (пейзаж)", _p(temperature=0.28, tint=0.03, exposure=0.05, contrast=0.15, highlights=-0.35, shadows=0.3, whites=0.05, vibrance=0.25,
                                  dehaze=0.1, vignette=-0.2, clarity=0.2,
                                  hsl={"orange": [0.03, 0.15, 0.05], "yellow": [0, 0.2, 0.05], "blue": [0.05, -0.1, -0.15]})),
    _f("Синий час", _p(temperature=-0.25, tint=-0.03, exposure=-0.15, contrast=0.2, saturation=0.05, highlights=-0.3, shadows=0.1, clarity=0.2, vignette=-0.25,
                       hsl={"blue": [0.03, 0.3, -0.1], "aqua": [0.05, 0.2, -0.05], "orange": [0, 0.2, 0.1]})),
    _f("Туман", _p(dehaze=-0.35, contrast=-0.2, saturation=-0.2, exposure=0.15, shadows=0.2, blacks=0.2, clarity=-0.1, temperature=-0.04,
                   curve=[[0.0, 0.06], [1.0, 0.98]])),
    _f("Драматичное небо", _p(contrast=0.3, dehaze=0.25, clarity=0.4, highlights=-0.5, whites=-0.2, shadows=0.15, blacks=-0.2, vignette=-0.3, sharpen=0.3,
                              hsl={"blue": [0.02, 0.35, -0.25], "aqua": [0, 0.2, -0.15]})),
    _f("Осень", _p(temperature=0.2, contrast=0.15, clarity=0.2, vignette=-0.18,
                   hsl={"orange": [0.03, 0.35, 0.08], "yellow": [0.05, 0.3, 0.05], "red": [0, 0.2, 0], "green": [-0.2, -0.2, -0.1]})),
    _f("Море", _p(temperature=-0.05, contrast=0.18, clarity=0.2, dehaze=0.12, highlights=-0.2, vibrance=0.3, saturation=0.08,
                  hsl={"aqua": [0.05, 0.5, -0.08], "blue": [0.03, 0.45, -0.12]})),
    _f("Горы (HDR-вид)", _p(clarity=0.5, texture=0.3, dehaze=0.2, highlights=-0.55, shadows=0.5, whites=0.15, blacks=-0.2, vibrance=0.25, contrast=0.1, sharpen=0.3)),
    _f("Зима", _p(temperature=-0.18, exposure=0.15, contrast=0.1, highlights=-0.2, whites=0.1, saturation=-0.1, clarity=0.15, tint=-0.02,
                  hsl={"blue": [0, 0.1, 0.1]})),
    _f("Пустыня", _p(temperature=0.2, contrast=0.2, clarity=0.3, dehaze=0.12, vignette=-0.15,
                     hsl={"orange": [0.02, 0.2, 0], "yellow": [0, 0.25, 0.05], "red": [0, 0.15, 0], "blue": [0.05, 0.1, -0.2]})),
]

STREET = [
    _f("Городской контраст", _p(contrast=0.3, clarity=0.35, texture=0.25, saturation=-0.15, highlights=-0.25, shadows=0.1, blacks=-0.2, vignette=-0.2, sharpen=0.25, grain=0.1)),
    _f("Неон ночью", _p(contrast=0.25, saturation=0.25, shadows=-0.1, highlights=-0.2, clarity=0.15, vignette=-0.3,
                        channels={"b": [[0.0, 0.06], [0.3, 0.34], [0.7, 0.7], [1.0, 1.0]], "g": [[0.0, 0.0], [0.5, 0.47], [1.0, 1.0]]},
                        hsl={"blue": [0.05, 0.3, 0.1], "magenta": [0, 0.3, 0.1], "aqua": [0.05, 0.3, 0]})),
    _f("Грубая улица", _p(contrast=0.35, clarity=0.5, texture=0.4, saturation=-0.3, grain=0.3, vignette=-0.25, highlights=-0.2, blacks=-0.25, sharpen=0.3)),
    _f("Ретро-улица", _p(temperature=0.1, saturation=-0.15, contrast=0.1, grain=0.2, vignette=-0.2, tint=0.03, curve=[[0.0, 0.05], [1.0, 0.95]])),
]

FILM = [
    _f("Тёплая плёнка", _p(temperature=0.1, contrast=-0.05, saturation=-0.1, grain=0.25, vignette=-0.12, blacks=0.1, shadows=0.1,
                           curve=[[0.0, 0.05], [0.25, 0.22], [0.75, 0.78], [1.0, 0.96]], channels={"r": [[0.0, 0.0], [0.5, 0.52], [1.0, 1.0]]},
                           hsl={"yellow": [-0.05, 0.1, 0], "green": [-0.1, -0.15, 0]})),
    _f("Холодная плёнка", _p(tint=-0.06, temperature=-0.06, saturation=-0.1, grain=0.25, contrast=0.08,
                             channels={"g": [[0.0, 0.03], [0.3, 0.33], [0.7, 0.72], [1.0, 1.0]]})),
    _f("Выцветшая 70-х", _p(saturation=-0.3, temperature=0.12, contrast=-0.15, blacks=0.25, grain=0.3, vignette=-0.18, curve=[[0.0, 0.1], [1.0, 0.92]],
                            hsl={"orange": [0.04, 0.1, 0], "blue": [0, -0.2, 0]})),
    _f("Кросс-процесс", _p(contrast=0.15, saturation=0.15, vignette=-0.15, grain=0.15,
                           channels={"r": [[0.0, 0.0], [0.25, 0.15], [0.75, 0.9], [1.0, 1.0]], "g": [[0.0, 0.0], [0.5, 0.55], [1.0, 1.0]],
                                     "b": [[0.0, 0.1], [0.5, 0.45], [1.0, 0.85]]})),
    _f("Полароид", _p(temperature=0.1, tint=0.04, saturation=-0.1, contrast=-0.1, blacks=0.2, highlights=-0.2, vignette=-0.3, grain=0.2,
                      curve=[[0.0, 0.08], [1.0, 0.94]], hsl={"blue": [0.05, -0.2, 0]})),
]

BLACK_WHITE = [
    _f("Классический Ч/Б", _p(mix=_bw(0.3, 0.59, 0.11), contrast=0.15, clarity=0.15)),
    _f("Контрастный Ч/Б (красный фильтр)", _p(mix=_bw(0.6, 0.3, 0.1), contrast=0.35, clarity=0.3, blacks=-0.15, whites=0.1, vignette=-0.15, sharpen=0.2)),
    _f("Мягкий Ч/Б", _p(mix=_bw(0.35, 0.5, 0.15), contrast=-0.1, highlights=-0.15, shadows=0.2, grain=0.08, curve=[[0.0, 0.06], [1.0, 0.97]])),
    _f("Ч/Б плёнка", _p(mix=_bw(0.4, 0.45, 0.15), contrast=0.12, grain=0.35, vignette=-0.18, blacks=0.05, curve=[[0.0, 0.03], [1.0, 0.97]])),
    _f("Холодный Ч/Б", _p(mix=_bw(0.3, 0.59, 0.11), contrast=0.12,
                          channels={"b": [[0.0, 0.02], [0.5, 0.54], [1.0, 1.0]], "r": [[0.0, 0.0], [0.5, 0.47], [1.0, 0.97]]})),
    _f("Сепия", _p(mix=_bw(0.3, 0.59, 0.11), contrast=0.08,
                   channels={"r": [[0.0, 0.03], [0.5, 0.56], [1.0, 1.0]], "g": [[0.0, 0.0], [0.5, 0.48], [1.0, 0.93]], "b": [[0.0, 0.0], [0.5, 0.36], [1.0, 0.74]]})),
    _f("Ч/Б улица", _p(mix=_bw(0.5, 0.4, 0.1), contrast=0.4, clarity=0.4, texture=0.3, grain=0.3, vignette=-0.25, blacks=-0.2)),
]

FOOD = [
    _f("Тёплая еда", _p(temperature=0.12, exposure=0.1, contrast=0.12, vibrance=0.25, saturation=0.08, clarity=0.2, highlights=-0.15, shadows=0.1, sharpen=0.25,
                        hsl={"orange": [0, 0.2, 0.08], "yellow": [0, 0.25, 0.05], "red": [0, 0.2, 0], "green": [0, 0.1, 0]})),
    _f("Яркая и сочная", _p(contrast=0.18, vibrance=0.4, saturation=0.15, clarity=0.25, sharpen=0.3, highlights=-0.2, shadows=0.15, whites=0.1)),
    _f("Тёмная еда", _p(exposure=-0.3, contrast=0.3, temperature=0.08, saturation=-0.08, clarity=0.25, shadows=-0.1, highlights=-0.2, vignette=-0.35,
                        hsl={"orange": [0, 0.1, -0.05], "yellow": [0, 0.15, -0.05]})),
    _f("Светлая и чистая", _p(exposure=0.35, contrast=-0.05, highlights=-0.2, whites=0.2, shadows=0.25, saturation=-0.05, vibrance=0.1, temperature=-0.02, sharpen=0.25)),
]

# (пакет, описание, список фильтров, тип по умолчанию, типы отдельных фильтров)
BASE_TYPES = {"Яркий": "Яркие", "Тёплый закат": "Пейзаж", "Холодный": "Базовые", "Матовый": "Плёнка", "Драматичный": "Кино", "Плёнка": "Плёнка",
              "Мягкий портрет": "Портрет", "Чёрно-белый": "Ч/Б"}
PACKS = [
    ("Базовые", "Универсальные фильтры на каждый день", BASE, "Базовые", BASE_TYPES),
    ("Портрет", "Кожа, свет и настроение для людей", PORTRAIT, "Портрет", {"Кино-портрет": "Кино"}),
    ("Пейзаж", "Природа, небо, вода и сезоны", LANDSCAPE, "Пейзаж", {}),
    ("Улица и город", "Контраст, текстура и ночные огни", STREET, "Улица", {}),
    ("Плёнка и винтаж", "Зерно, выцветание и плёночные тона", FILM, "Плёнка", {}),
    ("Чёрно-белые", "Классика, контраст, тонирование", BLACK_WHITE, "Ч/Б", {}),
    ("Еда", "Продукты, кафе и фуд-съёмка", FOOD, "Еда", {}),
    ("Dark & Moody", "Тёмный драматичный стиль: глубокие тени, приглушённый цвет", MOODY, "Тёмные (Moody)", {"Moody · Ч/Б": "Ч/Б"}),
]
SITE_PACK = ("Подобранные по образцам", "Виды, подобранные численно по парам «до/после» (кривые, HSL, микшер каналов); приближения, а не копии чужих пресетов")
SITE_TYPES = {"Moody · Тёплый беж": "Тёмные (Moody)", "Кино · Мягкий свет": "Кино", "Кино · Тёмный янтарь": "Кино", "Улица · Золотистый тон": "Улица",
              "Улица · Светлый воздух": "Улица", "Плёнка · Изумрудная трава": "Плёнка"}
