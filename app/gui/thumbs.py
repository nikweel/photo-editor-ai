from pathlib import Path

from PySide6.QtCore import QThread, Signal

from ..services.library import thumb_for


class ThumbWorker(QThread):
    """Готовит миниатюры по очереди, не блокируя окно."""
    ready = Signal(str, str)  # путь оригинала, путь миниатюры

    def __init__(self, paths: list[Path]):
        super().__init__()
        self.paths = paths

    def run(self):
        for p in self.paths:
            if self.isInterruptionRequested():
                return
            t = thumb_for(p)
            if t:
                self.ready.emit(str(p), str(t))
