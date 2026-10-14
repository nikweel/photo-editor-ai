from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QImage, QPainter, QPen
from PySide6.QtWidgets import QWidget

from .theme import CANVAS, MUTED

GRAB = 14        # px вокруг линии сравнения, где курсор меняется на «разделитель»
HANDLE = 10      # px, зона захвата ручки кадрирования
MIN_CROP = 0.04  # минимальный размер рамки в долях кадра
MAX_ZOOM = 16.0
CURSORS = {"tl": Qt.SizeFDiagCursor, "br": Qt.SizeFDiagCursor, "tr": Qt.SizeBDiagCursor, "bl": Qt.SizeBDiagCursor,
           "l": Qt.SizeHorCursor, "r": Qt.SizeHorCursor, "t": Qt.SizeVerCursor, "b": Qt.SizeVerCursor, "move": Qt.SizeAllCursor}


class CompareCanvas(QWidget):
    """Показ фото: зум колесом, перемещение мышью, сравнение «до/после» с линией и режим кадрирования."""
    crop_changed = Signal(list)
    view_changed = Signal()

    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 300)
        self.setMouseTracking(True)
        self.message = ""
        self.before: QImage | None = None
        self.after: QImage | None = None
        self.source_width = 0          # ширина показанного кадра в пикселях оригинала (для процента зума)
        self.compare = False
        self.split = 0.5               # доля ширины изображения
        self.zoom = 1.0                # 1 = вписать в окно
        self.center = QPointF(0.5, 0.5)  # какая точка изображения (в долях) в центре окна
        self._drag: str | None = None  # "split" | "pan" | ручка кадрирования
        self._last = QPointF()
        self.crop_mode = False
        self.crop = [0.0, 0.0, 1.0, 1.0]
        self.crop_ratio: float | None = None  # w/h в пикселях; None — свободно

    # ---------- состояние ----------
    def set_message(self, text: str):
        self.message = text
        self.update()

    def set_pair(self, before: QImage, after: QImage):
        self.before, self.after = before, after
        self._clamp_center()  # размер кадра мог измениться (поворот, кадрирование)
        self.update()

    def set_compare(self, on: bool):
        self.compare = on and not self.crop_mode
        self.update()

    def percent(self) -> int:
        """Масштаб показа относительно пикселей оригинала."""
        if self.after is None or not self.source_width:
            return 100
        return round(self._scale() * self.after.width() / self.source_width * 100)

    def fit(self):
        self.zoom, self.center = 1.0, QPointF(0.5, 0.5)
        self.update()
        self.view_changed.emit()

    def zoom_100(self):
        if self.after is not None and self.source_width:
            fit = self._fit_scale()
            self._set_zoom(self.source_width / self.after.width() / fit, self.rect().center())

    # ---------- геометрия ----------
    def _fit_scale(self) -> float:
        return min(self.width() / self.after.width(), self.height() / self.after.height())

    def _scale(self) -> float:
        return self._fit_scale() * self.zoom

    def _clamp_center(self):
        if self.after is None:
            return
        s = self._scale()
        for axis, size, total in ((0, self.after.width(), self.width()), (1, self.after.height(), self.height())):
            half = total / 2 / (size * s)
            v = self.center.x() if axis == 0 else self.center.y()
            v = 0.5 if half >= 0.5 else min(max(v, half), 1 - half)
            self.center.setX(v) if axis == 0 else self.center.setY(v)

    def _rect(self) -> QRectF:
        if self.after is None:
            return QRectF()
        s = self._scale()
        w, h = self.after.width() * s, self.after.height() * s
        return QRectF(self.width() / 2 - self.center.x() * w, self.height() / 2 - self.center.y() * h, w, h)

    def _set_zoom(self, z: float, anchor: QPointF):
        """Масштаб вокруг точки anchor (в координатах окна): точка под курсором остаётся на месте."""
        if self.after is None:
            return
        r = self._rect()
        u = QPointF((anchor.x() - r.left()) / r.width(), (anchor.y() - r.top()) / r.height())
        self.zoom = min(max(z, 1.0), MAX_ZOOM)
        s = self._scale()
        w, h = self.after.width() * s, self.after.height() * s
        self.center = QPointF(u.x() - (anchor.x() - self.width() / 2) / w, u.y() - (anchor.y() - self.height() / 2) / h)
        self._clamp_center()
        self.update()
        self.view_changed.emit()

    def _draw(self, p: QPainter, img: QImage, r: QRectF, clip_x: float | None = None):
        """Рисует видимую часть img в прямоугольник r (без масштабирования всей картинки при большом зуме)."""
        vis = r.intersected(QRectF(self.rect()))
        if clip_x is not None:
            vis = vis.intersected(QRectF(-1e6, -1e6, clip_x + 1e6, 2e6))
        if vis.width() <= 0 or vis.height() <= 0:
            return
        k = img.width() / r.width()
        p.drawImage(vis, img, QRectF((vis.left() - r.left()) * k, (vis.top() - r.top()) * k, vis.width() * k, vis.height() * k))

    # ---------- рисование ----------
    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(CANVAS))
        if self.after is None:
            p.setPen(QColor(MUTED))
            p.drawText(self.rect(), Qt.AlignCenter, self.message)
            return
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        r = self._rect()
        self._draw(p, self.after, r)
        if self.crop_mode:
            self._paint_crop(p, r)
        elif self.compare:
            self._paint_compare(p, r)

    def _paint_compare(self, p: QPainter, r: QRectF):
        x = r.left() + r.width() * self.split
        self._draw(p, self.before, r, clip_x=x)
        if not 0 <= x <= self.width():
            return
        p.setRenderHint(QPainter.Antialiasing)
        top, bottom = max(r.top(), 0), min(r.bottom(), self.height())
        p.setPen(QPen(QColor(0, 0, 0, 120), 4))
        p.drawLine(QPointF(x, top), QPointF(x, bottom))
        p.setPen(QPen(QColor("#ffffff"), 2))
        p.drawLine(QPointF(x, top), QPointF(x, bottom))
        c = QPointF(x, (top + bottom) / 2)  # ручка со стрелками
        p.setBrush(QColor(255, 255, 255, 235))
        p.setPen(QPen(QColor(0, 0, 0, 150), 1))
        p.drawEllipse(c, 15, 15)
        p.setPen(QPen(QColor("#333333"), 2))
        for s in (-1, 1):
            p.drawLine(QPointF(x + s * 4, c.y() - 5), QPointF(x + s * 9, c.y()))
            p.drawLine(QPointF(x + s * 9, c.y()), QPointF(x + s * 4, c.y() + 5))
        vis = r.intersected(QRectF(self.rect()))
        for text, left in (("До", True), ("После", False)):
            tw = p.fontMetrics().horizontalAdvance(text) + 16
            box = QRectF(vis.left() + 8 if left else vis.right() - tw - 8, vis.top() + 8, tw, 22)
            if (left and box.right() < x - 4) or (not left and box.left() > x + 4):  # подпись видна, только если её сторона открыта
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(0, 0, 0, 150))
                p.drawRoundedRect(box, 4, 4)
                p.setPen(QColor("#ffffff"))
                p.drawText(box, Qt.AlignCenter, text)

    def _crop_px(self, r: QRectF) -> QRectF:
        x0, y0, x1, y1 = self.crop
        return QRectF(r.left() + x0 * r.width(), r.top() + y0 * r.height(), (x1 - x0) * r.width(), (y1 - y0) * r.height())

    def _paint_crop(self, p: QPainter, r: QRectF):
        c = self._crop_px(r)
        dim = QColor(0, 0, 0, 150)
        p.fillRect(QRectF(r.left(), r.top(), r.width(), c.top() - r.top()), dim)
        p.fillRect(QRectF(r.left(), c.bottom(), r.width(), r.bottom() - c.bottom()), dim)
        p.fillRect(QRectF(r.left(), c.top(), c.left() - r.left(), c.height()), dim)
        p.fillRect(QRectF(c.right(), c.top(), r.right() - c.right(), c.height()), dim)
        p.setPen(QPen(QColor(255, 255, 255, 90), 1))  # сетка третей
        for i in (1, 2):
            p.drawLine(QPointF(c.left() + c.width() * i / 3, c.top()), QPointF(c.left() + c.width() * i / 3, c.bottom()))
            p.drawLine(QPointF(c.left(), c.top() + c.height() * i / 3), QPointF(c.right(), c.top() + c.height() * i / 3))
        p.setPen(QPen(QColor("#ffffff"), 1.5))
        p.setBrush(Qt.NoBrush)
        p.drawRect(c)
        p.setBrush(QColor("#ffffff"))
        for name, pt in self._handles(c).items():
            p.drawRect(QRectF(pt.x() - 4, pt.y() - 4, 8, 8))
        info = f"{round((self.crop[2] - self.crop[0]) * self.source_width)} × {round((self.crop[3] - self.crop[1]) * self.source_width * self.after.height() / self.after.width())}"
        p.setPen(QColor("#ffffff"))
        p.drawText(QPointF(c.left() + 6, c.top() - 6 if c.top() > 24 else c.top() + 18), info)

    @staticmethod
    def _handles(c: QRectF) -> dict[str, QPointF]:
        return {"tl": c.topLeft(), "tr": c.topRight(), "bl": c.bottomLeft(), "br": c.bottomRight(),
                "t": QPointF(c.center().x(), c.top()), "b": QPointF(c.center().x(), c.bottom()),
                "l": QPointF(c.left(), c.center().y()), "r": QPointF(c.right(), c.center().y())}

    # ---------- кадрирование ----------
    def set_crop_mode(self, on: bool, crop: list | None = None):
        self.crop_mode = on
        if on:
            self.compare = False
            self.fit()
            self.crop = list(crop) if crop else [0.0, 0.0, 1.0, 1.0]
        self.setCursor(Qt.ArrowCursor)
        self.update()

    def set_crop_ratio(self, ratio: float | None):
        """Новая пропорция: рамка вписывается вокруг своего центра, но не выходит за кадр."""
        self.crop_ratio = ratio
        if ratio and self.after is not None:
            x0, y0, x1, y1 = self.crop
            k = ratio * self.after.height() / self.after.width()  # ширина доли = k * высота доли
            cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
            if w / h > k:
                w = h * k
            else:
                h = w / k
            w, h = min(w, 1.0), min(h, 1.0)
            if w / h > k + 1e-6:
                w = h * k
            self.crop = self._fit_box(cx, cy, w, h)
            self.crop_changed.emit(self.crop)
        self.update()

    @staticmethod
    def _span(center: float, size: float) -> tuple[float, float]:
        """Отрезок заданной длины вокруг центра, сдвинутый внутрь кадра, если выходит за край."""
        lo = min(max(center - size / 2, 0.0), 1.0 - size)
        return lo, lo + size

    def _fit_box(self, cx, cy, w, h) -> list:
        (x0, x1), (y0, y1) = self._span(cx, w), self._span(cy, h)
        return [x0, y0, x1, y1]

    def _hit_crop(self, pos: QPointF) -> str | None:
        c = self._crop_px(self._rect())
        for name, pt in self._handles(c).items():
            if abs(pt.x() - pos.x()) <= HANDLE and abs(pt.y() - pos.y()) <= HANDLE:
                return name
        return "move" if c.contains(pos) else None

    def _resize_crop(self, handle: str, nx: float, ny: float):
        x0, y0, x1, y1 = self.crop
        nx, ny = min(max(nx, 0.0), 1.0), min(max(ny, 0.0), 1.0)
        if "l" in handle:
            x0 = min(nx, x1 - MIN_CROP)
        if "r" in handle:
            x1 = max(nx, x0 + MIN_CROP)
        if "t" in handle:
            y0 = min(ny, y1 - MIN_CROP)
        if "b" in handle:
            y1 = max(ny, y0 + MIN_CROP)
        if self.crop_ratio:
            k = self.crop_ratio * self.after.height() / self.after.width()  # ширина доли = k * высота доли
            w, h = x1 - x0, y1 - y0
            if len(handle) == 2:  # угол: противоположный остаётся на месте, ведущая — ширина
                h = w / k
                h = min(h, y1 if "t" in handle else 1 - y0)  # упёрлись в край кадра
                w = h * k
                x0, x1 = (x1 - w, x1) if "l" in handle else (x0, x0 + w)
                y0, y1 = (y1 - h, y1) if "t" in handle else (y0, y0 + h)
            elif handle in ("l", "r"):  # боковое ребро: высота подстраивается вокруг центра
                h = min(w / k, 1.0)
                w = h * k
                x0, x1 = (x1 - w, x1) if handle == "l" else (x0, x0 + w)
                y0, y1 = self._span((y0 + y1) / 2, h)
            else:  # верх/низ: ширина подстраивается вокруг центра
                w = min(h * k, 1.0)
                h = w / k
                y0, y1 = (y1 - h, y1) if handle == "t" else (y0, y0 + h)
                x0, x1 = self._span((x0 + x1) / 2, w)
        self.crop = [max(x0, 0.0), max(y0, 0.0), min(x1, 1.0), min(y1, 1.0)]

    # ---------- мышь ----------
    def mousePressEvent(self, e):
        if self.after is None or e.button() != Qt.LeftButton:
            return
        pos = e.position()
        self._last = pos
        if self.crop_mode:
            self._drag = self._hit_crop(pos)
        elif self.compare and (self.zoom == 1.0 or abs(pos.x() - (self._rect().left() + self._rect().width() * self.split)) < GRAB):
            self._drag = "split"  # при зуме 1 хватаем где угодно: линия прыгает под курсор
            self._set_split(pos.x())
        elif self.zoom > 1.0:
            self._drag = "pan"
            self.setCursor(Qt.ClosedHandCursor)

    def _set_split(self, px: float):
        r = self._rect()
        if r.width() > 0:
            self.split = min(max((px - r.left()) / r.width(), 0.0), 1.0)
            self.update()

    def mouseMoveEvent(self, e):
        pos = e.position()
        r = self._rect() if self.after is not None else QRectF()
        if self._drag == "split":
            self._set_split(pos.x())
        elif self._drag == "pan":
            d = pos - self._last
            self._last = pos
            self.center = QPointF(self.center.x() - d.x() / r.width(), self.center.y() - d.y() / r.height())
            self._clamp_center()
            self.update()
            self.view_changed.emit()
        elif self._drag and self.crop_mode:
            nx, ny = (pos.x() - r.left()) / r.width(), (pos.y() - r.top()) / r.height()
            if self._drag == "move":
                dx, dy = (pos.x() - self._last.x()) / r.width(), (pos.y() - self._last.y()) / r.height()
                x0, y0, x1, y1 = self.crop
                dx, dy = min(max(dx, -x0), 1 - x1), min(max(dy, -y0), 1 - y1)
                self.crop = [x0 + dx, y0 + dy, x1 + dx, y1 + dy]
                self._last = pos
            else:
                self._resize_crop(self._drag, nx, ny)
            self.crop_changed.emit(self.crop)
            self.update()
        elif self.crop_mode:
            h = self._hit_crop(pos)
            self.setCursor(CURSORS.get(h, Qt.ArrowCursor))
        elif self.compare and self.after is not None:
            near = abs(pos.x() - (r.left() + r.width() * self.split)) < GRAB
            self.setCursor(Qt.SplitHCursor if near or self.zoom == 1.0 else (Qt.OpenHandCursor if self.zoom > 1 else Qt.ArrowCursor))
        elif self.zoom > 1.0:
            self.setCursor(Qt.OpenHandCursor)

    def mouseReleaseEvent(self, _):
        self._drag = None
        self.setCursor(Qt.OpenHandCursor if self.zoom > 1.0 and not self.crop_mode else Qt.ArrowCursor)

    def mouseDoubleClickEvent(self, e):
        if self.after is None or self.crop_mode or e.button() != Qt.LeftButton:
            return
        if self.zoom > 1.0:
            self.fit()
        else:
            self._set_zoom(max(self.source_width / self.after.width() / self._fit_scale(), 2.0) if self.source_width else 2.0, e.position())

    def wheelEvent(self, e):
        if self.after is None or self.crop_mode:
            return
        self._set_zoom(self.zoom * 1.0015 ** e.angleDelta().y(), e.position())

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._clamp_center()
