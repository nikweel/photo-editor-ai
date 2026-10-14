from PySide6.QtWidgets import QComboBox, QDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

from ..services.filters import CATEGORIES, DEFAULT_CATEGORY, MY_PACK


class SaveFilterDialog(QDialog):
    """Название фильтра, пакет (свой существующий или новый) и тип."""

    def __init__(self, parent, pack_names: list[str], default_pack: str = MY_PACK, default_category: str = DEFAULT_CATEGORY, default_name: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Сохранить как фильтр")
        self.setMinimumWidth(420)
        self.name = QLineEdit(default_name)
        self.name.setPlaceholderText("Название фильтра")
        self.pack = QComboBox()
        self.pack.setEditable(True)
        self.pack.addItems(pack_names)
        self.pack.setCurrentText(default_pack if default_pack in pack_names else MY_PACK)
        self.pack.setToolTip("Выберите свой пакет или впишите название нового — пакет создастся сам")
        self.category = QComboBox()
        self.category.setEditable(True)
        self.category.addItems([*CATEGORIES, DEFAULT_CATEGORY])
        self.category.setCurrentText(default_category)
        self.category.setToolTip("Тип нужен для группировки «По типам»; можно вписать свой")
        form = QFormLayout()
        form.addRow("Название", self.name)
        form.addRow("Пакет", self.pack)
        form.addRow("Тип", self.category)
        hint = QLabel("Встроенные пакеты изменять нельзя. Фильтр можно поделиться: «Экспорт…» сохранит его или весь пакет одним файлом.")
        hint.setWordWrap(True)
        hint.setProperty("muted", True)
        ok, cancel = QPushButton("Сохранить"), QPushButton("Отмена")
        ok.setProperty("primary", True)
        ok.clicked.connect(self._accept)
        cancel.clicked.connect(self.reject)
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(cancel)
        row.addWidget(ok)
        lay = QVBoxLayout(self)
        lay.addLayout(form)
        lay.addWidget(hint)
        lay.addLayout(row)

    def _accept(self):
        if self.name.text().strip():
            self.accept()
        else:
            self.name.setFocus()

    def values(self) -> tuple[str, str, str]:
        return (self.name.text().strip(), self.pack.currentText().strip() or MY_PACK, self.category.currentText().strip() or DEFAULT_CATEGORY)
