import copy
import logging
import time
from pathlib import Path

import numpy as np
from PySide6.QtCore import QByteArray, QSize, Qt, QThread, QTimer, QUrl, Signal
from PySide6.QtGui import QColor, QDesktopServices, QIcon, QImage, QKeySequence, QPixmap, QShortcut
from PySide6.QtWidgets import (QComboBox, QFileDialog, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMenu, QMessageBox,
                               QPushButton, QSlider, QTabWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

from ..ai.auto import suggest
from ..ai.registry import Engine, add_custom, download_model, is_available, models, remove_custom
from ..core import adjust
from ..core.adjust import CHANNELS, HSL_COLORS, EditParams
from ..core.imageio import from_array, open_image, open_preview, to_array
from ..services.batch import collect_files
from ..services.export import ExportOptions, export_image
from ..services.filters import DEFAULT_CATEGORY, MY_PACK, FilterStore, blend, category_order
from ..services.library import Library
from ..utils.numbers import parse_number
from ..utils import settings
from .batch_dialog import BatchDialog
from .canvas import CompareCanvas
from .curve_widget import PRESETS, CurveWidget
from .export_dialog import ExportDialog
from .filter_dialogs import SaveFilterDialog
from .filmstrip import Filmstrip
from .icons import icon
from .import_dialog import ImportDialog
from .widgets import BipolarSlider, HistogramWidget, Section, UniSlider, ValueEdit

log = logging.getLogger(__name__)
PREVIEW_SIDE = 2400   # правки в окне считаются на уменьшенной копии, при экспорте — на оригинале
SMALL_SIDE = 1000     # во время перетаскивания ползунков считаем ещё меньшую копию, потом дорисовываем чёткую
TINY_SIDE = 520       # если и она слишком медленная (тяжёлые фильтры), быстрый режим переключается на эту копию
FAST_BUDGET = 0.09    # сколько секунд на кадр допустимо в быстром режиме
HISTORY_LIMIT = 100
GEOMETRY = ("rotate90", "flip_h", "flip_v", "straighten", "crop")  # настройки, которые не переносятся между снимками
UNIPOLAR = {"sharpen", "noise_color", "grain"}
# (поле EditParams, подпись, минимум, максимум, делитель, формат, множитель для показа)
LIGHT = [("exposure", "Экспозиция", -300, 300, 100, "{:+.2f}", 1), ("contrast", "Контраст", -100, 100, 100, "{:+.0f}", 100),
         ("highlights", "Света", -100, 100, 100, "{:+.0f}", 100), ("shadows", "Тени", -100, 100, 100, "{:+.0f}", 100),
         ("whites", "Белые", -100, 100, 100, "{:+.0f}", 100), ("blacks", "Чёрные", -100, 100, 100, "{:+.0f}", 100)]
COLOR = [("temperature", "Температура", -100, 100, 100, "{:+.0f}", 100), ("tint", "Оттенок", -100, 100, 100, "{:+.0f}", 100),
         ("vibrance", "Красочность", -100, 100, 100, "{:+.0f}", 100), ("saturation", "Насыщенность", -100, 100, 100, "{:+.0f}", 100)]
DETAIL = [("sharpen", "Резкость", 0, 100, 100, "{:.0f}", 100), ("texture", "Текстура", -100, 100, 100, "{:+.0f}", 100),
          ("clarity", "Чёткость", -100, 100, 100, "{:+.0f}", 100),
          ("noise_color", "Цветовой шум", 0, 100, 100, "{:.0f}", 100)]
EFFECTS = [("dehaze", "Дымка", -100, 100, 100, "{:+.0f}", 100), ("vignette", "Виньетка", -100, 100, 100, "{:+.0f}", 100), ("grain", "Зерно", 0, 100, 100, "{:.0f}", 100)]
STRAIGHTEN = [("straighten", "Горизонт", -450, 450, 10, "{:+.1f}°", 1)]
HSL_NAMES = {"red": "Красный", "orange": "Оранжевый", "yellow": "Жёлтый", "green": "Зелёный", "aqua": "Аква", "blue": "Синий",
             "purple": "Фиолетовый", "magenta": "Пурпурный"}
HSL_SWATCH = {"red": "#e0443e", "orange": "#ee8b2f", "yellow": "#e8cf3c", "green": "#4fb05a", "aqua": "#37b8b4", "blue": "#3f7be0",
              "purple": "#8a56d6", "magenta": "#d556b5"}
ASPECTS = [("Свободно", None), ("Исходные", "orig"), ("1 : 1", 1.0), ("4 : 3", 4 / 3), ("3 : 4", 3 / 4), ("3 : 2", 3 / 2), ("2 : 3", 2 / 3),
           ("16 : 9", 16 / 9), ("9 : 16", 9 / 16), ("5 : 4", 5 / 4), ("4 : 5", 4 / 5)]
EMPTY_HINT = "Перетащите фото или папку в окно\nили нажмите здесь, чтобы выбрать файлы  (Ctrl+I)"
TIPS = {
    "exposure": "Общая яркость кадра в ступенях (EV): +1 — вдвое светлее, −1 — вдвое темнее",
    "contrast": "Разница между светлым и тёмным: вправо — резче и плотнее, влево — мягче",
    "highlights": "Самые светлые области: влево — вернуть детали пересвета, вправо — осветлить",
    "shadows": "Тёмные области: вправо — проявить детали в тенях, влево — сгустить",
    "whites": "Белая точка: влево — приглушить самые яркие света, вправо — добавить блеска",
    "blacks": "Чёрная точка: влево — углубить чёрный, вправо — «поднять» тени (матовость)",
    "temperature": "Баланс белого: вправо — теплее (жёлтый), влево — холоднее (синий)",
    "tint": "Зелёно-пурпурный сдвиг баланса белого: вправо — к пурпурному, влево — к зелёному",
    "vibrance": "Усиливает бледные цвета и почти не трогает уже насыщенные: кожа остаётся естественной",
    "saturation": "Насыщенность всех цветов сразу: влево до −100 — чёрно-белое",
    "sharpen": "Резкость мелких деталей",
    "texture": "Контраст мелких деталей и фактуры (кожа, ткань, кора)",
    "clarity": "Контраст средних тонов: добавляет «объём»; влево — смягчает",
    "noise_color": "Убирает цветные пятна шума, не размывая детали по яркости",
    "dehaze": "Вправо убирает дымку и туман, влево — добавляет",
    "vignette": "Края кадра: влево — затемнить, вправо — осветлить",
    "grain": "Плёночное зерно",
    "straighten": "Выравнивание горизонта, ±45°",
}
HELP = """<table cellspacing=6>
<tr><td><b>Ctrl+I</b></td><td>Импорт фото</td></tr>
<tr><td><b>Ctrl+U</b></td><td>ИИ-автокоррекция (экспозиция и цвет)</td></tr>
<tr><td><b>F</b></td><td>Режим «фокус»: скрыть панели и ленту</td></tr>
<tr><td><b>J</b></td><td>Показать пересветы (красным) и провалы (синим)</td></tr>
<tr><td><b>Клик по числу</b></td><td>Ввести значение ползунка с клавиатуры (Enter — применить, Esc — отмена)</td></tr>
<tr><td><b>Ctrl+S</b></td><td>Экспорт</td></tr>
<tr><td><b>Ctrl+Z / Ctrl+Shift+Z</b></td><td>Отменить / повторить</td></tr>
<tr><td><b>\\</b></td><td>Сравнение «До / После»</td></tr>
<tr><td><b>Колесо мыши</b></td><td>Масштаб; перетаскивание — сдвиг; двойной клик — 100% / вписать</td></tr>
<tr><td><b>Ctrl+0 / Ctrl+1</b></td><td>Вписать / 100%</td></tr>
<tr><td><b>Alt+← / Alt+→</b></td><td>Предыдущее / следующее фото</td></tr>
<tr><td><b>0–5</b></td><td>Рейтинг выбранного фото (в ленте)</td></tr>
<tr><td><b>Delete</b></td><td>Убрать фото из каталога (файл остаётся)</td></tr>
<tr><td><b>Ctrl+Shift+C / V</b></td><td>Копировать / вставить настройки</td></tr>
<tr><td><b>Enter / Esc</b></td><td>Применить / отменить кадрирование</td></tr>
<tr><td><b>Двойной клик по ползунку</b></td><td>Сбросить значение</td></tr>
<tr><td><b>Кривая</b></td><td>Клик — точка; Ctrl+клик или Delete — удалить; стрелки — сдвиг</td></tr>
<tr><td><b>HSL</b></td><td>Выберите цвет-образец и меняйте его оттенок, насыщенность и яркость</td></tr>
<tr><td><b>Перетаскивание файлов</b></td><td>В окно — быстрый импорт</td></tr></table>"""


def _label(text: str = "", muted: bool = False, heading: bool = False, wrap: bool = False) -> QLabel:
    l = QLabel(text)
    if muted:
        l.setProperty("muted", True)
    if heading:
        l.setProperty("heading", True)
    l.setWordWrap(wrap)
    return l


def _button(text: str, fn, primary: bool = False, shortcut: str | None = None, tip: str | None = None, icon_name: str | None = None) -> QPushButton:
    b = QPushButton(text)
    if icon_name:
        b.setIcon(icon(icon_name))
        b.setIconSize(QSize(18, 18))
    if primary:
        b.setProperty("primary", True)
    if shortcut:
        b.setShortcut(shortcut)
    if tip:
        b.setToolTip(tip)
    b.setCursor(Qt.PointingHandCursor)
    b.clicked.connect(fn)
    return b


class AutoWorker(QThread):
    done = Signal(dict)  # предложенные параметры
    failed = Signal(str)

    def __init__(self, img: np.ndarray, model_id: str, mode: str):
        super().__init__()
        self.img, self.model_id, self.mode = img, model_id, mode

    def run(self):
        try:
            self.done.emit(suggest(Engine(self.model_id), self.img, self.mode))
        except Exception as ex:
            log.exception("Ошибка ИИ-коррекции")
            self.failed.emit(str(ex))


def qimage_from_array(img: np.ndarray) -> QImage:
    a = np.ascontiguousarray((img * 255 + 0.5).astype(np.uint8))
    h, w, _ = a.shape
    return QImage(a.data, w, h, 3 * w, QImage.Format_RGB888).copy()


def clip_overlay(out: np.ndarray) -> QImage | None:
    """Прозрачная картинка с пересветами (красным) и провалами в тенях (синим); None, если таких пикселей нет."""
    mx = out.max(-1)
    hi, lo = mx >= 0.995, mx <= 0.004
    if not (hi.any() or lo.any()):
        return None
    a = np.zeros(out.shape[:2] + (4,), np.uint8)
    a[hi] = (255, 60, 60, 175)
    a[lo] = (70, 130, 255, 175)
    h, w = mx.shape
    return QImage(a.data, w, h, 4 * w, QImage.Format_RGBA8888).copy()


class HqWorker(QThread):
    """Чёткая перерисовка в отдельном потоке, чтобы окно не замирало на тяжёлых фильтрах. Результат с устаревшим номером отбрасывается."""
    done = Signal(int, object, object, object, int, object)  # номер, ключ «до», «до» (или None), «после», ширина кадра в пикселях оригинала, индикатор пересветов

    def __init__(self, gen: int, key, src: np.ndarray, params: EditParams, crop_mode: bool, need_before: bool, full_side: int, show_clip: bool):
        super().__init__()
        self.args = (gen, key, src, params, crop_mode, need_before, full_side, show_clip)

    def run(self):
        gen, key, src, params, crop_mode, need_before, full_side, show_clip = self.args
        try:
            geo = adjust.apply_geometry(src, params, crop=not crop_mode)
            out = adjust.apply(geo, params)
            before = qimage_from_array(geo) if need_before else None
            self.done.emit(gen, key, before, qimage_from_array(out), round(geo.shape[1] * full_side / max(src.shape[:2])), clip_overlay(out) if show_clip else None)
        except Exception:
            log.exception("Ошибка чёткой перерисовки")


PREVIEW_W, PREVIEW_H = 56, 38  # размер значка фильтра в списке; считается вдвое крупнее для чёткости


class FilterPreviewWorker(QThread):
    """Фильтры, применённые к крошечной копии текущего фото, — для значков в списке. Идёт в фоне: на все 60 фильтров меньше секунды."""
    ready = Signal(int, object, object)  # номер запуска, ключ фильтра, QImage

    def __init__(self, gen: int, base: np.ndarray, items: list):
        super().__init__()
        self.gen, self.base, self.items = gen, base, items

    def run(self):
        for key, params in self.items:
            if self.isInterruptionRequested():
                return
            try:
                self.ready.emit(self.gen, key, qimage_from_array(adjust.apply(self.base, params)))
            except Exception:
                log.exception("Превью фильтра %s", key)


class DownloadWorker(QThread):
    progress = Signal(float, str)
    done = Signal(str)
    failed = Signal(str)

    def __init__(self, model_id: str):
        super().__init__()
        self.model_id = model_id

    def run(self):
        try:
            download_model(self.model_id, lambda f, m: self.progress.emit(f, m))
            self.done.emit(self.model_id)
        except Exception as e:
            log.warning("Модель не скачана: %s", e)
            self.failed.emit(str(e))


class ExportWorker(QThread):
    done = Signal(str)
    failed = Signal(str)

    def __init__(self, src, params, dest, opts):
        super().__init__()
        self.args = (src, params, dest, opts)

    def run(self):
        try:
            src, params, dest, opts = self.args
            img = to_array(open_image(src))  # оригинал читается здесь, в фоне, и только на время экспорта
            self.done.emit(str(export_image(src, img, params, dest, opts)))
        except Exception as e:
            log.exception("Ошибка экспорта")
            self.failed.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self, path: str | None = None):
        super().__init__()
        self.setWindowTitle("Photo Editor AI")
        self.setAcceptDrops(True)
        self.resize(1400, 780)  # Qt сам поднимет размер до минимума по содержимому панели
        self.src_path: Path | None = None
        self.full_size: tuple[int, int] | None = None  # размер оригинала в пикселях; сам оригинал читается только при экспорте
        self.preview: np.ndarray | None = None
        self.preview_small: np.ndarray | None = None
        self.preview_tiny: np.ndarray | None = None
        self.hq_worker: HqWorker | None = None
        self._hq_gen = 0               # растёт при каждой правке: устаревший результат фонового потока игнорируется
        self._hq_again = False
        self._cost_per_mpx = 0.2       # оценка секунд на мегапиксель в быстром режиме (уточняется по замерам)
        self.params = EditParams()
        self.worker: AutoWorker | None = None
        self.export_worker: ExportWorker | None = None
        self.clip: dict | None = None          # скопированные настройки
        self.crop_mode = False
        self._crop_backup = [0.0, 0.0, 1.0, 1.0]
        self._before: QImage | None = None
        self._before_key = None
        self._pending = False
        self.store = FilterStore()
        self.active_filter = None
        self.sliders: dict[str, tuple[QSlider, QLabel, int, str, int]] = {}
        self._fprev: dict = {}          # (пакет, имя) -> значок фильтра на текущем фото
        self._fitems: dict = {}         # (пакет, имя) -> элемент дерева
        self._fprev_gen = 0
        self._fprev_workers: list[FilterPreviewWorker] = []
        self._sec_keys: dict = {}  # раздел -> какие параметры он содержит (для сброса и пометки «изменён»)
        self.history: list[dict] = []  # снимки параметров для отмены/повтора
        self.hidx = -1
        self._commit_timer = QTimer(self)
        self._commit_timer.setSingleShot(True)
        self._commit_timer.setInterval(350)
        self._commit_timer.timeout.connect(self._commit)
        self._hq_timer = QTimer(self)  # чёткая перерисовка после того, как пользователь отпустил ползунок
        self._hq_timer.setSingleShot(True)
        self._hq_timer.setInterval(220)
        self._hq_timer.timeout.connect(self._start_hq)

        self.canvas = CompareCanvas()
        self.canvas.set_message(EMPTY_HINT)
        self.canvas.import_requested.connect(self.import_dialog)
        self.canvas.crop_changed.connect(lambda _: self._update_crop_status())
        self.canvas.view_changed.connect(self._zoom_changed)
        self.status = _label("Готово", muted=True)
        self.info = _label("", muted=True)
        self.zoom_lbl = _label("", muted=True)
        sb = self.statusBar()
        sb.addWidget(self.status, 1)
        fit = _button("Вписать", self.canvas.fit, tip="Показать фото целиком (Ctrl+0)")
        one = _button("100%", self.canvas.zoom_100, tip="Масштаб 1:1 (Ctrl+1)")
        for b in (fit, one):
            b.setProperty("flat", True)
            b.setStyleSheet("padding: 2px 8px; min-height: 14px;")
            sb.addPermanentWidget(b)
        sb.addPermanentWidget(self.zoom_lbl)
        sb.addPermanentWidget(self.info)
        sb.addPermanentWidget(_button("?", self.show_help, tip="Горячие клавиши (F1)"))
        sb.setSizeGripEnabled(False)

        self.hist = HistogramWidget()
        self.clip_on = False
        self.hist.clip_toggled.connect(self._toggle_clip)
        tabs = QTabWidget()
        tabs.addTab(self._auto_tab(), "Авто · ИИ")
        tabs.addTab(self._manual_tab(), "Ручные")
        tabs.addTab(self._filters_tab(), "Фильтры")
        panel = self.panel = QWidget()
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(0, 0, 0, 0)
        pl.setSpacing(8)
        pl.addWidget(self.hist)
        pl.addWidget(tabs, 1)
        panel.setFixedWidth(360)

        self.lib = Library()
        self.lib.remove_missing()
        self.strip = Filmstrip()
        self.strip.selected.connect(lambda p: self.load(Path(p)))
        self.strip.remove_requested.connect(self._remove_photo)
        self.strip.rating_changed.connect(self._set_rating)
        self.strip.copy_requested.connect(lambda _p: self._copy_settings())
        self.strip.paste_requested.connect(self._paste_settings)
        self.strip.sync_requested.connect(self._sync_all)
        self.strip.reveal_requested.connect(lambda p: QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(p).parent))))
        left = QVBoxLayout()
        left.setSpacing(8)
        left.addWidget(self.canvas, 1)
        left.addWidget(self.strip)
        row = QHBoxLayout()
        row.setSpacing(12)
        row.addLayout(left, 1)
        row.addWidget(panel)
        root = QVBoxLayout()
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(10)
        root.addLayout(self._toolbar())
        root.addLayout(row, 1)
        c = QWidget()
        c.setLayout(root)
        self.setCentralWidget(c)
        self._shortcuts()
        self.strip.add_paths([Path(e.path) for e in self.lib.entries], {e.path: e.rating for e in self.lib.entries})
        self._sync_ui()
        self._history_reset()
        g = settings.get("geometry")
        if g:
            self.restoreGeometry(QByteArray.fromBase64(g.encode()))
        if path:
            p = Path(path)
            self.lib.add([p])
            self.strip.add_paths([p])
            self.load(p)

    def _shortcuts(self):
        for keys, fn in (("Ctrl+Shift+C", self._copy_settings), ("Ctrl+Shift+V", self._paste_settings), ("F1", self.show_help),
                         ("Ctrl+0", self.canvas.fit), ("Ctrl+1", self.canvas.zoom_100), ("J", lambda: self.hist.clip_btn.toggle()),
                         ("Alt+Left", lambda: self._step(-1)), ("Alt+Right", lambda: self._step(1))):
            QShortcut(QKeySequence(keys), self, fn)
        self._crop_keys = [QShortcut(QKeySequence(k), self, self._crop_enter) for k in ("Return", "Enter")]
        self._crop_keys.append(QShortcut(QKeySequence("Escape"), self, self._crop_cancel))
        for sc in self._crop_keys:
            sc.setEnabled(False)  # включаются только в режиме кадрирования, чтобы не перехватывать Enter и Esc в диалогах

    def _step(self, d: int):
        nxt = self.strip.neighbour(d)
        if nxt:
            self.strip.setCurrentItem(self.strip.items[nxt])

    def show_help(self):
        QMessageBox.information(self, "Горячие клавиши", HELP)

    # ---------- верхняя панель ----------
    def _toolbar(self) -> QHBoxLayout:
        self.undo_btn = _button("", self.undo, shortcut="Ctrl+Z", tip="Отменить (Ctrl+Z)", icon_name="undo")
        self.redo_btn = _button("", self.redo, shortcut="Ctrl+Shift+Z", tip="Повторить (Ctrl+Shift+Z)", icon_name="redo")
        for b in (self.undo_btn, self.redo_btn):
            b.setProperty("flat", True)
            b.setFixedWidth(38)
        self.cmp_btn = QPushButton(" До / После")
        self.cmp_btn.setIcon(icon("compare"))
        self.cmp_btn.setIconSize(QSize(18, 18))
        self.cmp_btn.setCheckable(True)
        self.cmp_btn.setShortcut("\\")
        self.cmp_btn.setToolTip("Сравнить с оригиналом; линию можно двигать мышью (клавиша \\)")
        self.cmp_btn.setCursor(Qt.PointingHandCursor)
        self.cmp_btn.toggled.connect(self.canvas.set_compare)
        self.focus_btn = QPushButton()
        self.focus_btn.setIcon(icon("focus"))
        self.focus_btn.setIconSize(QSize(18, 18))
        self.focus_btn.setCheckable(True)
        self.focus_btn.setShortcut("F")
        self.focus_btn.setFixedWidth(38)
        self.focus_btn.setToolTip("Фокус на фото: скрыть панели и ленту (F)")
        self.focus_btn.setCursor(Qt.PointingHandCursor)
        self.focus_btn.toggled.connect(self._focus_mode)
        self.quick_auto = _button(" Авто", lambda: self.auto_correct("full"), shortcut="Ctrl+U",
                                  tip="ИИ-автокоррекция: экспозиция и цвет одним нажатием (Ctrl+U). Выбор модели и режимов — на вкладке «Авто · ИИ»", icon_name="auto")
        self.quick_auto.setProperty("accent", True)
        bar = QHBoxLayout()
        bar.setSpacing(8)
        bar.addWidget(_button(" Импорт", self.import_dialog, True, "Ctrl+I", "Добавить фото в каталог (Ctrl+I)", "import"))
        bar.addWidget(self.quick_auto)
        bar.addSpacing(10)
        for w in (self.undo_btn, self.redo_btn, self.cmp_btn, self.focus_btn):
            bar.addWidget(w)
        bar.addStretch()
        for w in (_button(" Пакетная обработка", self.batch_dialog, icon_name="batch", tip="Применить ИИ и настройки ко многим фото сразу"),
                  _button(" Сбросить", self.reset, icon_name="reset", tip="Вернуть все настройки текущего фото к исходным (можно отменить: Ctrl+Z)"),
                  _button(" Экспорт…", self.save_dialog, True, "Ctrl+S", "Сохранить результат в файл (Ctrl+S)", "export")):
            bar.addWidget(w)
        return bar

    def _toggle_clip(self, on: bool):
        """Индикатор пересветов (красный) и провалов (синий) на фото."""
        self.clip_on = on
        if self.preview is not None:
            self.render()
        else:
            self.canvas.set_overlay(None)

    def _focus_mode(self, on: bool):
        """Только фото: панель настроек и лента скрываются (повторное нажатие возвращает)."""
        self.panel.setVisible(not on)
        self.strip.setVisible(not on)

    def batch_dialog(self):
        BatchDialog(self, self.model_box.currentData(), copy.deepcopy(self.params) if self.src_path else None).exec()

    # ---------- вкладки ----------
    def _auto_tab(self) -> QWidget:
        self.model_box = QComboBox()
        self.model_desc = _label(muted=True, wrap=True)
        self.model_box.currentIndexChanged.connect(self._model_changed)
        self._model_list("iat_exposure")  # самая осторожная из моделей; без файла остаётся встроенная
        add_model = _button("Добавить свою…", self._model_add, tip="Подключить свою ONNX-модель: вид определится автоматически")
        self.del_model = _button("Удалить", self._model_remove)
        self._model_changed()
        mrow = QHBoxLayout()
        mrow.addWidget(add_model)
        mrow.addWidget(self.del_model)
        self.auto_full_btn = _button("Авто: экспозиция + цвет", lambda: self.auto_correct("full"), True)
        self.auto_exp_btn = _button("Авто: только экспозиция", lambda: self.auto_correct("exposure"))
        self.auto_strength = QSlider(Qt.Horizontal)
        self.auto_strength.setRange(0, 100)
        self.auto_strength.setValue(100)
        self.strength_val = _label("100%", muted=True)
        self.auto_strength.valueChanged.connect(lambda v: self.strength_val.setText(f"{v}%"))
        srow = QHBoxLayout()
        srow.addWidget(_label("Сила", muted=True))
        srow.addWidget(self.auto_strength, 1)
        srow.addWidget(self.strength_val)
        m = Section("Модель")
        m.add(self.model_box)
        m.add(self.model_desc)
        m.add(mrow)
        a = Section("Автокоррекция")
        a.add(self.auto_full_btn)
        a.add(self.auto_exp_btn)
        a.add(srow)
        a.add(_label("ИИ подбирает значения ползунков с защитой светов от пересвета. Результат можно доточить на вкладке «Ручные».", muted=True, wrap=True))
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 6, 0, 0)
        lay.addWidget(m)
        lay.addWidget(a)
        lay.addStretch()
        return w

    def _model_list(self, select: str | None = None):
        self.model_box.blockSignals(True)
        self.model_box.clear()
        for m in models().values():
            self.model_box.addItem(("★ " if m.id.startswith("custom_") else "") + m.name + ("" if is_available(m.id) else (" (скачать)" if m.url else " (нет файла)")), m.id)
        i = self.model_box.findData(select) if select else -1
        if i >= 0 and is_available(select):
            self.model_box.setCurrentIndex(i)
        self.model_box.blockSignals(False)
        if hasattr(self, "del_model"):
            self._model_changed()

    def _model_changed(self):
        mid = self.model_box.currentData()
        self.model_desc.setText(models()[mid].desc if mid else "")
        self.del_model.setEnabled(bool(mid) and mid.startswith("custom_"))

    def _model_add(self):
        f, _ = QFileDialog.getOpenFileName(self, "Выберите ONNX-модель", "", "ONNX (*.onnx)")
        if not f:
            return
        try:
            spec = add_custom(Path(f), Path(f).stem)
        except Exception as e:
            QMessageBox.warning(self, "Модель не добавлена", str(e))
            return
        self._model_list(spec.id)
        self.status.setText(f"Модель добавлена: {spec.name} ({spec.desc})")

    def _model_remove(self):
        mid = self.model_box.currentData()
        if mid and mid.startswith("custom_") and QMessageBox.question(self, "Удалить модель", f"Удалить «{models()[mid].name}»?") == QMessageBox.Yes:
            remove_custom(mid)
            self._model_list("iat_exposure")

    def _section(self, title: str, rows, expanded: bool = True, keys: list | None = None) -> Section:
        keys = keys if keys is not None else [r[0] for r in rows]
        sec = Section(title, expanded, lambda: self._reset_keys(keys))
        self._sec_keys[sec] = keys
        for key, label, lo, hi, div, fmt, mul in rows:
            cap = _label(label)
            cap.setFixedWidth(104)
            s = UniSlider(lo, hi) if key in UNIPOLAR else BipolarSlider(lo, hi)
            s.valueChanged.connect(self._on_slider)
            val = ValueEdit()
            val.committed.connect(lambda t, key=key: self._value_typed(key, t))
            for w_ in (cap, s, val):
                w_.setToolTip(TIPS.get(key, ""))
            self.sliders[key] = (s, val, div, fmt, mul)
            row = QHBoxLayout()
            row.setSpacing(6)
            row.addWidget(cap)
            row.addWidget(s, 1)
            row.addWidget(val)
            sec.add(row)
        return sec

    def _manual_tab(self) -> QWidget:
        self.curve = CurveWidget()
        self.curve.set_curves(self.params.curves)
        self.curve.changed.connect(self._on_curve)
        ch = QComboBox()
        ch.addItems(["RGB", "Красный", "Зелёный", "Синий"])
        ch.setToolTip("Клик по кривой — новая точка; Ctrl+клик или Delete — удалить; стрелки — сдвиг")
        ch.currentIndexChanged.connect(lambda i: self.curve.set_channel(CHANNELS[i]))
        pre = QComboBox()
        pre.addItems(PRESETS)
        pre.activated.connect(lambda i: self.curve.apply_preset(pre.itemText(i)))
        pre.setToolTip("Готовая форма кривой для выбранного канала")
        crow = QHBoxLayout()
        crow.addWidget(ch)
        crow.addWidget(pre)
        cs = Section("Тоновая кривая", False, lambda: self._reset_keys(["curves"]))
        self._sec_keys[cs] = ["curves"]
        cs.add(crow)
        cs.body_lay.addWidget(self.curve, 0, Qt.AlignHCenter)

        hs = self._hsl_section()
        geo = self._section("Кадр и поворот", STRAIGHTEN, False, keys=["straighten", "geometry"])
        grow = QHBoxLayout()
        for name, tip, fn in (("rotate_left", "Повернуть влево на 90°", lambda: self._geo(rotate90=(self.params.rotate90 - 1) % 4)),
                              ("rotate_right", "Повернуть вправо на 90°", lambda: self._geo(rotate90=(self.params.rotate90 + 1) % 4)),
                              ("flip_h", "Отразить по горизонтали", lambda: self._geo(flip_h=1 - self.params.flip_h)),
                              ("flip_v", "Отразить по вертикали", lambda: self._geo(flip_v=1 - self.params.flip_v))):
            grow.addWidget(_button("", fn, tip=tip, icon_name=name))
        geo.body_lay.insertLayout(0, grow)
        self.aspect = QComboBox()
        for name, _v in ASPECTS:
            self.aspect.addItem(name)
        self.aspect.currentIndexChanged.connect(self._aspect_changed)
        self.crop_btn = QPushButton(" Кадрировать")
        self.crop_btn.setIcon(icon("crop"))
        self.crop_btn.setIconSize(QSize(18, 18))
        self.crop_btn.setCheckable(True)
        self.crop_btn.setCursor(Qt.PointingHandCursor)
        self.crop_btn.toggled.connect(self._toggle_crop)
        self.crop_btn.setToolTip("Включить рамку на фото. Enter — применить, Esc — отменить")
        reset_crop = _button("Сбросить кадр", lambda: self._geo(crop=[0.0, 0.0, 1.0, 1.0], keep_crop=True))
        crow2 = QHBoxLayout()
        crow2.addWidget(self.aspect, 1)
        crow2.addWidget(self.crop_btn)
        geo.add(crow2)
        geo.add(reset_crop)

        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 4, 0, 0)
        lay.setSpacing(0)
        secs = (self._section("Свет", LIGHT), self._section("Цвет", COLOR), self._section("Детали", DETAIL, False),
                self._section("Эффекты", EFFECTS, False), hs, cs, geo)
        self._open_secs = [secs[0], secs[1]]  # открыты одновременно не больше двух: панель без прокрутки остаётся в пределах экрана
        for sec in secs:
            lay.addWidget(sec)
            sec.head.toggled.connect(lambda on, sec=sec: self._section_toggled(sec, on))
        lay.addStretch()
        return w

    def _section_toggled(self, sec: Section, on: bool):
        if sec in self._open_secs:
            self._open_secs.remove(sec)
        if on:
            self._open_secs.append(sec)
            while len(self._open_secs) > 2:
                self._open_secs.pop(0).head.setChecked(False)  # самый давно открытый сворачивается

    def _hsl_section(self) -> Section:
        """Цвет по оттенкам: образцы цветов в ряд и три ползунка для выбранного (как в Lightroom «Микс цветов»)."""
        sec = Section("Цвет по оттенкам (HSL)", False, lambda: self._reset_keys(["hsl"]))
        self._sec_keys[sec] = ["hsl"]
        self.hsl_color = "orange"
        self.hsl_buttons: dict[str, QPushButton] = {}
        row = QHBoxLayout()
        row.setSpacing(4)
        for col in HSL_COLORS:
            b = QPushButton()
            b.setCheckable(True)
            b.setFixedSize(30, 24)
            b.setToolTip(HSL_NAMES[col])
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(f"QPushButton {{ background: {HSL_SWATCH[col]}; border: 2px solid transparent; border-radius: 6px; padding: 0; }}"
                            f"QPushButton:checked {{ border: 2px solid #ffffff; }}")
            b.clicked.connect(lambda _=False, c=col: self._hsl_pick(c))
            self.hsl_buttons[col] = b
            row.addWidget(b)
        sec.add(row)
        self.hsl_title = _label(muted=True)
        sec.add(self.hsl_title)
        self.hsl_sliders: list[tuple[BipolarSlider, QLabel]] = []
        for i, name in enumerate(("Оттенок", "Насыщенность", "Яркость")):
            cap = _label(name)
            cap.setFixedWidth(104)
            s = BipolarSlider(-100, 100)
            s.valueChanged.connect(lambda _v, i=i: self._on_hsl(i))
            val = ValueEdit()
            val.committed.connect(lambda t, i=i: self._hsl_typed(i, t))
            r = QHBoxLayout()
            r.setSpacing(6)
            r.addWidget(cap)
            r.addWidget(s, 1)
            r.addWidget(val)
            sec.add(r)
            self.hsl_sliders.append((s, val))
        self._hsl_pick("orange")
        return sec

    def _hsl_pick(self, col: str):
        self.hsl_color = col
        for c, b in self.hsl_buttons.items():
            b.setChecked(c == col)
        self.hsl_title.setText(HSL_NAMES[col])
        self._hsl_sync()

    def _hsl_sync(self):
        """Показать значения выбранного цвета; точка у образца — у цвета есть правки."""
        for i, (s, val) in enumerate(self.hsl_sliders):
            v = self.params.hsl[self.hsl_color][i]
            s.blockSignals(True)
            s.setValue(round(v * 100))
            s.blockSignals(False)
            val.setText(f"{v * 100:+.0f}")
        for c, b in self.hsl_buttons.items():
            b.setText("●" if any(self.params.hsl[c]) else "")

    def _on_hsl(self, i: int):
        s, val = self.hsl_sliders[i]
        self.params.hsl[self.hsl_color][i] = s.value() / 100
        val.setText(f"{s.value():+.0f}")
        self.hsl_buttons[self.hsl_color].setText("●" if any(self.params.hsl[self.hsl_color]) else "")
        self._edited()

    # ---------- геометрия и кадрирование ----------
    def _geo(self, keep_crop: bool = False, **changes):
        """Поворот и отражения меняют систему координат кадра, поэтому рамка сбрасывается."""
        for k, v in changes.items():
            setattr(self.params, k, v)
        if not keep_crop:
            self.params.crop = [0.0, 0.0, 1.0, 1.0]
        if self.crop_mode:
            self.canvas.crop = list(self.params.crop)
        self._sync_ui()
        self._edited()

    def _aspect_changed(self):
        ratio = ASPECTS[self.aspect.currentIndex()][1]
        if ratio == "orig":
            ratio = self.canvas.after.width() / self.canvas.after.height() if self.canvas.after is not None else None
        if not self.crop_btn.isChecked() and ratio is not None and self.preview is not None:
            self.crop_btn.setChecked(True)  # выбор пропорции сразу включает рамку
        self.canvas.set_crop_ratio(ratio)
        self._update_crop_status()

    def _toggle_crop(self, on: bool):
        if self.preview is None:
            self.crop_btn.blockSignals(True)
            self.crop_btn.setChecked(False)
            self.crop_btn.blockSignals(False)
            self.status.setText("Сначала откройте фото")
            return
        self.crop_mode = on
        for sc in self._crop_keys:
            sc.setEnabled(on)
        if on:
            self.cmp_btn.setChecked(False)
            self._crop_backup = list(self.params.crop)
            self.render()  # кадр показывается целиком, рамка — поверх него
            self.canvas.set_crop_mode(True, self.params.crop)
            self._aspect_changed_silent()
            self.status.setText("Кадрирование: потяните за углы и стороны, Enter — применить, Esc — отмена")
        else:
            self.canvas.set_crop_mode(False)
            c = self.canvas.crop
            self.params.crop = [0.0, 0.0, 1.0, 1.0] if (c[2] - c[0]) * (c[3] - c[1]) > 0.995 else [round(v, 5) for v in c]
            self.render()
            self.canvas.fit()
            self._commit_timer.start()
            self.status.setText("Кадр применён" if self.params.crop != [0.0, 0.0, 1.0, 1.0] else "Кадр без обрезки")

    def _aspect_changed_silent(self):
        ratio = ASPECTS[self.aspect.currentIndex()][1]
        if ratio == "orig":
            ratio = self.canvas.after.width() / self.canvas.after.height()
        self.canvas.set_crop_ratio(ratio)

    def _crop_enter(self):
        self.crop_btn.setChecked(False)

    def _crop_cancel(self):
        self.canvas.crop = list(self._crop_backup)
        self.crop_btn.setChecked(False)
        self.status.setText("Кадрирование отменено")

    def _update_crop_status(self):
        if self.crop_mode and self.canvas.after is not None:
            c = self.canvas.crop
            self.status.setText(f"Рамка: {round((c[2] - c[0]) * self.canvas.source_width)} × "
                                f"{round((c[3] - c[1]) * self.canvas.source_width * self.canvas.after.height() / self.canvas.after.width())} px")

    # ---------- фильтры и пакеты ----------
    def _filters_tab(self) -> QWidget:
        self.filters: list = []
        self.active_pack = None
        saved = settings.get("filter_open", None)
        self._open_groups: set[str] | None = set(saved) if isinstance(saved, list) else None  # раскрытые группы; None — первый запуск
        self.fgroup = QComboBox()
        self.fgroup.addItems(["По пакетам", "По типам", "Списком"])
        self.fgroup.setToolTip("Как сгруппировать фильтры: по пакетам, по типам (портрет, пейзаж, …) или одним списком")
        self.fgroup.setCurrentIndex(min(max(int(settings.get("filter_group", 0) or 0), 0), 2))
        self.fgroup.currentIndexChanged.connect(self._filter_group_changed)
        self.fsearch = QLineEdit()
        self.fsearch.setPlaceholderText("Поиск фильтра…")
        self.fsearch.setClearButtonEnabled(True)
        self.fsearch.textChanged.connect(lambda _t: self._filter_list())
        top = QHBoxLayout()
        top.addWidget(self.fgroup)
        top.addWidget(self.fsearch, 1)
        self.ftree = QTreeWidget()
        self.ftree.setHeaderHidden(True)
        self.ftree.setIconSize(QSize(PREVIEW_W, PREVIEW_H))
        self.ftree.setIndentation(14)
        self.ftree.setUniformRowHeights(False)  # у строк со значками высота больше, чем у заголовков групп
        self.ftree.currentItemChanged.connect(lambda cur, _prev: self._filter_picked(cur))
        self.ftree.itemExpanded.connect(lambda it: self._group_open(it, True))
        self.ftree.itemCollapsed.connect(lambda it: self._group_open(it, False))
        self.fstrength = QSlider(Qt.Horizontal)
        self.fstrength.setRange(0, 100)
        self.fstrength.setValue(100)
        self.fval = _label("100%", muted=True)
        self.fstrength.valueChanged.connect(lambda v: (self.fval.setText(f"{v}%"), self._apply_filter()))
        srow = QHBoxLayout()
        srow.addWidget(_label("Сила", muted=True))
        srow.addWidget(self.fstrength, 1)
        srow.addWidget(self.fval)
        self.fexport = QPushButton("Экспорт")
        self.fexport.setCursor(Qt.PointingHandCursor)
        menu = QMenu(self.fexport)
        self.act_export_filter = menu.addAction("Выбранный фильтр…")
        self.act_export_pack = menu.addAction("Весь пакет…")
        self.act_export_filter.triggered.connect(lambda: self._filter_export("filter"))
        self.act_export_pack.triggered.connect(lambda: self._filter_export("pack"))
        menu.aboutToShow.connect(lambda: (self.act_export_filter.setEnabled(self.active_filter is not None), self.act_export_pack.setEnabled(self.active_pack is not None)))
        self.fexport.setMenu(menu)
        grid = QGridLayout()
        grid.addWidget(_button("Сохранить как фильтр…", self._filter_save), 0, 0)
        grid.addWidget(_button("Импорт…", self._filter_import, tip="Загрузить фильтр или целый пакет: .json (фильтр или пакет), .cube (LUT)"), 0, 1)
        grid.addWidget(self.fexport, 1, 0)
        grid.addWidget(_button("Удалить", self._filter_delete, tip="Удалить свой фильтр; если выбран заголовок своего пакета — весь пакет"), 1, 1)
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 8, 0, 0)
        lay.addLayout(top)
        lay.addWidget(self.ftree, 1)
        lay.addLayout(srow)
        lay.addLayout(grid)
        lay.addWidget(_label("★ — ваши фильтры и пакеты. Пакет можно экспортировать одним файлом и отправить другому: «Импорт…» добавит его целиком.", muted=True, wrap=True))
        self._filter_list()
        return w

    def _filter_icon(self, key) -> QIcon:
        pm = self._fprev.get(key)
        if pm is None:  # пока значок не готов — пустое место того же размера, чтобы строки не прыгали
            pm = QPixmap(PREVIEW_W, PREVIEW_H)
            pm.fill(Qt.transparent)
        return QIcon(pm)

    def _start_previews(self):
        """Запустить расчёт значков для фильтров без значка. Старый расчёт прерывается: фото могло смениться."""
        self._fprev_workers = [w for w in self._fprev_workers if w.isRunning()]
        for w in self._fprev_workers:
            w.requestInterruption()
        self._fprev_gen += 1
        if self.preview_tiny is None:
            return
        todo = [((f.pack, f.name), f.params) for f in self.filters if (f.pack, f.name) not in self._fprev]
        if not todo:
            return
        im = from_array(self.preview_tiny)
        w2, h2 = PREVIEW_W * 2, PREVIEW_H * 2
        k = max(w2 / im.width, h2 / im.height)  # масштаб «заполнить» и обрезка по центру до пропорций значка
        im = im.resize((max(w2, round(im.width * k)), max(h2, round(im.height * k))))
        left, top = (im.width - w2) // 2, (im.height - h2) // 2
        base = to_array(im.crop((left, top, left + w2, top + h2)))
        worker = FilterPreviewWorker(self._fprev_gen, base, todo)
        worker.ready.connect(self._preview_ready)
        self._fprev_workers.append(worker)
        worker.start()

    def _preview_ready(self, gen: int, key, qimg):
        if gen != self._fprev_gen:  # результат прерванного расчёта (другое фото)
            return
        pm = QPixmap.fromImage(qimg)
        pm.setDevicePixelRatio(2)
        self._fprev[key] = pm
        it = self._fitems.get(key)
        if it is not None:
            it.setIcon(0, QIcon(pm))

    def _group_open(self, item, on: bool):
        kind, val = item.data(0, Qt.UserRole) or (None, None)
        if kind in ("p", "c"):
            if self._open_groups is None:
                self._open_groups = set()
            (self._open_groups.add if on else self._open_groups.discard)(f"{kind}:{val}")
            settings.put("filter_open", sorted(self._open_groups))

    def _filter_group_changed(self, i: int):
        settings.put("filter_group", i)
        self._filter_list()

    def _filter_list(self, select: tuple[str, str] | None = None):
        """Перестроить дерево фильтров. select — (пакет, название фильтра), который нужно выделить."""
        packs = self.store.packs()
        self.filters = [f for pk in packs for f in pk.filters]
        index = {id(f): i for i, f in enumerate(self.filters)}
        mode = self.fgroup.currentIndex()
        q = self.fsearch.text().strip().lower()
        match = lambda f: not q or q in f.name.lower() or q in f.pack.lower() or q in f.category.lower()

        self._fitems = {}

        def leaf(f) -> QTreeWidgetItem:
            it = QTreeWidgetItem([f.name + ("" if f.builtin else "  ★")])
            it.setData(0, Qt.UserRole, ("f", index[id(f)]))
            it.setToolTip(0, f"{f.pack} · {f.category}")
            key = (f.pack, f.name)
            it.setIcon(0, self._filter_icon(key))
            self._fitems[key] = it
            return it

        self.ftree.blockSignals(True)
        self.ftree.clear()
        target = None
        if mode == 2:
            for f in self.filters:
                if match(f):
                    self.ftree.addTopLevelItem(leaf(f))
        else:
            if mode == 0:
                groups = [("p", pk.name, pk.name + ("" if pk.builtin else "  ★"), [f for f in pk.filters if match(f)], pk.description) for pk in packs]
            else:
                cats: dict[str, list] = {}
                for f in self.filters:
                    if match(f):
                        cats.setdefault(f.category or DEFAULT_CATEGORY, []).append(f)
                groups = [("c", c, c, cats[c], "") for c in category_order(cats)]
            groups = [g for g in groups if g[3]]
            if self._open_groups is None and groups:  # первый запуск: раскрыт только первый пакет, остальные свёрнуты
                self._open_groups = {f"{groups[0][0]}:{groups[0][1]}"}
            for kind, key, title, fl, tip in groups:
                head = QTreeWidgetItem([f"{title}  ({len(fl)})"])
                head.setData(0, Qt.UserRole, (kind, key))
                head.setToolTip(0, tip)
                font = head.font(0)
                font.setBold(True)
                head.setFont(0, font)
                for f in fl:
                    head.addChild(leaf(f))
                self.ftree.addTopLevelItem(head)
                head.setExpanded(bool(q) or f"{kind}:{key}" in (self._open_groups or set()))
        if select:
            for it in self.ftree.findItems("", Qt.MatchContains | Qt.MatchRecursive):
                kind, val = it.data(0, Qt.UserRole) or (None, None)
                if kind == "f" and (self.filters[val].pack, self.filters[val].name) == select:
                    target = it
                    break
        self.ftree.blockSignals(False)
        self._start_previews()  # значки для фильтров, у которых их ещё нет (новый фильтр, новое фото)
        if target is not None:
            if target.parent() is not None:
                target.parent().setExpanded(True)
            self.ftree.setCurrentItem(target)  # сигнал не заблокирован: фильтр применится
            self.ftree.scrollToItem(target)

    def _filter_picked(self, item):
        self.active_filter = self.active_pack = None
        if item is None:
            return
        kind, val = item.data(0, Qt.UserRole) or (None, None)
        if kind == "f":
            self.active_filter = self.filters[val]
            self.active_pack = next((p for p in self.store.packs() if p.name == self.active_filter.pack), None)
            self._apply_filter()
        elif kind == "p":
            self.active_pack = next((p for p in self.store.packs() if p.name == val), None)
            if self.active_pack is not None:
                self.status.setText(f"Пакет «{val}»: {len(self.active_pack.filters)} фильтров" + (f" — {self.active_pack.description}" if self.active_pack.description else ""))
        elif kind == "c":
            self.status.setText(f"Тип «{val}»")

    def _apply_filter(self):
        if self.active_filter is None or self.preview is None:
            return
        new = blend(self.active_filter.params, self.fstrength.value() / 100)
        for k in GEOMETRY:  # фильтр меняет цвет, но не кадр и не поворот
            setattr(new, k, getattr(self.params, k))
        self.params = new
        self._sync_ui()
        self._schedule_render()  # как у обычных ползунков: быстро сразу, чётко — после паузы
        self._commit_timer.start()
        self.status.setText(f"Фильтр: {self.active_filter.name}  ·  {self.active_filter.pack}")

    def _filter_save(self):
        f, pk = self.active_filter, self.active_pack
        d = SaveFilterDialog(self, self.store.pack_names(), pk.name if pk is not None and not pk.builtin else MY_PACK, f.category if f else DEFAULT_CATEGORY)
        if not d.exec():
            return
        name, pack, category = d.values()
        params = EditParams.from_dict(self.params.to_dict())
        for k, default in (("rotate90", 0), ("flip_h", 0), ("flip_v", 0), ("straighten", 0.0), ("crop", [0.0, 0.0, 1.0, 1.0])):  # кадр и поворот в фильтр не входят
            setattr(params, k, default)
        try:
            saved = self.store.save_user(name, params, pack, category)
        except ValueError as e:
            QMessageBox.warning(self, "Фильтр не сохранён", str(e))
            return
        if self._open_groups is None:
            self._open_groups = set()
        self._open_groups |= {f"p:{saved.pack}", f"c:{saved.category}"}
        self._filter_list((saved.pack, saved.name))
        self.status.setText(f"Фильтр «{saved.name}» сохранён в пакет «{saved.pack}»")

    def _filter_import(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Импорт фильтров и пакетов", "", "Фильтры и пакеты (*.json *.cube)")
        if not files:
            return
        filters = packs = 0
        errors, last = [], None
        for f in files:
            try:
                r = self.store.import_file(Path(f))
            except Exception as e:
                errors.append(f"{Path(f).name}: {e}")
                continue
            filters += r.count
            packs += r.kind == "pack"
            last = r
            if r.kind == "pack":
                if self._open_groups is None:
                    self._open_groups = set()
                self._open_groups.add(f"p:{r.name}")
        if last is not None:
            self._filter_list((last.name, last.name) if last.kind != "pack" else None)
            self.status.setText(f"Импортировано: фильтров {filters}" + (f", пакетов {packs}" if packs else ""))
        if errors:
            QMessageBox.warning(self, "Не всё загружено", "\n".join(errors))

    def _filter_export(self, what: str):
        if what == "filter":
            f = self.active_filter
            if f is None:
                self.status.setText("Выберите фильтр для экспорта")
                return
            ext = ".cube" if f.path and f.path.suffix == ".cube" else ".json"
            dest, _ = QFileDialog.getSaveFileName(self, "Экспорт фильтра", f"{f.name}{ext}", f"*{ext}")
            if dest:
                self.store.export(f, Path(dest))
                self.status.setText(f"Фильтр сохранён: {Path(dest).name}")
            return
        pk = self.active_pack
        if pk is None:
            self.status.setText("Выберите пакет (заголовок пакета или любой фильтр из него)")
            return
        dest, _ = QFileDialog.getSaveFileName(self, "Экспорт пакета", f"{pk.name}.pack.json", "Пакет фильтров (*.pack.json *.json)")
        if dest:
            n = self.store.export_pack(pk, Path(dest))
            skipped = len(pk.filters) - n
            self.status.setText(f"Пакет «{pk.name}» сохранён: {n} фильтров" + (f" (без {skipped} на основе LUT)" if skipped else ""))

    def _filter_delete(self):
        f, pk = self.active_filter, self.active_pack
        if f is not None:
            if f.builtin:
                self.status.setText("Встроенные фильтры удалить нельзя")
                return
            self.store.delete(f)
            self.active_filter = None
        elif pk is not None:
            if pk.builtin:
                self.status.setText("Встроенные пакеты удалить нельзя")
                return
            if pk.name == MY_PACK:
                self.status.setText("«Мои фильтры» — удаляйте фильтры по одному")
                return
            if QMessageBox.question(self, "Удалить пакет", f"Удалить пакет «{pk.name}» вместе с {len(pk.filters)} фильтрами?") != QMessageBox.Yes:
                return
            self.store.delete_pack(pk)
            self.active_pack = None
        else:
            self.status.setText("Выберите свой фильтр или заголовок своего пакета")
            return
        self._filter_list()

    # ---------- параметры и история ----------
    def _sync_ui(self):
        """Привести ползунки и кривую в соответствие с self.params (без лишних перерисовок)."""
        for key, (s, val, div, fmt, mul) in self.sliders.items():
            s.blockSignals(True)
            s.setValue(round(getattr(self.params, key) * div))
            s.blockSignals(False)
            val.setText(fmt.format(getattr(self.params, key) * mul))
        self.curve.set_curves(self.params.curves)
        self._hsl_sync()
        self._mark_sections()

    def _value_typed(self, key: str, text: str):
        s, val, div, fmt, mul = self.sliders[key]
        v = parse_number(text)
        if v is not None:
            s.setValue(round(v / mul * div))  # QSlider сам ограничивает значение диапазоном ползунка
        self._sync_ui()  # вернуть корректный текст (и после неверного ввода)

    def _hsl_typed(self, i: int, text: str):
        v = parse_number(text)
        if v is not None:
            self.hsl_sliders[i][0].setValue(round(v))
        self._hsl_sync()

    def _is_modified(self, keys: list) -> bool:
        d, p = EditParams(), self.params
        for k in keys:
            if k == "curves":
                changed = not p.curve_is_identity()
            elif k == "hsl":
                changed = not p.hsl_is_identity()
            elif k == "geometry":
                changed = bool(p.rotate90 % 4 or p.flip_h or p.flip_v or p.crop != d.crop)
            else:
                changed = getattr(p, k) != getattr(d, k)
            if changed:
                return True
        return False

    def _mark_sections(self):
        for sec, keys in self._sec_keys.items():
            sec.set_modified(self._is_modified(keys))

    def _reset_keys(self, keys: list):
        """Вернуть параметры раздела к исходным (кнопка у заголовка раздела); действие можно отменить."""
        if "geometry" in keys and self.crop_mode:
            self.canvas.crop = [0.0, 0.0, 1.0, 1.0]
            self.crop_btn.setChecked(False)
        d = EditParams()
        for k in keys:
            if k == "curves":
                self.params.curves = d.curves
            elif k == "hsl":
                self.params.hsl = d.hsl
            elif k == "geometry":
                for g in ("rotate90", "flip_h", "flip_v", "crop"):
                    setattr(self.params, g, getattr(d, g))
            else:
                setattr(self.params, k, getattr(d, k))
        self._sync_ui()
        self._edited()

    def _on_slider(self):
        for key, (s, val, div, fmt, mul) in self.sliders.items():
            v = s.value() / div
            setattr(self.params, key, v)
            val.setText(fmt.format(v * mul))
        self._edited()

    def _on_curve(self):
        self._edited()

    def _edited(self):
        self._mark_sections()
        self._schedule_render()
        self._commit_timer.start()  # снимок для отмены берём, когда пользователь остановился

    def _schedule_render(self):
        """При перетаскивании событий больше, чем кадров: рисуем один раз после пачки, сначала быстро, потом чётко."""
        if not self._pending:
            self._pending = True
            QTimer.singleShot(0, self._do_render)

    def _do_render(self):
        self._pending = False
        self.render(fast=True)
        self._hq_timer.start()

    def _history_reset(self):
        self.history, self.hidx = [copy.deepcopy(self.params.to_dict())], 0
        self._history_buttons()

    def _commit(self):
        snap = copy.deepcopy(self.params.to_dict())
        if snap == self.history[self.hidx]:
            return
        del self.history[self.hidx + 1:]
        self.history.append(snap)
        del self.history[:-HISTORY_LIMIT]
        self.hidx = len(self.history) - 1
        self._history_buttons()

    def _history_buttons(self):
        self.undo_btn.setEnabled(self.hidx > 0)
        self.redo_btn.setEnabled(self.hidx < len(self.history) - 1)

    def _history_go(self, idx: int):
        self.hidx = idx
        self.params = EditParams.from_dict(self.history[idx])
        if self.crop_mode:
            self.canvas.crop = list(self.params.crop)
        self._sync_ui()
        self.render()
        self._history_buttons()

    def undo(self):
        self._commit_timer.stop()
        self._commit()  # не потерять правку, сделанную прямо перед отменой
        if self.hidx > 0:
            self._history_go(self.hidx - 1)

    def redo(self):
        if self.hidx < len(self.history) - 1:
            self._history_go(self.hidx + 1)

    def reset(self):
        if self.crop_mode:
            self.canvas.crop = [0.0, 0.0, 1.0, 1.0]
            self.crop_btn.setChecked(False)
        self.params = EditParams()
        self._sync_ui()
        self.render()
        self._commit_timer.start()

    # ---------- каталог ----------
    def import_dialog(self):
        d = ImportDialog(self)
        if d.exec() and d.imported:
            self._add_to_library(d.imported)

    def _add_to_library(self, paths: list[Path]):
        self._save_edit()
        self.lib.add(paths)
        self.strip.add_paths(paths, {e.path: e.rating for e in self.lib.entries})
        self.status.setText(f"Добавлено фото: {len(paths)}")
        self.strip.setCurrentItem(self.strip.items[str(paths[0])])

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        files = collect_files([Path(u.toLocalFile()) for u in e.mimeData().urls() if u.isLocalFile()])
        if files:
            self._add_to_library(files)

    def _save_edit(self):
        e = self.src_path and self.lib.get(self.src_path)
        if e:
            e.params = self.params.to_dict()
            self.lib.save()

    def _remove_photo(self, path: str):
        """Убирает снимок из каталога; файл на диске не удаляется."""
        nxt = self.strip.neighbour(1) or self.strip.neighbour(-1) if self.src_path == Path(path) else None
        if self.src_path == Path(path):
            self.src_path = None  # правки удаляемого снимка сохранять не нужно
        self.lib.remove(Path(path))
        self.strip.remove_path(path)
        self.status.setText(f"Убрано из каталога: {Path(path).name} (файл на диске остался)")
        if self.src_path is None and self.preview is not None and Path(path) == getattr(self, "_shown", None):
            if nxt:
                self.load(Path(nxt))  # Qt сам сдвигает выбор без сигнала, поэтому открываем соседнее фото явно
            else:
                self._clear_view()

    def _clear_view(self):
        self.preview = self.preview_small = self.preview_tiny = self.full_size = None
        self._shown = None
        self.canvas.after = self.canvas.before = None
        self.canvas.set_message(EMPTY_HINT)
        self.hist.set_image(None)
        self.info.setText("")
        self.zoom_lbl.setText("")
        self.setWindowTitle("Photo Editor AI")
        self.params = EditParams()
        self._sync_ui()
        self._history_reset()

    def _set_rating(self, path: str, n: int):
        e = self.lib.get(Path(path))
        if e:
            e.rating = n
            self.lib.save()
            self.strip.set_rating(path, n)

    def _copy_settings(self):
        if self.preview is None:
            return
        self.clip = copy.deepcopy(self.params.to_dict())
        self.status.setText("Настройки скопированы (кроме кадра и поворота)")

    def _paste_settings(self):
        if self.clip is None or self.preview is None:
            self.status.setText("Нечего вставлять: сначала скопируйте настройки (Ctrl+Shift+C)")
            return
        d = copy.deepcopy(self.clip)
        for k in GEOMETRY:  # кадр и поворот у каждого снимка свои
            d[k] = getattr(self.params, k)
        self.params = EditParams.from_dict(d)
        self._sync_ui()
        self.render()
        self._commit_timer.start()
        self.status.setText("Настройки вставлены")

    def _sync_all(self):
        if self.preview is None:
            return
        n = len(self.lib.entries) - 1
        if n < 1 or QMessageBox.question(self, "Применить ко всем", f"Заменить настройки у {n} других фото в каталоге текущими?\n"
                                         "Кадр и поворот каждого фото сохранятся.") != QMessageBox.Yes:
            return
        base = self.params.to_dict()
        for e in self.lib.entries:
            if e.path != str(self.src_path):
                own = EditParams.from_dict(e.params)
                d = copy.deepcopy(base)
                for k in GEOMETRY:
                    d[k] = getattr(own, k)
                e.params = d
        self.lib.save()
        self.status.setText(f"Настройки применены к {n} фото")

    def closeEvent(self, ev):
        if self.crop_mode:
            self.crop_btn.setChecked(False)
        self._save_edit()
        settings.put("geometry", bytes(self.saveGeometry().toBase64()).decode())
        self.strip.shutdown()
        for w in self._fprev_workers:
            w.requestInterruption()  # значки фильтров не нужно дорисовывать при закрытии
        for w in (*self._fprev_workers, self.worker, self.export_worker, self.hq_worker):
            if w and w.isRunning():
                w.wait(8000)
        super().closeEvent(ev)

    def load(self, path: Path):
        if self.crop_mode:
            self.canvas.crop = list(self._crop_backup)
            self.crop_btn.setChecked(False)
        self._save_edit()  # правки предыдущего снимка остаются в каталоге
        try:
            im, full_size = open_preview(path, PREVIEW_SIDE)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть файл:\n{e}")
            self.src_path = None
            return
        self.src_path, self._shown, self.full_size = path, path, full_size
        prev = im
        prev.thumbnail((PREVIEW_SIDE, PREVIEW_SIDE))
        self.preview = to_array(prev)
        small = prev.copy()
        small.thumbnail((SMALL_SIDE, SMALL_SIDE))
        self.preview_small = to_array(small) if max(small.size) < max(prev.size) else self.preview
        tiny = small.copy()
        tiny.thumbnail((TINY_SIDE, TINY_SIDE))
        self.preview_tiny = to_array(tiny) if max(tiny.size) < max(small.size) else self.preview_small
        self._before_key = None
        self._fprev.clear()  # значки фильтров зависят от фото
        self.curve.set_histogram(self.preview)
        e = self.lib.get(path)
        self.params = EditParams.from_dict(e.params) if e and e.params else EditParams()
        self.ftree.blockSignals(True)
        self.ftree.clearSelection()
        self.ftree.setCurrentItem(None)
        self.ftree.blockSignals(False)
        self.active_filter = None
        self._sync_ui()
        self._history_reset()
        self.render()
        self.canvas.fit()
        self._filter_list()  # перестроить дерево со значками на этом фото
        self.strip.select_path(path)
        self.setWindowTitle(f"Photo Editor AI — {path.name}")
        self.info.setText(f"{path.name}  ·  {self.full_size[0]}×{self.full_size[1]}")

    # ---------- показ и ИИ ----------
    def _fast_source(self) -> np.ndarray:
        """Копия для быстрого режима: самая крупная из тех, что укладываются в бюджет по замеренной скорости."""
        small = self.preview_small
        if self.preview_tiny is not small and self._cost_per_mpx * small.shape[0] * small.shape[1] / 1e6 > FAST_BUDGET:
            return self.preview_tiny
        return small

    def render(self, fast: bool = False):
        """Полный пересчёт показа. fast — по уменьшенной копии (для перетаскивания ползунков); без fast — чётко и сразу."""
        if self.preview is None:
            return
        self._hq_gen += 1  # всё, что считается в фоне, устарело
        if not fast:
            self._hq_timer.stop()
        src = self._fast_source() if fast else self.preview
        t0 = time.perf_counter()
        geo = adjust.apply_geometry(src, self.params, crop=not self.crop_mode)  # в режиме кадрирования фото показано целиком
        out = adjust.apply(geo, self.params)
        if fast:  # уточняем оценку скорости (скользящее среднее): тяжёлые фильтры переключат быстрый режим на меньшую копию
            cost = (time.perf_counter() - t0) / (src.shape[0] * src.shape[1] / 1e6)
            self._cost_per_mpx = 0.5 * self._cost_per_mpx + 0.5 * cost
        key = (id(src), self.params.rotate90, self.params.flip_h, self.params.flip_v, self.params.straighten, tuple(self.params.crop), self.crop_mode)
        if key != self._before_key:  # «до» — тот же кадр без цвета; пересчитываем только при смене геометрии
            self._before, self._before_key = self._qimage(geo), key
        self.canvas.source_width = round(geo.shape[1] * max(self.full_size) / max(src.shape[:2]))
        self.canvas.set_pair(self._before, self._qimage(out))
        self.canvas.set_overlay(clip_overlay(out) if self.clip_on else None)
        self.hist.set_image(out)
        self._zoom_changed()

    def _start_hq(self):
        """Чёткая перерисовка после паузы — в фоновом потоке. Если предыдущая ещё идёт, перезапустим по её окончании."""
        if self.preview is None:
            return
        if self.hq_worker and self.hq_worker.isRunning():
            self._hq_again = True
            return
        p = self.params
        key = (id(self.preview), p.rotate90, p.flip_h, p.flip_v, p.straighten, tuple(p.crop), self.crop_mode)
        self.hq_worker = HqWorker(self._hq_gen, key, self.preview, copy.deepcopy(p), self.crop_mode, key != self._before_key, max(self.full_size), self.clip_on)
        self.hq_worker.done.connect(self._hq_done)
        self.hq_worker.start()

    def _hq_done(self, gen: int, key, before, after, source_width: int, overlay):
        if gen == self._hq_gen and self.preview is not None:  # иначе пользователь уже изменил настройки: результат устарел
            if before is not None:
                self._before, self._before_key = before, key
            self.canvas.source_width = source_width
            self.canvas.set_pair(self._before, after)
            self.canvas.set_overlay(overlay)
            self._zoom_changed()
        if self._hq_again:
            self._hq_again = False
            self._hq_timer.start()

    def _zoom_changed(self):
        self.zoom_lbl.setText(f"{self.canvas.percent()}%" if self.canvas.after is not None else "")

    @staticmethod
    def _qimage(img: np.ndarray) -> QImage:
        return qimage_from_array(img)

    def auto_correct(self, mode: str):
        if self.preview is None:
            self.status.setText("Сначала откройте фото")
            return
        if self.worker and self.worker.isRunning():
            return
        mid = self.model_box.currentData()
        if not is_available(mid):  # модели нет на диске: предлагаем скачать (с проверкой контрольной суммы)
            spec = models()[mid]
            if not spec.url:
                self.status.setText(f"Для «{spec.name}» положите файл {spec.file} в папку models/")
                return
            if QMessageBox.question(self, "Скачать модель", f"Модель «{spec.name}» ещё не скачана ({spec.size_bytes / 1e6:.1f} МБ).\nСкачать с GitHub?") != QMessageBox.Yes:
                return
            self.status.setText("Скачиваю модель…")
            self.dl_worker = DownloadWorker(mid)
            self.dl_worker.progress.connect(lambda f, m: self.status.setText(f"Скачиваю модель… {m}"))
            self.dl_worker.done.connect(lambda m: (self._model_list(m), self.status.setText("Модель скачана"), self.auto_correct(mode)))
            self.dl_worker.failed.connect(lambda m: self.status.setText(f"Модель не скачана: {m}"))
            self.dl_worker.start()
            return
        for b in (self.auto_exp_btn, self.auto_full_btn, self.quick_auto):
            b.setEnabled(False)
        self.status.setText("ИИ анализирует кадр…")
        self.worker = AutoWorker(self.preview, self.model_box.currentData(), mode)
        self.worker.done.connect(self._auto_done)
        self.worker.failed.connect(self._auto_failed)
        self.worker.start()

    def _auto_failed(self, msg: str):
        for b in (self.auto_exp_btn, self.auto_full_btn, self.quick_auto):
            b.setEnabled(True)
        self.status.setText(f"Ошибка: {msg}")

    def _auto_done(self, sug: dict):
        for b in (self.auto_exp_btn, self.auto_full_btn, self.quick_auto):
            b.setEnabled(True)
        k = self.auto_strength.value() / 100
        for key in ("exposure", "temperature", "tint", "vibrance"):
            if key in sug:
                setattr(self.params, key, sug[key] * k)
        self._sync_ui()
        self.render()
        self._commit_timer.start()
        self.status.setText(f"Авто: {self.params.exposure:+.2f} EV" + (f", цвет {self.params.temperature:+.2f}/{self.params.tint:+.2f}" if "temperature" in sug else ""))

    # ---------- экспорт ----------
    def save_dialog(self):
        if self.full_size is None:
            self.status.setText("Нечего экспортировать: откройте фото")
            return
        if self.export_worker and self.export_worker.isRunning():
            self.status.setText("Экспорт уже идёт")
            return
        if self.crop_mode:
            self.crop_btn.setChecked(False)  # применить рамку до экспорта
        d = ExportDialog(self, self.src_path.with_name(self.src_path.stem + "_edit.jpg"))
        if not d.exec():
            return
        if d.target.exists() and QMessageBox.question(self, "Файл существует", f"Заменить {d.target.name}?") != QMessageBox.Yes:
            return
        self.status.setText("Экспорт…")
        self.export_worker = ExportWorker(self.src_path, copy.deepcopy(self.params), d.target, d.options)
        self.export_worker.done.connect(lambda p: self.status.setText(f"Сохранено: {Path(p).name}"))
        self.export_worker.failed.connect(lambda m: (self.status.setText("Ошибка экспорта"), QMessageBox.warning(self, "Экспорт не удался", m)))
        self.export_worker.start()
