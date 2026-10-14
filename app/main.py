import logging
import sys

from .utils.logging_setup import setup_logging


def main() -> int:
    setup_logging()
    try:
        from PySide6.QtWidgets import QApplication

        from .gui.main_window import MainWindow

        app = QApplication(sys.argv)
        app.setApplicationName("Photo Editor AI")
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
