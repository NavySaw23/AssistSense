import webbrowser
from pathlib import Path

from PyQt6.QtCore import QPoint, QRect, QRectF, QSize, Qt, QTimer
from PyQt6.QtGui import QKeyEvent, QMouseEvent, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QLabel, QWidget

from .controller import controller  # <-- import the singleton controller


class MainMenuWindow(QWidget):
    def __init__(self, scalefactor, DebugMode):
        super().__init__()
        self.scalefactor = scalefactor
        self.DebugMode = DebugMode
        self.original_width = 1080 * self.scalefactor
        self.original_height = 813 * self.scalefactor
        self._drag_pos = QPoint()

        # Window setup
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(100, 100, int(self.original_width), int(self.original_height))

        # Initialize components
        self._init_bg()
        self._init_footer()
        self._init_vinyl()

        if self.DebugMode:
            self.background_label.setStyleSheet("border: 1px solid red;")
            self.footer_label.setStyleSheet("border: 1px solid red;")
            self.vinyl_label.setStyleSheet("border: 1px solid red;")

        # Initialize vinyl rotation & voice recognition display
        self._init_vinyl_rotation()
        self._init_voice_text_display()

    # ---------------- INIT ELEMENTS ----------------

    def _init_bg(self):
        self.background_label = QLabel(self)
        self.background_label.setGeometry(self.rect())
        self.background_label.lower()
        svg_file_bg = Path(__file__).parent / ".." / "assets" / "svg" / "MainMenuBG.svg"
        self.load_svg(str(svg_file_bg), self.background_label, self.size())

    def _init_footer(self):
        self.footer_label = QLabel(self)
        footer_width = 591 * self.scalefactor
        footer_height = 194 * self.scalefactor
        footer_x = 0
        footer_y = self.original_height - footer_height
        self.footer_label.setGeometry(int(footer_x), int(footer_y), int(footer_width), int(footer_height))
        self.footer_label.raise_()
        svg_file_footer = Path(__file__).parent / ".." / "assets" / "svg" / "MainMenuFooter.svg"
        self.load_svg(str(svg_file_footer), self.footer_label, QSize(int(footer_width), int(footer_height)))

        # Logo
        self.Logo_label = QLabel(self)
        Logo_width = 285 * self.scalefactor
        Logo_height = 52 * self.scalefactor
        Logo_x = 80
        Logo_y = self.original_height - Logo_height - 30
        self.Logo_label.setGeometry(int(Logo_x), int(Logo_y), int(Logo_width), int(Logo_height))
        self.Logo_label.raise_()
        svg_file_Logo = Path(__file__).parent / ".." / "assets" / "svg" / "Logo.svg"
        self.load_svg(str(svg_file_Logo), self.Logo_label, QSize(int(Logo_width), int(Logo_height)))
        self.Logo_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.Logo_label.mousePressEvent = self.open_link

    def _init_vinyl(self):
        # Main vinyl
        self.vinyl_label = QLabel(self)
        vinyl_size = int(275 * self.scalefactor)
        vinyl_x = self.original_width - vinyl_size
        vinyl_y = self.original_height - vinyl_size
        self.vinyl_label.setGeometry(int(vinyl_x), int(vinyl_y), int(vinyl_size), int(vinyl_size))
        svg_file_vinyl = Path(__file__).parent / ".." / "assets" / "svg" / "Vinyl.svg"
        self.load_svg(str(svg_file_vinyl), self.vinyl_label, QSize(vinyl_size, vinyl_size))

        # Vinyl charge overlay
        self.vinylcharge_label = QLabel(self)
        self.vinylcharge_label.setGeometry(int(vinyl_x), int(vinyl_y), int(vinyl_size), int(vinyl_size))
        svg_file_vinylcharge = Path(__file__).parent / ".." / "assets" / "svg" / "VinylCharge.svg"
        self.load_svg(str(svg_file_vinylcharge), self.vinylcharge_label, QSize(vinyl_size, vinyl_size))
        self.vinylcharge_label.raise_()

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(-2)
        shadow.setYOffset(-2)
        self.vinyl_label.setGraphicsEffect(shadow)

    # ---------------- VINYL ROTATION ----------------

    def _init_vinyl_rotation(self):
        self.rotation_timer = QTimer(self)
        self.rotation_timer.timeout.connect(self._update_vinyl_state)
        self.rotation_timer.start(100)  # poll every 100ms

    def _update_vinyl_state(self):
        if controller.is_listening():
            self._start_vinyl_rotation()
        else:
            self._stop_vinyl_rotation()

    def _start_vinyl_rotation(self):
        # You can replace this with actual QPixmap rotation later
        self.vinyl_label.setStyleSheet("border: 2px solid green;")

    def _stop_vinyl_rotation(self):
        self.vinyl_label.setStyleSheet("border: 1px solid red;")

    # ---------------- VOICE TEXT ----------------

    def _init_voice_text_display(self):
        self.voice_text_label = QLabel(self)
        self.voice_text_label.setGeometry(int((self.original_width/2)-20), int(self.original_height-110), 900, 42)
        self.voice_text_label.setStyleSheet("font-size: 18px; color: black; background: transparent;")
        self.voice_timer = QTimer(self)
        self.voice_timer.timeout.connect(self._update_voice_text)
        self.voice_timer.start(200)

    def _update_voice_text(self):
        text = controller.get_listened_text()
        self.voice_text_label.setText(text if text else "")

    # ---------------- HELPERS ----------------

    def load_svg(self, svg_path, label, size):
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

    # ---------------- INTERACTIONS ----------------

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def open_link(self, event):
        webbrowser.open("https://github.com/NavySaw23/AssistSense")
