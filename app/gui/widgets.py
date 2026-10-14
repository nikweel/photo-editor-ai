import numpy as np
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QFrame, QLabel, QSizePolicy, QSlider, QToolButton, QVBoxLayout, QWidget

from .theme import ACCENT, BG, BORDER

HANDLE = 14


class BipolarSlider(QSlider):
    """Ползунок вокруг нуля: цветная заливка идёт от середины к ручке, двойной клик сбрасывает в середину."""

    def __init__(self, lo: int, hi: int):
        super().__init__(Qt.Horizontal)
        self.setRange(lo, hi)
        self.setProperty("bipolar", True)
        self.setMinimumHeight(22)

    def mouseDoubleClickEvent(self, e):
        self.setValue((self.minimum() + self.maximum()) // 2)

    def _x(self, v: int) -> float:
        span = self.width() - HANDLE
        return HANDLE / 2 + span * (v - self.minimum()) / max(self.maximum() - self.minimum(), 1)

    def paintEvent(self, e):
        super().paintEvent(e)
        mid, x = self._x((self.minimum() + self.maximum()) // 2), self._x(self.value())
        if abs(x - mid) < 1:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(ACCENT))
        a, b = (mid, x - HANDLE / 2) if x > mid else (x + HANDLE / 2, mid)
        if b > a:
            p.drawRoundedRect(QRectF(a, self.height() / 2 - 2, b - a, 4), 2, 2)


class UniSlider(QSlider):
    """Обычный ползунок от минимума; двойной клик сбрасывает на минимум."""

    def __init__(self, lo: int, hi: int):
        super().__init__(Qt.Horizontal)
        self.setRange(lo, hi)
        self.setMinimumHeight(22)

    def mouseDoubleClickEvent(self, e):
        self.setValue(self.minimum())


class Section(QFrame):
    """Сворачиваемый раздел панели (как в Lightroom). Свёрнутый раздел занимает одну строку."""

    def __init__(self, title: str, expanded: bool = True):
        super().__init__()
        self.head = QToolButton()
        self.head.setText(title.upper())
        self.head.setCheckable(True)
        self.head.setChecked(expanded)
        self.head.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.head.setArrowType(Qt.DownArrow if expanded else Qt.RightArrow)
        self.head.setCursor(Qt.PointingHandCursor)
        self.head.setStyleSheet("QToolButton { border: none; color: #9a9aa4; font-size: 8pt; font-weight: 600; letter-spacing: 1px;"
                                " text-align: left; padding: 6px 2px; } QToolButton:hover { color: #e8e8ec; }")
        self.body = QWidget()
        self.body.setVisible(expanded)
        self.body_lay = QVBoxLayout(self.body)
        self.body_lay.setContentsMargins(2, 0, 2, 6)
        self.body_lay.setSpacing(2)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(self.head)
        lay.addWidget(self.body)
        self.head.toggled.connect(self._toggle)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)  # раздел не растёт сверх содержимого: свободное место уходит вниз

    def _toggle(self, on: bool):
        self.head.setArrowType(Qt.DownArrow if on else Qt.RightArrow)
        self.body.setVisible(on)

    def add(self, w):
        (self.body_lay.addLayout if hasattr(w, "addWidget") else self.body_lay.addWidget)(w)


class HistogramWidget(QWidget):
    """Гистограмма текущего результата: R, G, B наложены друг на друга."""

    def __init__(self):
        super().__init__()
        self.setFixedHeight(84)
        self.h: np.ndarray | None = None

    def set_image(self, img: np.ndarray | None):
        if img is None:
            self.h = None
        else:
            s = img[::4, ::4]
            self.h = np.stack([np.histogram(s[..., c], bins=96, range=(0, 1))[0] for c in range(3)]).astype(np.float32)
            self.h = np.sqrt(self.h)  # корень: редкие тона остаются видны рядом с пиками
            self.h /= max(float(self.h.max()), 1.0)
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        p.setPen(QPen(QColor(BORDER), 1))
        p.setBrush(QColor(BG))
        p.drawRoundedRect(r, 8, 8)
        if self.h is None:
            return
        inner = r.adjusted(4, 6, -4, -4)
        p.setCompositionMode(QPainter.CompositionMode_Plus)  # сложение цветов: где все три канала — серый/белый
        p.setPen(Qt.NoPen)
        for c, col in enumerate(("#d03030", "#30c050", "#3060e0")):
            path = QPainterPath(QPointF(inner.left(), inner.bottom()))
            n = self.h.shape[1]
            for i, v in enumerate(self.h[c]):
                path.lineTo(inner.left() + inner.width() * (i + 0.5) / n, inner.bottom() - inner.height() * float(v))
            path.lineTo(inner.right(), inner.bottom())
            p.setBrush(QColor(col))
            p.drawPath(path)
