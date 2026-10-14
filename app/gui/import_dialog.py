from pathlib import Path

from PySide6.QtCore import QSize, Qt, QThread, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QListView,
                               QListWidget, QListWidgetItem, QMessageBox, QProgressBar, QPushButton, QVBoxLayout)

from ..services.batch import collect_files
from ..services.library import import_files
from .thumbs import ThumbWorker


class ImportWorker(QThread):
    progress = Signal(int, int)
    done = Signal(list)

    def __init__(self, files, dest, by_date):
        super().__init__()
        self.files, self.dest, self.by_date = files, dest, by_date

    def run(self):
        self.done.emit(import_files(self.files, self.dest, self.by_date, self.progress.emit, self.isInterruptionRequested))


class ImportDialog(QDialog):
    """Импорт как в Lightroom: источник -> миниатюры с галочками -> добавить на месте или копировать."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Импорт фотографий")
        self.resize(820, 620)
        self.imported: list[Path] = []
        self.thumbs: ThumbWorker | None = None
        self.worker: ImportWorker | None = None
        self.grid = QListWidget()
        self.grid.setViewMode(QListView.IconMode)
        self.grid.setIconSize(QSize(120, 90))
        self.grid.setResizeMode(QListWidget.Adjust)
        self.grid.setMovement(QListView.Static)
        self.grid.setSpacing(6)
        self.items: dict[str, QListWidgetItem] = {}
        src_f, src_d = QPushButton("Файлы…"), QPushButton("Папка…")
        src_f.clicked.connect(self._files)
        src_d.clicked.connect(self._folder)
        all_, none = QPushButton("Выбрать все"), QPushButton("Снять выбор")
        all_.clicked.connect(lambda: self._check_all(Qt.Checked))
        none.clicked.connect(lambda: self._check_all(Qt.Unchecked))
        top = QHBoxLayout()
        for w in (QLabel("Источник:"), src_f, src_d, all_, none):
            top.addWidget(w)
        top.addStretch()
        self.mode = QComboBox()
        self.mode.addItems(["Добавить на месте", "Копировать в папку"])
        self.mode.currentIndexChanged.connect(self._mode)
        self.dest = QLineEdit(str(Path.home() / "Pictures" / "PhotoEditorAI" / "Import"))
        self.pick = QPushButton("…")
        self.pick.clicked.connect(self._dest)
        self.by_date = QCheckBox("Раскладывать по папкам-датам")
        self.by_date.setChecked(True)
        mid = QHBoxLayout()
        for w in (QLabel("Режим:"), self.mode, self.dest, self.pick, self.by_date):
            mid.addWidget(w)
        self.bar = QProgressBar()
        self.info = QLabel("Выберите источник")
        self.go = QPushButton("Импортировать")
        self.go.clicked.connect(self._import)
        lay = QVBoxLayout(self)
        lay.addLayout(top)
        lay.addWidget(self.grid, 1)
        lay.addLayout(mid)
        lay.addWidget(self.bar)
        lay.addWidget(self.info)
        lay.addWidget(self.go)
        self._mode()

    def _mode(self):
        copy = self.mode.currentIndex() == 1
        for w in (self.dest, self.pick, self.by_date):
            w.setEnabled(copy)

    def _dest(self):
        d = QFileDialog.getExistingDirectory(self, "Куда копировать")
        if d:
            self.dest.setText(d)

    def _files(self):
        fs, _ = QFileDialog.getOpenFileNames(self, "Выберите фото")
        self._add([Path(f) for f in fs])

    def _folder(self):
        d = QFileDialog.getExistingDirectory(self, "Выберите папку с фото")
        if d:
            self._add([Path(d)])

    def _add(self, paths):
        new = [f for f in collect_files(paths) if str(f) not in self.items]
        for f in new:
            it = QListWidgetItem(f.name[:18])
            it.setFlags(it.flags() | Qt.ItemIsUserCheckable)
            it.setCheckState(Qt.Checked)
            it.setData(Qt.UserRole, str(f))
            it.setSizeHint(QSize(136, 118))
            self.grid.addItem(it)
            self.items[str(f)] = it
        self.info.setText(f"Найдено фото: {len(self.items)}")
        if self.thumbs and self.thumbs.isRunning():
            self.thumbs.requestInterruption()
            self.thumbs.wait(3000)
        self.thumbs = ThumbWorker(new)
        self.thumbs.ready.connect(lambda p, t: self.items[p].setIcon(QIcon(t)))
        self.thumbs.start()

    def _check_all(self, st):
        for it in self.items.values():
            it.setCheckState(st)

    def _import(self):
        files = [Path(p) for p, it in self.items.items() if it.checkState() == Qt.Checked]
        if not files:
            QMessageBox.information(self, "Импорт", "Нет выбранных фото.")
            return
        dest = Path(self.dest.text()) if self.mode.currentIndex() == 1 else None
        self.go.setEnabled(False)
        self.worker = ImportWorker(files, dest, self.by_date.isChecked())
        self.worker.progress.connect(lambda d, t: (self.bar.setMaximum(t), self.bar.setValue(d)))
        self.worker.done.connect(self._done)
        self.worker.start()

    def _done(self, paths):
        self.imported = paths
        self.accept()

    def done(self, r):
        for w in (self.thumbs, self.worker):
            if w and w.isRunning():
                w.requestInterruption()
                w.wait(3000)
        super().done(r)
