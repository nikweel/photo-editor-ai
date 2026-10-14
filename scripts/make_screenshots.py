"""Скриншоты для README: генерирует демо-пейзаж (без чужих фото), открывает его в редакторе и снимает окно.
Запуск (без экрана): QT_QPA_PLATFORM=offscreen uv run python scripts/make_screenshots.py"""
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def demo_landscape(w: int = 1800, h: int = 1200, seed: int = 7) -> Image.Image:
    """Сгенерированный пейзаж: небо с облаками, три хребта, озеро с отражением, лёгкое зерно."""
    rng = np.random.default_rng(seed)
    y = np.linspace(0, 1, h)[:, None]
    x = np.linspace(0, 1, w)[None, :]
    horizon = int(h * 0.62)
    sky = np.stack([0.30 + 0.45 * y.repeat(w, 1) ** 1.3, 0.45 + 0.35 * y.repeat(w, 1) ** 1.1, 0.78 - 0.10 * y.repeat(w, 1)], -1)
    glow = np.exp(-(((x - 0.68) / 0.22) ** 2 + ((y - 0.5) / 0.20) ** 2))[..., None]
    img = sky + glow * np.array([0.55, 0.38, 0.12])
    noise = sum(np.asarray(Image.fromarray(rng.random((h // s, w // s)).astype(np.float32), "F").resize((w, h), Image.BICUBIC)) / 2 ** i for i, s in enumerate((300, 150, 75, 38)))
    clouds = np.clip((noise - 0.55) * 1.8, 0, 1)[..., None] * (1 - y[..., None]) * 0.5
    img = img * (1 - clouds) + clouds * np.array([1.0, 0.95, 0.9])
    xs = np.arange(w)
    for k, (base, amp, col) in enumerate(((0.50, 0.10, (0.45, 0.50, 0.62)), (0.55, 0.12, (0.28, 0.36, 0.40)), (0.60, 0.10, (0.12, 0.20, 0.18)))):
        ridge = base * h + amp * h * sum(np.sin(xs / w * f * 6.283 + rng.random() * 6.283) / f for f in (1, 2.3, 4.7, 9.1, 17)) * 0.5
        mask = (np.arange(h)[:, None] > ridge[None, :])[..., None]
        shade = 0.85 + 0.15 * np.asarray(Image.fromarray(rng.random((h // 40, w // 40)).astype(np.float32), "F").resize((w, h), Image.BICUBIC))[..., None]
        img = np.where(mask, np.array(col) * shade, img)
    lake = (np.arange(h)[:, None] > horizon)[..., None]
    refl = img[::-1][: h - horizon + 1][: h - horizon]
    reflected = np.zeros_like(img)
    reflected[horizon:] = np.asarray(Image.fromarray((np.clip(refl, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)), np.float32)[: h - horizon] / 255 * 0.75
    ripple = 1 + 0.04 * np.sin(np.arange(h)[:, None] * 0.9) * np.ones((1, w))
    img = np.where(lake, reflected * ripple[..., None] + np.array([0.0, 0.03, 0.06]), img)
    img = np.clip(img + rng.normal(0, 0.012, img.shape), 0, 1)
    return Image.fromarray((img * 255).astype(np.uint8))


def main():
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication, QTabWidget

    import app.services.filters as FL
    import app.utils.settings as S
    from app.gui import theme

    out = ROOT / "docs" / "screenshots"
    tmp = Path(tempfile.mkdtemp())
    S.FILE = tmp / "settings.json"  # настройки и каталог — во временной папке, ваши не трогаем
    a = QApplication([])
    theme.apply(a)
    from app.gui.main_window import MainWindow

    demo_landscape().save(tmp / "demo.jpg", quality=93)
    w = MainWindow()
    w.lib.file = tmp / "library.json"
    w.lib.entries.clear()
    w.strip.clear()
    w.strip.items.clear()
    w.store = FL.FilterStore(tmp / "presets")
    w._filter_list()
    w.resize(1440, 880)
    w.show()
    w._add_to_library([tmp / "demo.jpg"])
    a.processEvents()
    tabs = w.findChildren(QTabWidget)[0]

    def pick(name):
        it = next(i for i in w.ftree.findItems("", Qt.MatchContains | Qt.MatchRecursive) if i.text(0) == name)
        it.parent().setExpanded(True)
        w.ftree.setCurrentItem(it)
        a.processEvents()
        w.render()
        a.processEvents()

    def shot(name):
        a.processEvents()
        w.grab().save(str(out / f"{name}.png"))
        print("saved", name)

    tabs.setCurrentIndex(0)
    shot("main")                                  # главное окно, вкладка «Авто · ИИ»
    tabs.setCurrentIndex(2)
    pick("Золотой час (пейзаж)")
    w.cmp_btn.setChecked(True)
    w.canvas.split = 0.5
    shot("compare")                               # «До / После» с фильтром
    w.cmp_btn.setChecked(False)
    pick("Dark & Moody")
    shot("filters")                               # пакеты фильтров
    w.fgroup.setCurrentIndex(1)
    tabs.setCurrentIndex(1)
    for sec in w.findChildren(type(w._open_secs[0])):  # раскрыть кривую
        if sec.head.text().startswith("ТОНОВАЯ") and not sec.head.isChecked():
            sec.head.setChecked(True)
    shot("manual")                                # ручные настройки и кривая


if __name__ == "__main__":
    main()
