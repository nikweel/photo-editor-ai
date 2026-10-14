from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (QComboBox, QDialog, QFileDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget,
                               QCheckBox, QMessageBox, QProgressBar, QPushButton, QSlider, QSpinBox, QVBoxLayout)

from ..ai.registry import Engine
from ..services.batch import BatchOptions, collect_files, run_batch


class BatchWorker(QThread):
    progress = Signal(int, int, str)
    done = Signal(int, list)
    failed = Signal(str)

    def __init__(self, files, model_id, opts):
        super().__init__()
        self.files, self.model_id, self.opts = files, model_id, opts

    def run(self):
        try:
            engine = Engine(self.model_id)
            ok, errs = run_batch(self.files, engine, self.opts, self.progress.emit, self.isInterruptionRequested)
            self.done.emit(ok, errs)
        except Exception as e:
            self.failed.emit(str(e))


class BatchDialog(QDialog):
    def __init__(self, parent, model_id: str, params=None):
        super().__init__(parent)
        self.setWindowTitle("Пакетная обработка")
        self.resize(560, 560)
        self.model_id, self.files, self.worker, self.params = model_id, [], None, params
        self.use_params = QCheckBox("Применить ручные настройки открытого фото")
        self.use_params.setEnabled(params is not None)
        self.list = QListWidget()
        add_f = QPushButton("Добавить файлы…")
        add_d = QPushButton("Добавить папку…")
        clr = QPushButton("Очистить")
        add_f.clicked.connect(self._add_files)
        add_d.clicked.connect(self._add_dir)
        clr.clicked.connect(lambda: (self.files.clear(), self._refresh()))
        row = QHBoxLayout()
        for b in (add_f, add_d, clr):
            row.addWidget(b)
        self.out = QLineEdit(str(Path.home() / "Pictures" / "PhotoEditorAI"))
        pick = QPushButton("…")
        pick.clicked.connect(self._pick_out)
        orow = QHBoxLayout()
        orow.addWidget(self.out)
        orow.addWidget(pick)
        self.fmt = QComboBox()
        self.fmt.addItems(["jpg", "png", "webp", "tif"])
        self.quality = QSpinBox()
        self.quality.setRange(50, 100)
        self.quality.setValue(95)
        self.auto = QComboBox()
        self.auto.addItems(["Экспозиция и цвет", "Только экспозиция", "Без ИИ"])
        self.side = QSpinBox()
        self.side.setRange(0, 20000)
        self.side.setSingleStep(100)
        self.side.setSpecialValueText("исходный")
        self.side.setSuffix(" px")
        self.exif = QCheckBox("Сохранить EXIF")
        self.exif.setChecked(True)
        self.strength = QSlider(Qt.Horizontal)
        self.strength.setRange(0, 100)
        self.strength.setValue(100)
        self.contrast = QSlider(Qt.Horizontal)
        self.contrast.setRange(-100, 100)
        form = QFormLayout()
        form.addRow("Папка результата", orow)
        form.addRow("Формат", self.fmt)
        form.addRow("Качество (JPEG, WebP)", self.quality)
        form.addRow("Длинная сторона", self.side)
        form.addRow(self.exif)
        form.addRow("Автокоррекция ИИ", self.auto)
        form.addRow("Сила ИИ-коррекции", self.strength)
        form.addRow("Контраст", self.contrast)
        form.addRow(self.use_params)
        self.bar = QProgressBar()
        self.info = QLabel(f"Модель: {model_id}")
        self.start = QPushButton("Запустить")
        self.start.clicked.connect(self._toggle)
        lay = QVBoxLayout(self)
        for w in (self.list, row, form, self.bar, self.info, self.start):
            lay.addLayout(w) if hasattr(w, "addWidget") else lay.addWidget(w)
        self._refresh()

    def _refresh(self):
        self.list.clear()
        self.list.addItems(str(f) for f in self.files)
        self.info.setText(f"Файлов: {len(self.files)}")

    def _add(self, paths):
        seen = set(self.files)
        self.files += [f for f in collect_files(paths) if f not in seen]
        self._refresh()

    def _add_files(self):
        fs, _ = QFileDialog.getOpenFileNames(self, "Выберите фото")
        self._add([Path(f) for f in fs])

    def _add_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if d:
            self._add([Path(d)])

    def _pick_out(self):
        d = QFileDialog.getExistingDirectory(self, "Папка результата")
        if d:
            self.out.setText(d)

    def _toggle(self):
        if self.worker and self.worker.isRunning():
            self.worker.requestInterruption()
            self.start.setEnabled(False)
            return
        if not self.files:
            QMessageBox.information(self, "Пакет", "Добавьте фото.")
            return
        o = BatchOptions(Path(self.out.text()), self.fmt.currentText(), self.quality.value(), self.side.value(), self.exif.isChecked(),
                         self.strength.value() / 100, ("full", "exposure", "")[self.auto.currentIndex()], self.contrast.value() / 100,
                         self.params if self.use_params.isChecked() else None)
        self.worker = BatchWorker(list(self.files), self.model_id, o)
        self.worker.progress.connect(lambda d, t, n: (self.bar.setMaximum(t), self.bar.setValue(d), self.info.setText(f"{d}/{t} {n}")))
        self.worker.done.connect(self._done)
        self.worker.failed.connect(self._failed)
        self.start.setText("Остановить")
        self.worker.start()

    def _finish(self):
        self.start.setText("Запустить")
        self.start.setEnabled(True)

    def _done(self, ok, errs):
        self._finish()
        self.info.setText(f"Готово: {ok}, ошибок: {len(errs)}")

    def _failed(self, msg):
        self._finish()
        QMessageBox.warning(self, "Ошибка", msg)
