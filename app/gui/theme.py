"""Тёмная тема для работы с фото: нейтральный тёмный фон не искажает восприятие цвета."""
from PySide6.QtGui import QColor, QPalette

BG, PANEL, SURFACE, BORDER = "#18181a", "#212124", "#2b2b30", "#3a3a40"
TEXT, MUTED, ACCENT, ACCENT_HI = "#e8e8ec", "#9a9aa4", "#4c8dff", "#6ea3ff"
CANVAS = "#121214"


def apply(app) -> None:
    app.setStyle("Fusion")
    p = QPalette()
    for role, c in ((QPalette.Window, PANEL), (QPalette.WindowText, TEXT), (QPalette.Base, BG), (QPalette.AlternateBase, SURFACE),
                    (QPalette.Text, TEXT), (QPalette.Button, SURFACE), (QPalette.ButtonText, TEXT), (QPalette.ToolTipBase, SURFACE),
                    (QPalette.ToolTipText, TEXT), (QPalette.Highlight, ACCENT), (QPalette.HighlightedText, "#ffffff"),
                    (QPalette.PlaceholderText, MUTED), (QPalette.Link, ACCENT_HI)):
        p.setColor(role, QColor(c))
    for role in (QPalette.WindowText, QPalette.Text, QPalette.ButtonText):
        p.setColor(QPalette.Disabled, role, QColor("#66666e"))
    app.setPalette(p)
    f = app.font()
    f.setPointSize(10)
    app.setFont(f)
    app.setStyleSheet(QSS)


QSS = f"""
QMainWindow, QDialog {{ background: {PANEL}; }}
QToolTip {{ background: {SURFACE}; color: {TEXT}; border: 1px solid {BORDER}; padding: 4px 6px; }}
QLabel[muted="true"] {{ color: {MUTED}; }}
QLabel[heading="true"] {{ color: {MUTED}; font-size: 8pt; font-weight: 600; letter-spacing: 1px; }}

QPushButton {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 6px; padding: 6px 12px; min-height: 18px; }}
QPushButton:hover {{ background: #35353b; border-color: #50505a; }}
QPushButton:pressed {{ background: #26262a; }}
QPushButton:checked {{ background: {ACCENT}; border-color: {ACCENT}; color: white; }}
QPushButton:disabled {{ color: #66666e; background: #232326; border-color: #2c2c30; }}
QPushButton[primary="true"] {{ background: {ACCENT}; border-color: {ACCENT}; color: white; font-weight: 600; }}
QPushButton[primary="true"]:hover {{ background: {ACCENT_HI}; border-color: {ACCENT_HI}; }}
QPushButton[primary="true"]:disabled {{ background: #2f3f5e; border-color: #2f3f5e; color: #8c97ad; }}
QPushButton[accent="true"] {{ background: transparent; border: 1px solid {ACCENT}; color: {ACCENT_HI}; font-weight: 600; }}
QPushButton[accent="true"]:hover {{ background: rgba(76, 141, 255, 0.16); }}
QPushButton[accent="true"]:disabled {{ border-color: #2f3f5e; color: #5a6a88; }}
QPushButton[flat="true"] {{ background: transparent; border-color: transparent; }}
QPushButton[flat="true"]:hover {{ background: {SURFACE}; }}

QTabWidget::pane {{ border: none; border-top: 1px solid {BORDER}; }}
QTabBar::tab {{ background: transparent; color: {MUTED}; padding: 9px 14px; border: none; border-bottom: 2px solid transparent; }}
QTabBar::tab:hover {{ color: {TEXT}; }}
QTabBar::tab:selected {{ color: {TEXT}; border-bottom: 2px solid {ACCENT}; }}

QComboBox {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 6px; padding: 5px 8px; min-height: 18px; }}
QComboBox:hover {{ border-color: #50505a; }}
QComboBox QAbstractItemView {{ background: {SURFACE}; border: 1px solid {BORDER}; selection-background-color: {ACCENT}; outline: none; }}
QLineEdit, QSpinBox {{ background: {BG}; border: 1px solid {BORDER}; border-radius: 6px; padding: 5px 8px; }}
QLineEdit:focus, QSpinBox:focus {{ border-color: {ACCENT}; }}

QListWidget {{ background: {BG}; border: 1px solid {BORDER}; border-radius: 8px; outline: none; padding: 3px; }}
QListWidget::item {{ border-radius: 6px; padding: 5px 6px; }}
QListWidget::item:hover {{ background: {SURFACE}; }}
QListWidget::item:selected {{ background: {ACCENT}; color: white; }}

QTreeWidget {{ background: {BG}; border: 1px solid {BORDER}; border-radius: 8px; outline: none; padding: 3px; }}
QTreeWidget::item {{ padding: 4px 3px; border-radius: 6px; }}
QTreeWidget::item:hover {{ background: {SURFACE}; }}
QTreeWidget::item:selected {{ background: {ACCENT}; color: white; }}

QSlider::groove:horizontal {{ height: 4px; background: {BORDER}; border-radius: 2px; }}
QSlider::sub-page:horizontal {{ background: {ACCENT}; border-radius: 2px; }}
QSlider[bipolar="true"]::sub-page:horizontal {{ background: transparent; }}
QSlider::handle:horizontal {{ background: {TEXT}; width: 14px; height: 14px; margin: -5px 0; border-radius: 7px; }}
QSlider::handle:horizontal:hover {{ background: white; }}
QSlider::handle:horizontal:pressed {{ background: {ACCENT_HI}; }}

QScrollBar:horizontal {{ background: transparent; height: 10px; }}
QScrollBar::handle:horizontal {{ background: #44444b; border-radius: 4px; min-width: 30px; margin: 2px; }}
QScrollBar::handle:horizontal:hover {{ background: #5a5a63; }}
QScrollBar:vertical {{ background: transparent; width: 10px; }}
QScrollBar::handle:vertical {{ background: #44444b; border-radius: 4px; min-height: 30px; margin: 2px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

QProgressBar {{ background: {BG}; border: 1px solid {BORDER}; border-radius: 6px; text-align: center; min-height: 16px; }}
QProgressBar::chunk {{ background: {ACCENT}; border-radius: 5px; }}
QStatusBar {{ background: {BG}; color: {MUTED}; border-top: 1px solid {BORDER}; }}
QStatusBar::item {{ border: none; }}
QFrame[card="true"] {{ background: {BG}; border: 1px solid {BORDER}; border-radius: 8px; }}
QMessageBox, QInputDialog {{ background: {PANEL}; }}
"""
