from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtGui import QRegion, QKeyEvent, QMouseEvent, QPixmap, QPainter
from PyQt6.QtCore import Qt, QRect, QPoint, QSize, QRectF, QTimer
from PyQt6.QtSvg import QSvgRenderer
from pathlib import Path
# from voiceRecog import VoiceListener

import webbrowser

class MainMenuWindow(QWidget):
    def __init__(self, scalefactor, DebugMode):
        super().__init__()
        
        self.scalefactor = scalefactor
        self.DebugMode = DebugMode
        self.original_width = 1080*self.scalefactor
        self.original_height = 813*self.scalefactor
        self._drag_pos = QPoint()
        
        # Window Setup (Frameless, Transparent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(100, 100, self.original_width, self.original_height)

        self._init_bg()
        self._init_footer()
        self._init_vinyl()
        
        #debugmode config
        if self.DebugMode:
            self.background_label.setStyleSheet("border: 1px solid red;")
            self.footer_label.setStyleSheet("border: 1px solid red;")
            self.vinyl_label.setStyleSheet("border: 1px solid red;")

    #----Elements----------------------------------------------
    def _init_bg(self):
        self.background_label = QLabel(self)
        self.background_label.setGeometry(self.rect())
        self.background_label.lower() 
        current_script_dir = Path(__file__).parent
        svg_file_bg = current_script_dir / ".." / "assets" / "svg" / "MainMenuBG.svg"
        self.load_svg(str(svg_file_bg), self.background_label, self.size())

    def _init_footer(self):
        self.footer_label = QLabel(self)
        footer_width = 591 * self.scalefactor 
        footer_height = 194 * self.scalefactor
        footer_x = 0
        footer_y = self.original_height - footer_height
        self.footer_label.setGeometry(int(footer_x), int(footer_y), int(footer_width), int(footer_height))
        self.footer_label.raise_()
        current_script_dir = Path(__file__).parent
        svg_file_footer = current_script_dir / ".." / "assets" / "svg" / "MainMenuFooter.svg"
        self.load_svg(str(svg_file_footer), self.footer_label, QSize(int(footer_width), int(footer_height)))

        # SVG Logo
        self.Logo_label = QLabel(self)
        Logo_width = 285 * self.scalefactor 
        Logo_height = 52 * self.scalefactor
        Logo_x = 80
        Logo_y = self.original_height - Logo_height - 30
        self.Logo_label.setGeometry(int(Logo_x), int(Logo_y), int(Logo_width), int(Logo_height))
        self.Logo_label.raise_()
        svg_file_Logo = current_script_dir / ".." / "assets" / "svg" / "Logo.svg"
        self.load_svg(str(svg_file_Logo), self.Logo_label, QSize(int(Logo_width), int(Logo_height)))
        self.Logo_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.Logo_label.mousePressEvent = self.open_link

    def _init_vinyl(self):
        #vinyl
        self.vinyl_label = QLabel(self)
        vinyl_width = 275 * self.scalefactor 
        vinyl_height = 275 * self.scalefactor
        vinyl_x = self.original_width - vinyl_width
        vinyl_y = self.original_height - vinyl_height
        self.vinyl_label.setGeometry(int(vinyl_x), int(vinyl_y), int(vinyl_width), int(vinyl_height))
        self.vinyl_label.raise_()
        current_script_dir = Path(__file__).parent
        svg_file_vinyl = current_script_dir / ".." / "assets" / "svg" / "Vinyl.svg"
        self.load_svg(str(svg_file_vinyl), self.vinyl_label, QSize(int(vinyl_width), int(vinyl_height)))
        
        #vinyl playing overlay 
        self.vinylcharge_label = QLabel(self)
        vinylcharge_width = 275 * self.scalefactor
        vinylcharge_height = 275 * self.scalefactor
        vinylcharge_x = self.original_width - vinylcharge_width
        vinylcharge_y = self.original_height - vinylcharge_height
        self.vinylcharge_label.setGeometry(int(vinylcharge_x), int(vinylcharge_y), int(vinylcharge_width), int(vinylcharge_height))
        self.vinylcharge_label.raise_()
        current_script_dir = Path(__file__).parent
        svg_file_vinylcharge = current_script_dir / ".." / "assets" / "svg" / "VinylCharge.svg" # Assuming you also rename the SVG file
        self.load_svg(str(svg_file_vinylcharge), self.vinylcharge_label, QSize(int(vinylcharge_width), int(vinylcharge_height)))

        shadow = QGraphicsDropShadowEffect()
        shadow.setColor
        shadow.setBlurRadius(15)
        shadow.setXOffset(-2)
        shadow.setYOffset(-2)
        self.vinyl_label.setGraphicsEffect(shadow)

        


    #----Helpers----------------------------------------------
    
    # render SVGs with masks
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
    
    def open_link(self, event):
        webbrowser.open("https://github.com/NavySaw23/AssistSense")