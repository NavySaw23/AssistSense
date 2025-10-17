from pathlib import Path
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QSize, QRectF
from PyQt6.QtGui import QPixmap, QColor, QPainter
from PyQt6.QtSvg import QSvgRenderer

from app.utils.helpers import load_svg

class MinimizeButton(QLabel):
    def __init__(self, parent, scalefactor):
        super().__init__(parent)
        self.scalefactor = scalefactor
        width = 94 * self.scalefactor
        height = 50 * self.scalefactor
        x = 858 * self.scalefactor
        y = 5 * self.scalefactor
        self.setGeometry(int(x), int(y), int(width), int(height))
        self.svg_path = str(Path(__file__).parent.parent.parent / "assets" / "svg" / "Button_Min.svg")
        load_svg(self.svg_path, self, QSize(int(width), int(height)))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mousePressEvent = self.minimize_window
        self.enterEvent = self.button_enter
        self.leaveEvent = self.button_leave

    def minimize_window(self, event):
        self.parent().showMinimized()
        event.accept()

    def button_enter(self, event):
        size = self.pixmap().size()
        new_pixmap = QPixmap(size)
        new_pixmap.fill(QColor("#A033B6"))
        painter = QPainter(new_pixmap)
        renderer = QSvgRenderer(self.svg_path)
        renderer.render(painter, QRectF(0, 0, size.width(), size.height()))
        painter.end()
        self.setPixmap(new_pixmap)

    def button_leave(self, event):
        load_svg(self.svg_path, self, self.pixmap().size())

class CrossButton(QLabel):
    def __init__(self, parent, scalefactor):
        super().__init__(parent)
        self.scalefactor = scalefactor
        width = 94 * self.scalefactor
        height = 50 * self.scalefactor
        x = 921 * self.scalefactor
        y = 5 * self.scalefactor
        self.setGeometry(int(x), int(y), int(width), int(height))
        self.svg_path = str(Path(__file__).parent.parent.parent / "assets" / "svg" / "Button_Cross.svg")
        load_svg(self.svg_path, self, QSize(int(width), int(height)))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mousePressEvent = self.close_window
        self.enterEvent = self.button_enter
        self.leaveEvent = self.button_leave

    def close_window(self, event):
        self.parent().close()
        event.accept()

    def button_enter(self, event):
        size = self.pixmap().size()
        new_pixmap = QPixmap(size)
        new_pixmap.fill(QColor("#A033B6"))
        painter = QPainter(new_pixmap)
        renderer = QSvgRenderer(self.svg_path)
        renderer.render(painter, QRectF(0, 0, size.width(), size.height()))
        painter.end()
        self.setPixmap(new_pixmap)

    def button_leave(self, event):
        load_svg(self.svg_path, self, self.pixmap().size())

class PlainButton(QLabel):
    def __init__(self, parent, scalefactor, position):
        super().__init__(parent)
        self.scalefactor = scalefactor
        width = 94 * self.scalefactor
        height = 50 * self.scalefactor
        self.setGeometry(int(position[0]), int(position[1]), int(width), int(height))
        svg_path = str(Path(__file__).parent.parent.parent / "assets" / "svg" / "Button_Plain.svg")
        load_svg(svg_path, self, QSize(int(width), int(height)))
