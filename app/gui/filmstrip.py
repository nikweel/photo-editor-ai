from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QListView, QListWidget, QListWidgetItem, QMenu

from .thumbs import ThumbWorker


class Filmstrip(QListWidget):
    """Лента снимков внизу окна: выбор, рейтинг (клавиши 0-5), удаление из каталога (Delete), контекстное меню."""
    selected = Signal(str)
    remove_requested = Signal(str)
    rating_changed = Signal(str, int)
    copy_requested = Signal(str)
    paste_requested = Signal()
    sync_requested = Signal()
    reveal_requested = Signal(str)

    def __init__(self):
        super().__init__()
        self.setViewMode(QListView.IconMode)
        self.setFlow(QListView.LeftToRight)
        self.setWrapping(False)
        self.setMovement(QListView.Static)
        self.setIconSize(QSize(120, 90))
        self.setFixedHeight(142)
        self.setHorizontalScrollMode(QListWidget.ScrollPerPixel)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSpacing(4)
        self.items: dict[str, QListWidgetItem] = {}
        self.ratings: dict[str, int] = {}
        self.worker: ThumbWorker | None = None
        self.currentItemChanged.connect(lambda cur, _: cur and self.selected.emit(cur.data(Qt.UserRole)))

    @staticmethod
    def _text(name: str, rating: int) -> str:
        stars = "★" * rating + " " if rating else ""
        room = 17 - len(stars)  # одна строка: в режиме значков многострочный текст обрезается до «…»
        return stars + (name if len(name) <= room else name[:room - 1] + "…")

    def add_paths(self, paths: list[Path], ratings: dict[str, int] | None = None):
        new = []
        for p in paths:
            if str(p) in self.items:
                continue
            r = (ratings or {}).get(str(p), 0)
            it = QListWidgetItem(self._text(p.name, r))
            it.setData(Qt.UserRole, str(p))
            it.setToolTip(str(p))
            it.setSizeHint(QSize(130, 124))
            self.ratings[str(p)] = r
            self.addItem(it)
            self.items[str(p)] = it
            new.append(p)
        prev = self.worker
        if prev and prev.isRunning():  # дождёмся предыдущей очереди, потом новая
            prev.finished.connect(lambda: self._thumbs(new))
        else:
            self._thumbs(new)

    def _thumbs(self, paths: list[Path]):
        if not paths:
            return
        self.worker = ThumbWorker(paths)
        self.worker.ready.connect(lambda p, t: self.items[p].setIcon(QIcon(t)) if p in self.items else None)
        self.worker.start()

    def select_path(self, path: Path):
        it = self.items.get(str(path))
        if it:
            self.blockSignals(True)
            self.setCurrentItem(it)
            self.blockSignals(False)

    def remove_path(self, path: str):
        it = self.items.pop(path, None)
        self.ratings.pop(path, None)
        if it:
            self.blockSignals(True)
            self.takeItem(self.row(it))
            self.blockSignals(False)

    def set_rating(self, path: str, n: int):
        self.ratings[path] = n
        if path in self.items:
            self.items[path].setText(self._text(Path(path).name, n))

    def neighbour(self, step: int) -> str | None:
        row = self.currentRow() + step
        return self.item(row).data(Qt.UserRole) if 0 <= row < self.count() else None

    def keyPressEvent(self, e):
        it = self.currentItem()
        if it and e.key() == Qt.Key_Delete:
            self.remove_requested.emit(it.data(Qt.UserRole))
        elif it and Qt.Key_0 <= e.key() <= Qt.Key_5 and not e.modifiers():
            self.rating_changed.emit(it.data(Qt.UserRole), e.key() - Qt.Key_0)
        else:
            super().keyPressEvent(e)

    def contextMenuEvent(self, e):
        it = self.itemAt(e.pos())
        m = QMenu(self)
        if it:
            path = it.data(Qt.UserRole)
            self.setCurrentItem(it)
            stars = m.addMenu("Рейтинг")
            for n in range(6):
                stars.addAction("Без оценки" if n == 0 else "★" * n).triggered.connect(lambda _=False, n=n: self.rating_changed.emit(path, n))
            m.addAction("Копировать настройки").triggered.connect(lambda: self.copy_requested.emit(path))
            m.addAction("Вставить настройки").triggered.connect(self.paste_requested.emit)
            m.addAction("Применить текущие настройки ко всем").triggered.connect(self.sync_requested.emit)
            m.addSeparator()
            m.addAction("Показать в папке").triggered.connect(lambda: self.reveal_requested.emit(path))
            m.addAction("Убрать из каталога  (Del)").triggered.connect(lambda: self.remove_requested.emit(path))
            m.exec(e.globalPos())

    def shutdown(self):
        if self.worker and self.worker.isRunning():
            self.worker.requestInterruption()
            self.worker.wait(3000)
