from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QSize
from app.utils.helpers import load_svg

class BaseWidget(QLabel):
    def __init__(self, parent, svg_path, size, position):
        super().__init__(parent)
        self.setGeometry(position[0], position[1], size[0], size[1])
        load_svg(svg_path, self, QSize(size[0], size[1]))
