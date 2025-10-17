import webbrowser
from pathlib import Path

from PyQt6.QtCore import QPoint, QRect, QRectF, QSize, Qt, QTimer
from PyQt6.QtGui import QColor, QKeyEvent, QMouseEvent, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QLabel, QWidget

from .controller import controller
from .widgets.buttons import MinimizeButton, CrossButton, PlainButton
from .widgets.vinyl import VinylWidget, ReaderWidget
from .widgets.panels import MacroPaneWidget, InfoBoxWidget, TextBoxWidget
from .widgets.voice_display import VoiceDisplayWidget
from .utils.helpers import load_svg


class MainMenuWindow(QWidget):
    def __init__(self, scalefactor, DebugMode):
        super().__init__()
        self.scalefactor = scalefactor
        self.DebugMode = DebugMode
        self.original_width = 1080 * self.scalefactor
        self.original_height = 813 * self.scalefactor
        self._drag_pos = QPoint()
        self.tab_toggled = False

        # Window setup
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(100, 100, int(self.original_width), int(self.original_height))

        # Initialize components
        self._init_bg()
        self._init_footer()
        self._init_tab()

        self.vinyl = VinylWidget(self, self.scalefactor, controller)
        self.reader = ReaderWidget(self, self.scalefactor)
        self.textbox = TextBoxWidget(self, self.scalefactor)
        self.macropane = MacroPaneWidget(self, self.scalefactor)
        self.infobox = InfoBoxWidget(self, self.scalefactor)

        self.min_button = MinimizeButton(self, self.scalefactor)
        self.cross_button = CrossButton(self, self.scalefactor)
        self.plain_button_1 = PlainButton(self, self.scalefactor, (794 * self.scalefactor, 5 * self.scalefactor))
        self.plain_button_2 = PlainButton(self, self.scalefactor, (160 * self.scalefactor, 631 * self.scalefactor))
        self.plain_button_3 = PlainButton(self, self.scalefactor, (100 * self.scalefactor, 631 * self.scalefactor))

        self.voice_display = VoiceDisplayWidget(self, self.scalefactor, controller, self.DebugMode)

        if self.DebugMode:
            self.background_label.setStyleSheet("border: 1px solid red;")
            self.footer_label.setStyleSheet("border: 1px solid red;")

    def _init_bg(self):
        self.background_label = QLabel(self)
        self.background_label.setGeometry(self.rect())
        self.background_label.lower()
        svg_file_bg = Path(__file__).parent / ".." / "assets" / "svg" / "MainMenuBG.svg"
        load_svg(str(svg_file_bg), self.background_label, self.size())

    def _init_footer(self):
        self.footer_label = QLabel(self)
        footer_width = 591 * self.scalefactor
        footer_height = 194 * self.scalefactor
        footer_x = 0
        footer_y = self.original_height - footer_height
        self.footer_label.setGeometry(int(footer_x), int(footer_y), int(footer_width), int(footer_height))
        self.footer_label.raise_()
        svg_file_footer = Path(__file__).parent / ".." / "assets" / "svg" / "MainMenuFooter.svg"
        load_svg(str(svg_file_footer), self.footer_label, QSize(int(footer_width), int(footer_height)))

        # Logo
        self.Logo_label = QLabel(self)
        Logo_width = 285 * self.scalefactor
        Logo_height = 52 * self.scalefactor
        Logo_x = 80
        Logo_y = self.original_height - Logo_height - 30
        self.Logo_label.setGeometry(int(Logo_x), int(Logo_y), int(Logo_width), int(Logo_height))
        self.Logo_label.raise_()
        svg_file_Logo = Path(__file__).parent / ".." / "assets" / "svg" / "Logo.svg"
        load_svg(str(svg_file_Logo), self.Logo_label, QSize(int(Logo_width), int(Logo_height)))
        self.Logo_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.Logo_label.mousePressEvent = self.open_link

    def _init_tab(self):
        self.tab_label = QLabel(self)
        tab_width = 190 * self.scalefactor
        tab_height = 158 * self.scalefactor
        self.original_tab_x = 817 * self.scalefactor
        tab_y = 272 * self.scalefactor
        self.tab_label.setGeometry(int(self.original_tab_x), int(tab_y), int(tab_width), int(tab_height))
        self.tab_label.lower()

        svg_file_tab = Path(__file__).parent / ".." / "assets" / "svg" / "MainMenuTab.svg"

        load_svg(str(svg_file_tab), self.tab_label, QSize(int(tab_width), int(tab_height)))
        self.tab_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tab_label.mousePressEvent = self.toggle_tab

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
        event.accept()

    def toggle_tab(self, event):
        if not self.tab_toggled:
            self.tab_label.move(int(self.original_tab_x - 20), self.tab_label.y())
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            self.tab_toggled = True
        else:
            self.tab_label.move(int(self.original_tab_x), self.tab_label.y())
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
            self.tab_toggled = False
        self.show()
        event.accept()