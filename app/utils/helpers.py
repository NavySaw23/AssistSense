from pathlib import Path

from PyQt6.QtCore import QRectF, Qt, QByteArray
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

def load_svg_with_shadow(svg_path, label, size):
    with open(svg_path, 'r') as f:
        svg_content = f.read()

    shadow_filter = '''
    <defs>
        <filter id="drop_shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feOffset result="offOut" in="SourceAlpha" dx="-5" dy="5" />
            <feGaussianBlur result="blurOut" in="offOut" stdDeviation="5" />
            <feBlend in="SourceGraphic" in2="blurOut" mode="normal" />
        </filter>
    </defs>
    '''

    # Find the svg tag and add the filter
    svg_tag_end = svg_content.find('>')
    svg_content = svg_content[:svg_tag_end+1] + shadow_filter + svg_content[svg_tag_end+1:]

    # Find the root graphic tag and apply the filter
    # This is a bit of a hack, we assume the first <g> or <path> is the root graphic
    for tag in ['<g', '<path', '<rect', '<circle', '<ellipse', '<polygon', '<polyline', '<line']:
        if tag in svg_content:
            svg_content = svg_content.replace(tag, tag + ' filter="url(#drop_shadow)"', 1)
            break

    renderer = QSvgRenderer(QByteArray(svg_content.encode('utf-8')))
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