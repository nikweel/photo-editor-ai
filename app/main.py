import logging
import os
import sys

from .utils.logging_setup import setup_logging


def selftest() -> int:
    """Проверка без окна: движок, все встроенные фильтры, Qt и ONNX Runtime. Годится для собранной программы и для CI."""
    import numpy as np
    import onnxruntime
    import PySide6

    from .core import adjust
    from .services.filters import BUILTIN, BUILTIN_PACKS

    img = np.random.default_rng(0).random((48, 64, 3)).astype(np.float32)
    for f in BUILTIN:
        out = adjust.render(img, f.params)
        if not (np.isfinite(out).all() and 0 <= out.min() and out.max() <= 1):
            print("FAIL: фильтр", f.name)
            return 1
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")  # окно не нужно: проверяем, что интерфейсные модули (в том числе значки SVG) на месте
    from PySide6.QtWidgets import QApplication

    from .gui import theme
    from .gui.canvas import CompareCanvas
    from .gui.icons import PATHS, icon
    from .gui.widgets import HistogramWidget, Section

    qapp = QApplication.instance() or QApplication([])
    theme.apply(qapp)
    for name in PATHS:
        if icon(name).pixmap(18, 18).isNull():
            print("FAIL: значок", name)
            return 1
    CompareCanvas(), HistogramWidget(), Section("проверка", True, lambda: None)
    print(f"OK: фильтров {len(BUILTIN)} в {len(BUILTIN_PACKS)} пакетах; значков {len(PATHS)}; PySide6 {PySide6.__version__}; ONNX Runtime {onnxruntime.__version__}")
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    setup_logging()
    try:
        from PySide6.QtWidgets import QApplication

        from .gui.main_window import MainWindow

        app = QApplication(sys.argv)
        app.setApplicationName("Photo Editor AI")
        app.setDesktopFileName("photo-editor-ai")  # связывает окно с .desktop-файлом и иконкой в системе
        from PySide6.QtGui import QIcon

        from .utils.paths import ICON

        if ICON.exists():
            app.setWindowIcon(QIcon(str(ICON)))
        from .gui import theme

        theme.apply(app)
        win = MainWindow(sys.argv[1] if len(sys.argv) > 1 else None)
        win.show()
        return app.exec()
    except Exception:
        logging.exception("Критическая ошибка")
        raise


if __name__ == "__main__":
    sys.exit(main())
