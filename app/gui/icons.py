"""Векторные значки интерфейса (линейные, в духе Lucide). Рисуются из SVG и перекрашиваются под тему, поэтому одинаково резкие на любом масштабе."""
from functools import lru_cache

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QImage, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from .theme import TEXT

# 24x24, линия 1.8; «currentColor» подменяется цветом
PATHS = {
    "import": '<path d="M12 3v12m0 0l-4-4m4 4l4-4"/><path d="M4 17v3h16v-3"/>',
    "export": '<path d="M12 15V3m0 0l-4 4m4-4l4 4"/><path d="M4 17v3h16v-3"/>',
    "undo": '<path d="M9 14L4 9l5-5"/><path d="M4 9h10a6 6 0 010 12h-3"/>',
    "redo": '<path d="M15 14l5-5-5-5"/><path d="M20 9H10a6 6 0 000 12h3"/>',
    "compare": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M12 4v16"/><path d="M3 6a2 2 0 012-2h7v16H5a2 2 0 01-2-2z" fill="currentColor" fill-opacity=".3" stroke="none"/>',
    "auto": '<path d="M11 3l1.9 4.9L18 9.8l-5.1 1.9L11 16.6l-1.9-4.9L4 9.8l5.1-1.9z"/><path d="M19 14l.8 2.2 2.2.8-2.2.8-.8 2.2-.8-2.2-2.2-.8 2.2-.8z"/>',
    "batch": '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/>',
    "reset": '<path d="M3 12a9 9 0 109-9 9 9 0 00-6.4 2.6L3 8"/><path d="M3 3v5h5"/>',
    "crop": '<path d="M6 2v14a2 2 0 002 2h14"/><path d="M18 22V8a2 2 0 00-2-2H2"/>',
    "rotate_left": '<path d="M3 12a9 9 0 109-9 9 9 0 00-6.4 2.6"/><path d="M3 4v5h5"/>',
    "rotate_right": '<path d="M21 12a9 9 0 11-9-9 9 9 0 016.4 2.6"/><path d="M21 4v5h-5"/>',
    "flip_h": '<path d="M12 3v18"/><path d="M8 7L3 12l5 5z"/><path d="M16 7l5 5-5 5z"/>',
    "flip_v": '<g transform="rotate(90 12 12)"><path d="M12 3v18"/><path d="M8 7L3 12l5 5z"/><path d="M16 7l5 5-5 5z"/></g>',
    "focus": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M15 4v16"/>',
    "clip": '<path d="M12 3.5l9.5 16.5h-19z"/><path d="M12 10v4"/><path d="M12 17h.01"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "folder": '<path d="M3 7a2 2 0 012-2h4l2 2h8a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>',
    "save": '<path d="M5 3h11l3 3v15H5z"/><path d="M8 3v5h7V3"/><path d="M8 21v-7h8v7"/>',
    "star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
}


@lru_cache(maxsize=256)
def _pixmap(name: str, color: str, size: int) -> QPixmap:
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{PATHS[name].replace("currentColor", color)}</svg>'
    r = QSvgRenderer(QByteArray(svg.encode()))
    scale = 2  # рисуем вдвое крупнее для чёткости на экранах с масштабом
    img = QImage(size * scale, size * scale, QImage.Format_ARGB32_Premultiplied)
    img.fill(Qt.transparent)
    p = QPainter(img)
    r.render(p)
    p.end()
    pm = QPixmap.fromImage(img)
    pm.setDevicePixelRatio(scale)
    return pm


@lru_cache(maxsize=64)
def icon(name: str, size: int = 18, color: str = TEXT, checked_color: str = "#ffffff", disabled_color: str = "#5c5c64") -> QIcon:
    """Значок для кнопки: обычный, выключенный и нажатый (для переключателей) вид."""
    ic = QIcon()
    ic.addPixmap(_pixmap(name, color, size), QIcon.Normal, QIcon.Off)
    ic.addPixmap(_pixmap(name, checked_color, size), QIcon.Normal, QIcon.On)
    ic.addPixmap(_pixmap(name, disabled_color, size), QIcon.Disabled, QIcon.Off)
    return ic
