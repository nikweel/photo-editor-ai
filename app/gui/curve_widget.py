import bisect

import numpy as np
from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPolygonF
from PySide6.QtWidgets import QWidget

from ..core.adjust import IDENTITY_CURVE, curve_lut

COLORS = {"rgb": "#dddddd", "r": "#ff5555", "g": "#55dd55", "b": "#5599ff"}
MIN_GAP = 0.01   # точки не сближаются и не перескакивают друг через друга
HIT = 9          # радиус захвата точки, px
PRESETS = {
    "Линейная": [[0.0, 0.0], [1.0, 1.0]],
    "Лёгкий контраст": [[0.0, 0.0], [0.25, 0.20], [0.75, 0.80], [1.0, 1.0]],
    "Сильный контраст": [[0.0, 0.0], [0.25, 0.14], [0.75, 0.86], [1.0, 1.0]],
    "Светлее": [[0.0, 0.0], [0.5, 0.65], [1.0, 1.0]],
    "Темнее": [[0.0, 0.0], [0.5, 0.35], [1.0, 1.0]],
    "Негатив": [[0.0, 1.0], [1.0, 0.0]],
}


class CurveWidget(QWidget):
    """Кривая как в Photoshop: клик в любом месте кривой создаёт точку и сразу её тянет; Ctrl+клик или правый клик по точке
    и клавиша Delete удаляют; стрелки сдвигают выбранную точку (Shift — крупнее); крайние точки двигаются и по X (чёрная/белая точка)."""
    changed = Signal()

    def __init__(self):
        super().__init__()
        self.setFixedSize(236, 236)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.curves: dict[str, list[list[float]]] = {}
        self.channel = "rgb"
        self.sel = -1
        self.drag = False
        self.hover: tuple[float, float] | None = None
        self.hist: dict[str, np.ndarray] = {}

    # ---------- данные ----------
    def set_curves(self, curves: dict):
        self.curves, self.sel = curves, -1
        self.update()

    def set_channel(self, ch: str):
        self.channel, self.sel = ch, -1
        self.update()

    def set_histogram(self, img: np.ndarray | None):
        """Гистограммы изображения под кривой (яркость и три канала)."""
        self.hist = {}
        if img is not None:
            lum = img @ np.array([0.2126, 0.7152, 0.0722], np.float32)
            for k, ch in (("rgb", lum), ("r", img[..., 0]), ("g", img[..., 1]), ("b", img[..., 2])):
                h = np.histogram(ch, bins=64, range=(0, 1))[0].astype(np.float32)
                self.hist[k] = h / max(h.max(), 1)
        self.update()

    def apply_preset(self, name: str):
        self.curves[self.channel] = [p[:] for p in PRESETS.get(name, IDENTITY_CURVE)]
        self.sel = -1
        self.update()
        self.changed.emit()

    def reset_channel(self):
        self.apply_preset("Линейная")

    @property
    def pts(self) -> list[list[float]]:
        return self.curves.setdefault(self.channel, [p[:] for p in IDENTITY_CURVE])

    # ---------- геометрия ----------
    def _box(self) -> QRectF:
        return QRectF(8, 8, self.width() - 16, self.height() - 16)

    def _px(self, x, y) -> QPointF:
        b = self._box()
        return QPointF(b.left() + x * b.width(), b.bottom() - y * b.height())

    def _val(self, pos) -> tuple[float, float]:
        b = self._box()
        return min(max((pos.x() - b.left()) / b.width(), 0), 1), min(max((b.bottom() - pos.y()) / b.height(), 0), 1)

    def _hit(self, pos) -> int:
        best, bd = -1, HIT + 1
        for i, (x, y) in enumerate(self.pts):
            d = (self._px(x, y) - pos).manhattanLength() / 1.4
            if d < bd:
                best, bd = i, d
        return best

    def _y_at(self, x: float) -> float:
        return float(np.interp(x, np.linspace(0, 1, 512), curve_lut(self.pts, 512)))

    # ---------- рисование ----------
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        b = self._box()
        p.fillRect(b, QColor("#1e1e1e"))
        h = self.hist.get(self.channel)
        if h is not None:  # гистограмма снимка — ориентир для точек
            poly = QPolygonF([QPointF(b.left(), b.bottom())] + [QPointF(b.left() + b.width() * (i + 0.5) / len(h), b.bottom() - b.height() * 0.9 * v)
                                                                  for i, v in enumerate(h)] + [QPointF(b.right(), b.bottom())])
            c = QColor(COLORS[self.channel])
            c.setAlpha(60)
            p.setPen(Qt.NoPen)
            p.setBrush(c)
            p.drawPolygon(poly)
        p.setPen(QPen(QColor("#3a3a3a"), 1))
        for i in range(1, 4):
            p.drawLine(QPointF(b.left() + b.width() * i / 4, b.top()), QPointF(b.left() + b.width() * i / 4, b.bottom()))
            p.drawLine(QPointF(b.left(), b.top() + b.height() * i / 4), QPointF(b.right(), b.top() + b.height() * i / 4))
        p.setPen(QPen(QColor("#555555"), 1, Qt.DashLine))
        p.drawLine(self._px(0, 0), self._px(1, 1))
        pts = self.pts
        lut = curve_lut(pts, 160)
        path = QPainterPath(self._px(0, lut[0]))
        for i in range(1, len(lut)):
            path.lineTo(self._px(i / (len(lut) - 1), lut[i]))
        col = QColor(COLORS[self.channel])
        p.setPen(QPen(col, 2))
        p.setBrush(Qt.NoBrush)
        p.drawPath(path)
        for i, (x, y) in enumerate(pts):
            on = i == self.sel
            p.setPen(QPen(QColor("#ffffff") if on else QColor("#222222"), 1.5))
            p.setBrush(QColor("#ffffff") if on else col)
            p.drawEllipse(self._px(x, y), 5.5 if on else 4.5, 5.5 if on else 4.5)
        # подпись «вход → выход» для выбранной точки или под курсором
        v = pts[self.sel] if 0 <= self.sel < len(pts) else (self.hover[0], self._y_at(self.hover[0])) if self.hover else None
        if v:
            p.setPen(QColor("#bbbbbb"))
            p.drawText(QPointF(b.left() + 6, b.top() + 14), f"Вход {round(v[0] * 255)}  →  Выход {round(v[1] * 255)}")

    # ---------- мышь ----------
    def _remove(self, i: int) -> bool:
        if 0 < i < len(self.pts) - 1:  # крайние точки удалять нельзя
            del self.pts[i]
            self.sel = -1
            return True
        return False

    def mousePressEvent(self, e):
        self.setFocus()
        i = self._hit(e.position())
        if e.button() == Qt.RightButton or (e.button() == Qt.LeftButton and e.modifiers() & Qt.ControlModifier):
            if i >= 0 and self._remove(i):
                self.update()
                self.changed.emit()
            return
        if e.button() != Qt.LeftButton:
            return
        if i < 0:  # клик в любом месте: новая точка на кривой в этом X, дальше тянем её за мышью
            x, _ = self._val(e.position())
            pts = self.pts
            if any(abs(x - q[0]) < MIN_GAP for q in pts):
                return
            i = bisect.bisect([q[0] for q in pts], x)
            pts.insert(i, [x, self._y_at(x)])
            self.changed.emit()
        self.sel, self.drag = i, True
        self._move(e.position())

    def _move(self, pos):
        pts, i = self.pts, self.sel
        x, y = self._val(pos)
        lo = pts[i - 1][0] + MIN_GAP if i > 0 else 0.0
        hi = pts[i + 1][0] - MIN_GAP if i < len(pts) - 1 else 1.0
        pts[i] = [min(max(x, lo), hi), y]
        self.update()
        self.changed.emit()

    def mouseMoveEvent(self, e):
        self.hover = self._val(e.position())
        if self.drag and self.sel >= 0:
            self._move(e.position())
        else:
            self.setCursor(Qt.PointingHandCursor if self._hit(e.position()) >= 0 else Qt.CrossCursor)
            self.update()

    def mouseReleaseEvent(self, _):
        self.drag = False

    def leaveEvent(self, _):
        self.hover = None
        self.update()

    # ---------- клавиатура ----------
    def keyPressEvent(self, e):
        if self.sel < 0:
            return super().keyPressEvent(e)
        if e.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            if self._remove(self.sel):
                self.update()
                self.changed.emit()
            return
        step = (10 if e.modifiers() & Qt.ShiftModifier else 1) / 255
        dx, dy = {Qt.Key_Left: (-step, 0), Qt.Key_Right: (step, 0), Qt.Key_Up: (0, step), Qt.Key_Down: (0, -step)}.get(e.key(), (None, None))
        if dx is None:
            return super().keyPressEvent(e)
        pts, i = self.pts, self.sel
        lo = pts[i - 1][0] + MIN_GAP if i > 0 else 0.0
        hi = pts[i + 1][0] - MIN_GAP if i < len(pts) - 1 else 1.0
        pts[i] = [min(max(pts[i][0] + dx, lo), hi), min(max(pts[i][1] + dy, 0), 1)]
        self.update()
        self.changed.emit()
