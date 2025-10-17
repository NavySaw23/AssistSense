from pathlib import Path
from PyQt6.QtCore import QTimer, QRectF, QSize, Qt
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QLabel

from app.utils.helpers import load_svg

class VinylWidget(QLabel):
    def __init__(self, parent, scalefactor, controller):
        super().__init__(parent)
        self.scalefactor = scalefactor
        self.controller = controller
        size = int(275 * self.scalefactor)
        x = 804 * self.scalefactor
        y = 500 * self.scalefactor
        self.setGeometry(int(x), int(y), int(size), int(size))
        self.svg_file_vinyl = str(Path(__file__).parent.parent.parent / "assets" / "svg" / "Vinyl.svg")
        load_svg(self.svg_file_vinyl, self, QSize(size, size))

        self.rotation_angle = 0
        self.rotation_timer = QTimer(self)
        self.rotation_timer.timeout.connect(self._rotate)

        self.is_listening_prev_state = -1
        self.listening_check_timer = QTimer(self)
        self.listening_check_timer.timeout.connect(self._check_listening_status)
        self.listening_check_timer.start(200)

    def _check_listening_status(self):
        try:
            is_listening = int(self.controller.is_listening())
        except AttributeError:
            is_listening = int(bool(self.controller.get_listened_text()))

        if is_listening != self.is_listening_prev_state:
            if is_listening:
                if not self.rotation_timer.isActive():
                    self.rotation_timer.start(30)
            else:
                if self.rotation_timer.isActive():
                    self.rotation_timer.stop()
                    self._reset_rotation()
            self.is_listening_prev_state = is_listening

    def _rotate(self):
        self.rotation_angle = (self.rotation_angle + 2) % 360
        self._update_pixmap()

    def _reset_rotation(self):
        self.rotation_angle = 0
        self._update_pixmap()

    def _update_pixmap(self):
        size = self.size()
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.translate(size.width() / 2, size.height() / 2)
        painter.rotate(self.rotation_angle)
        painter.translate(-size.width() / 2, -size.height() / 2)
        renderer = QSvgRenderer(self.svg_file_vinyl)
        renderer.render(painter, QRectF(0, 0, size.width(), size.height()))
        painter.end()
        self.setPixmap(pixmap)

class ReaderWidget(QLabel):
    def __init__(self, parent, scalefactor):
        super().__init__(parent)
        self.scalefactor = scalefactor
        size = int(160 * self.scalefactor)
        x = int(790 * self.scalefactor)
        y = int(380 * self.scalefactor)
        self.setGeometry(x, y, size, size)
        self.svg_file_reader = str(Path(__file__).parent.parent.parent / "assets" / "svg" / "Reader.svg")
        load_svg(self.svg_file_reader, self, QSize(size, size))
        self.rotation_angle = 0
        self._update_pixmap()

    def _update_pixmap(self):
        size = self.size()
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.translate(size.width() / 2, size.height() / 2)
        painter.rotate(self.rotation_angle)
        painter.translate(-size.width() / 2, -size.height() / 2)
        renderer = QSvgRenderer(self.svg_file_reader)
        renderer.render(painter, QRectF(0, 0, size.width(), size.height()))
        painter.end()
        self.setPixmap(pixmap)
