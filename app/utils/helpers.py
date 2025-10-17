from pathlib import Path

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer


def load_svg(svg_path, label, size):
    renderer = QSvgRenderer(svg_path)
    if not renderer.isValid():
        print(f"Error: Could not load SVG file. Checked path: {Path(svg_path).resolve()}")
        return

    pixmap = QPixmap(size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter, QRectF(0, 0, size.width(), size.height()))
    painter.end()
    label.setPixmap(pixmap)
    if pixmap.hasAlphaChannel():
        label.setMask(pixmap.mask())
    label.setContentsMargins(0, 0, 0, 0)