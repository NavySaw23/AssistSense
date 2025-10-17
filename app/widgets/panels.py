from pathlib import Path
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QSize

from app.utils.helpers import load_svg

class MacroPaneWidget(QLabel):
    def __init__(self, parent, scalefactor):
        super().__init__(parent)
        width = 389 * scalefactor
        height = 541 * scalefactor
        x = 99 * scalefactor
        y = 57 * scalefactor
        self.setGeometry(int(x), int(y), int(width), int(height))
        svg_path = str(Path(__file__).parent.parent.parent / "assets" / "svg" / "MacroPane.svg")
        load_svg(svg_path, self, QSize(int(width), int(height)))

class InfoBoxWidget(QLabel):
    def __init__(self, parent, scalefactor):
        super().__init__(parent)
        width = 460 * scalefactor
        height = 222 * scalefactor
        x = 524 * scalefactor
        y = 85 * scalefactor
        self.setGeometry(int(x), int(y), int(width), int(height))
        svg_path = str(Path(__file__).parent.parent.parent / "assets" / "svg" / "InfoBox.svg")
        load_svg(svg_path, self, QSize(int(width), int(height)))

class TextBoxWidget(QLabel):
    def __init__(self, parent, scalefactor):
        super().__init__(parent)
        width = 354 * scalefactor
        height = 401 * scalefactor
        x = 526 * scalefactor
        y = 348 * scalefactor
        self.setGeometry(int(x), int(y), int(width), int(height))
        svg_path = str(Path(__file__).parent.parent.parent / "assets" / "svg" / "TextBox.svg")
        load_svg(svg_path, self, QSize(int(width), int(height)))
