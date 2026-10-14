from dataclasses import asdict
from pathlib import Path

from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QFileDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QSlider, QSpinBox, QVBoxLayout)
from PySide6.QtCore import Qt

from ..services.export import FORMATS, ExportOptions
from ..utils import settings


class ExportDialog(QDialog):
    """Параметры экспорта: файл, формат, качество, размер, EXIF. Выбор запоминается."""

    def __init__(self, parent, default_path: Path):
        super().__init__(parent)
        self.setWindowTitle("Экспорт")
        self.setMinimumWidth(480)
        saved = settings.get("export", {})
        self.options = ExportOptions(**{k: v for k, v in saved.items() if k in asdict(ExportOptions())})
        last_dir = settings.get("export_dir", "")
        start = (Path(last_dir) / default_path.name) if last_dir and Path(last_dir).is_dir() else default_path
        self.path = QLineEdit(str(start.with_suffix("." + self.options.fmt)))
        browse = QPushButton("Обзор…")
        browse.clicked.connect(self._browse)
        prow = QHBoxLayout()
        prow.addWidget(self.path, 1)
        prow.addWidget(browse)
        self.fmt = QComboBox()
        for k, v in FORMATS.items():
            self.fmt.addItem(v, k)
        self.fmt.setCurrentIndex(self.fmt.findData(self.options.fmt))
        self.fmt.currentIndexChanged.connect(self._fmt_changed)
        self.quality = QSlider(Qt.Horizontal)
        self.quality.setRange(50, 100)
        self.quality.setValue(self.options.quality)
        self.q_val = QLabel(str(self.options.quality))
        self.quality.valueChanged.connect(lambda v: self.q_val.setText(str(v)))
        qrow = QHBoxLayout()
        qrow.addWidget(self.quality, 1)
        qrow.addWidget(self.q_val)
        self.resize_on = QCheckBox("Изменить размер")
        self.resize_on.setChecked(self.options.long_side > 0)
        self.side = QSpinBox()
        self.side.setRange(100, 20000)
        self.side.setSingleStep(100)
        self.side.setSuffix(" px по длинной стороне")
        self.side.setValue(self.options.long_side or 2048)
        self.side.setEnabled(self.resize_on.isChecked())
        self.resize_on.toggled.connect(self.side.setEnabled)
        self.exif = QCheckBox("Сохранить данные съёмки (EXIF)")
        self.exif.setChecked(self.options.keep_exif)
        form = QFormLayout()
        form.addRow("Файл", prow)
        form.addRow("Формат", self.fmt)
        form.addRow("Качество", qrow)
        form.addRow(self.resize_on, self.side)
        form.addRow(self.exif)
        ok, cancel = QPushButton("Экспортировать"), QPushButton("Отмена")
        ok.setProperty("primary", True)
        ok.clicked.connect(self._accept)
        cancel.clicked.connect(self.reject)
        brow = QHBoxLayout()
        brow.addStretch()
        brow.addWidget(cancel)
        brow.addWidget(ok)
        lay = QVBoxLayout(self)
        lay.addLayout(form)
        lay.addLayout(brow)
        self._fmt_changed()

    def _fmt_changed(self):
        f = self.fmt.currentData()
        self.quality.setEnabled(f in ("jpg", "webp"))  # PNG и TIFF — без потерь
        self.exif.setEnabled(f != "png")
        self.path.setText(str(Path(self.path.text()).with_suffix("." + f)))

    def _browse(self):
        f, _ = QFileDialog.getSaveFileName(self, "Куда сохранить", self.path.text())
        if f:
            self.path.setText(f)

    def _accept(self):
        self.options = ExportOptions(self.fmt.currentData(), self.quality.value(), self.side.value() if self.resize_on.isChecked() else 0,
                                     self.exif.isChecked())
        settings.put("export", asdict(self.options))
        settings.put("export_dir", str(Path(self.path.text()).parent))
        self.accept()

    @property
    def target(self) -> Path:
        return Path(self.path.text())
