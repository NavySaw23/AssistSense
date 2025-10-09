from PyQt6.QtWidgets import QWidget, QLabel, QPushButton
from PyQt6.QtGui import QRegion, QKeyEvent, QMouseEvent, QPixmap, QPainter
from PyQt6.QtCore import Qt, QRect, QPoint, QSize, QRectF
from PyQt6.QtSvg import QSvgRenderer
from pathlib import Path  # NEW IMPORT
import webbrowser

class MainMenuWindow(QWidget):
    def __init__(self, scalefactor, DebugMode):
        super().__init__()
        
        self.original_width = 1080*scalefactor
        self.original_height = 813*scalefactor
        self._drag_pos = QPoint()
        
        # Window Setup (Frameless, Transparent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(100, 100, self.original_width, self.original_height)

        # SVG Background
        self.background_label = QLabel(self)
        self.background_label.setGeometry(self.rect())
        self.background_label.lower() 
        current_script_dir = Path(__file__).parent
        svg_file_bg = current_script_dir / ".." / "assets" / "svg" / "MainMenuBG.svg"
        self.load_svg(str(svg_file_bg), self.background_label, self.size())

        # SVG Footer
        self.footer_label = QLabel(self)
        footer_width = 591 * scalefactor 
        footer_height = 194 * scalefactor
        footer_x = 0
        footer_y = self.original_height - footer_height
        self.footer_label.setGeometry(int(footer_x), int(footer_y), int(footer_width), int(footer_height))
        self.footer_label.raise_()
        svg_file_footer = current_script_dir / ".." / "assets" / "svg" / "MainMenuFooter.svg"
        self.load_svg(str(svg_file_footer), self.footer_label, QSize(int(footer_width), int(footer_height)))
        self.footer_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.footer_label.mousePressEvent = self.open_link


        if DebugMode:
            self.background_label.setStyleSheet("border: 1px solid red;")
            self.footer_label.setStyleSheet("border: 1px solid red;")

    def open_link(self, event):
        webbrowser.open("https://github.com/NavySaw23/AssistSense")

    # render SVGs
    def load_svg(self, svg_path, label, size):
        renderer = QSvgRenderer(svg_path)
        
        if not renderer.isValid():
            print(f"Error: Could not load SVG file. Checked path: {Path(svg_path).resolve()}")
            return

        pixmap = QPixmap(size) 
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        target_rect = QRectF(0, 0, size.width(), size.height())
        renderer.render(painter, target_rect) 
        painter.end()

        #Set the pixmap (which has the visual shape)
        label.setPixmap(pixmap)
        if pixmap.hasAlphaChannel():
            mask = pixmap.mask() 
            label.setMask(mask) 
            
        label.setContentsMargins(0, 0, 0, 0)


    # Make Window Draggable
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    # Close Window on Esc
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)