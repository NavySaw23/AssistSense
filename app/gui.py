import webbrowser
from pathlib import Path

from PyQt6.QtCore import QPoint, QRect, QRectF, QSize, Qt, QTimer
from PyQt6.QtGui import QColor, QKeyEvent, QMouseEvent, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QLabel, QWidget

from .controller import controller 


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

        self._init_vinyl()
        self._init_reader()
        self._init_TextBox()

        self._init_MacroPane()
        self._init_InfoBox()

        self._init_Button_Min()
        self._init_Button_Cross()
        self._init_Button_Plain()

        self._init_voice_text_display()


        if self.DebugMode:
            self.background_label.setStyleSheet("border: 1px solid red;")
            self.footer_label.setStyleSheet("border: 1px solid red;")
            self.vinyl_label.setStyleSheet("border: 1px solid red;")
            self.reader_label.setStyleSheet("border: 1px solid red;")
            self.tab_label.setStyleSheet("border: 1px solid red;")


        # Vinyl rotation setup
        self.vinyl_rotation_angle = 0
        self.vinyl_rotation_timer = QTimer(self)
        self.vinyl_rotation_timer.timeout.connect(self._rotate_vinyl)

        self.reader_rotation_angle = 0
        self.is_listening_prev_state = -1

        self.listening_check_timer = QTimer(self)
        self.listening_check_timer.timeout.connect(self._check_listening_status)
        self.listening_check_timer.start(200)


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

    def _init_tab(self):
        self.tab_label = QLabel(self)
        tab_width = 190 * self.scalefactor
        tab_height = 158 * self.scalefactor
        self.original_tab_x = 817 * self.scalefactor
        tab_y = 272 * self.scalefactor
        self.tab_label.setGeometry(int(self.original_tab_x), int(tab_y), int(tab_width), int(tab_height))
        self.tab_label.lower()

        svg_file_tab = Path(__file__).parent / ".." / "assets" / "svg" / "MainMenuTab.svg" 
        
        self.load_svg(str(svg_file_tab), self.tab_label, QSize(int(tab_width), int(tab_height)))
        self.tab_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tab_label.mousePressEvent = self.toggle_tab

    def _init_vinyl(self):
        self.vinyl_label = QLabel(self)
        vinyl_size = int(275 * self.scalefactor)
        vinyl_x = 804 * self.scalefactor
        vinyl_y = 500 * self.scalefactor
        self.vinyl_label.setGeometry(int(vinyl_x), int(vinyl_y), int(vinyl_size), int(vinyl_size))
        self.svg_file_vinyl = Path(__file__).parent / ".." / "assets" / "svg" / "Vinyl.svg"
        self.load_svg(str(self.svg_file_vinyl), self.vinyl_label, QSize(vinyl_size, vinyl_size))

    def _init_reader(self):
            self.reader_label = QLabel(self)
            reader_size = int(160 * self.scalefactor)
            reader_x = int(790 * self.scalefactor)
            reader_y = int(380 * self.scalefactor)
            self.reader_label.raise_()
            self.reader_label.setGeometry(reader_x, reader_y, reader_size, reader_size)
            self.svg_file_reader = Path(__file__).parent / ".." / "assets" / "svg" / "Reader.svg"
            self.load_svg(str(self.svg_file_reader), self.reader_label, QSize(reader_size, reader_size))
            self.reader_rotation_angle = 0
            self._update_reader_pixmap()



    def _init_TextBox(self):
        self.TextBox_label = QLabel(self)
        TextBox_width = 354 * self.scalefactor
        TextBox_height = 401 * self.scalefactor
        TextBox_x = 526 * self.scalefactor
        TextBox_y = 348 * self.scalefactor
        self.TextBox_label.setGeometry(TextBox_x, TextBox_y, int(TextBox_width), int(TextBox_height))
        svg_file_TextBox = Path(__file__).parent / ".." / "assets" / "svg" / "TextBox.svg"
        self.load_svg(str(svg_file_TextBox), self.TextBox_label, QSize(TextBox_width, TextBox_height))

    def _init_MacroPane(self):
            self.MacroPane_label = QLabel(self)
            MacroPane_width = 389 * self.scalefactor
            MacroPane_height = 541 * self.scalefactor
            MacroPane_x = 99 * self.scalefactor
            MacroPane_y = 57 * self.scalefactor
            self.MacroPane_label.setGeometry(int(MacroPane_x), int(MacroPane_y), int(MacroPane_width), int(MacroPane_height))
            svg_file_MacroPane = Path(__file__).parent / ".." / "assets" / "svg" / "MacroPane.svg"
            self.load_svg(str(svg_file_MacroPane), self.MacroPane_label, QSize(int(MacroPane_width), int(MacroPane_height)))

    def _init_InfoBox(self):
            self.InfoBox_label = QLabel(self)
            InfoBox_width = 460 * self.scalefactor
            InfoBox_height = 222 * self.scalefactor
            InfoBox_x = 524 * self.scalefactor
            InfoBox_y = 85 * self.scalefactor
            self.InfoBox_label.setGeometry(int(InfoBox_x), int(InfoBox_y), int(InfoBox_width), int(InfoBox_height))
            svg_file_InfoBox = Path(__file__).parent / ".." / "assets" / "svg" / "InfoBox.svg"
            self.load_svg(str(svg_file_InfoBox), self.InfoBox_label, QSize(int(InfoBox_width), int(InfoBox_height)))


    # -------------- Buttons --------------

    def _init_Button_Min(self):
        self.Button_Min_label = QLabel(self)
        Button_Min_width = 94 * self.scalefactor
        Button_Min_height = 50 * self.scalefactor
        Button_Min_x = 858 * self.scalefactor
        Button_Min_y = 5 *  self.scalefactor
        self.Button_Min_label.setGeometry(int(Button_Min_x), int(Button_Min_y), int(Button_Min_width), int(Button_Min_height))
        svg_file_Button_Min = Path(__file__).parent / ".." / "assets" / "svg" / "Button_Min.svg"
        self.load_svg(str(svg_file_Button_Min), self.Button_Min_label, QSize(Button_Min_width, Button_Min_height))

        self.Button_Min_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.Button_Min_label.mousePressEvent = self.minimize_window
        self.Button_Min_label.enterEvent = self.button_min_enter
        self.Button_Min_label.leaveEvent = self.button_min_leave

    def _init_Button_Cross(self):
        self.Button_Cross_label = QLabel(self)
        Button_Cross_width = 94 * self.scalefactor
        Button_Cross_height = 50 * self.scalefactor
        Button_Cross_x = 921 * self.scalefactor
        Button_Cross_y = 5 *  self.scalefactor
        self.Button_Cross_label.setGeometry(int(Button_Cross_x), int(Button_Cross_y), int(Button_Cross_width), int(Button_Cross_height))
        svg_file_Button_Cross = Path(__file__).parent / ".." / "assets" / "svg" / "Button_Cross.svg"
        self.load_svg(str(svg_file_Button_Cross), self.Button_Cross_label, QSize(Button_Cross_width, Button_Cross_height))

        self.Button_Cross_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.Button_Cross_label.mousePressEvent = self.close_window
        self.Button_Cross_label.enterEvent = self.button_cross_enter
        self.Button_Cross_label.leaveEvent = self.button_cross_leave

    def minimize_window(self, event):
        self.showMinimized()
        event.accept()

    def close_window(self, event):
        self.close()
        event.accept()

    def button_min_enter(self, event):
        size = self.Button_Min_label.pixmap().size()
        new_pixmap = QPixmap(size)
        new_pixmap.fill(QColor("#A033B6"))
        painter = QPainter(new_pixmap)
        renderer = QSvgRenderer(str(Path(__file__).parent / ".." / "assets" / "svg" / "Button_Min.svg"))
        renderer.render(painter, QRectF(0, 0, size.width(), size.height()))
        painter.end()
        self.Button_Min_label.setPixmap(new_pixmap)

    def button_min_leave(self, event):
        svg_file_Button_Min = Path(__file__).parent / ".." / "assets" / "svg" / "Button_Min.svg"
        self.load_svg(str(svg_file_Button_Min), self.Button_Min_label, self.Button_Min_label.pixmap().size())

    def button_cross_enter(self, event):
        size = self.Button_Cross_label.pixmap().size()
        new_pixmap = QPixmap(size)
        new_pixmap.fill(QColor("#A033B6"))
        painter = QPainter(new_pixmap)
        renderer = QSvgRenderer(str(Path(__file__).parent / ".." / "assets" / "svg" / "Button_Cross.svg"))
        renderer.render(painter, QRectF(0, 0, size.width(), size.height()))
        painter.end()
        self.Button_Cross_label.setPixmap(new_pixmap)

    def button_cross_leave(self, event):
        svg_file_Button_Cross = Path(__file__).parent / ".." / "assets" / "svg" / "Button_Cross.svg"
        self.load_svg(str(svg_file_Button_Cross), self.Button_Cross_label, self.Button_Cross_label.pixmap().size())

    def _init_Button_Plain(self):
        Button_Plain_width = 94 * self.scalefactor
        Button_Plain_height = 50 * self.scalefactor
        svg_file_Button_Plain = Path(__file__).parent / ".." / "assets" / "svg" / "Button_Plain.svg"

        # Button 1
        self.Button_Plain_label_1 = QLabel(self)
        Button_Plain_x_1 = 794 * self.scalefactor
        Button_Plain_y_1 = 5 * self.scalefactor
        self.Button_Plain_label_1.setGeometry(int(Button_Plain_x_1), int(Button_Plain_y_1), int(Button_Plain_width), int(Button_Plain_height))
        self.load_svg(str(svg_file_Button_Plain), self.Button_Plain_label_1, QSize(int(Button_Plain_width), int(Button_Plain_height)))

        # Button 2
        self.Button_Plain_label_2 = QLabel(self)
        Button_Plain_x_2 = 160 * self.scalefactor
        Button_Plain_y_2 = 631 * self.scalefactor
        self.Button_Plain_label_2.setGeometry(int(Button_Plain_x_2), int(Button_Plain_y_2), int(Button_Plain_width), int(Button_Plain_height))
        self.load_svg(str(svg_file_Button_Plain), self.Button_Plain_label_2, QSize(int(Button_Plain_width), int(Button_Plain_height)))

        # Button 3
        self.Button_Plain_label_3 = QLabel(self)
        Button_Plain_x_3 = 100 * self.scalefactor
        Button_Plain_y_3 = 631 * self.scalefactor
        self.Button_Plain_label_3.setGeometry(int(Button_Plain_x_3), int(Button_Plain_y_3), int(Button_Plain_width), int(Button_Plain_height))
        self.load_svg(str(svg_file_Button_Plain), self.Button_Plain_label_3, QSize(int(Button_Plain_width), int(Button_Plain_height)))




    # -------------- VOICE TO TEXT --------------
    def _init_voice_text_display(self):
        self.voice_text_label = QLabel(self)
        self.voice_text_label.setGeometry(578*self.scalefactor, 440*self.scalefactor, 209*self.scalefactor, 296*self.scalefactor)
        font_size = int(24 * self.scalefactor)
        self.voice_text_label.setStyleSheet(f"font-family: montserrat; font-size: {font_size}px; color: #A033B6; background: transparent; font-weight: bold;")
        self.voice_text_label.setWordWrap(True)
        self.voice_text_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)


        if self.DebugMode:
            self.voice_text_label.setStyleSheet("border: 1px solid red; color: #A033B6; font-weight: bold; font-family: montserrat;")

        self.voice_timer = QTimer(self)
        self.voice_timer.timeout.connect(self._update_voice_text)
        self.voice_timer.start(200)

    def _update_voice_text(self):
        if self.DebugMode:
            self.voice_text_label.setText("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt")
            return
        text = controller.get_listened_text()
        self.voice_text_label.setText(text if text else "")

    def _check_listening_status(self):
        try:
            is_listening = int(controller.is_listening())
        except AttributeError:
            is_listening = int(bool(controller.get_listened_text()))

        if is_listening != self.is_listening_prev_state:
            if is_listening:
                if not self.vinyl_rotation_timer.isActive():
                    self.vinyl_rotation_timer.start(30)
                

            else:
                if self.vinyl_rotation_timer.isActive():
                    self.vinyl_rotation_timer.stop()
                    self._reset_vinyl_rotation()
                
            
            self.is_listening_prev_state = is_listening

    def _rotate_vinyl(self):
        self.vinyl_rotation_angle = (self.vinyl_rotation_angle + 2) % 360
        self._update_vinyl_pixmap()

    def _reset_vinyl_rotation(self):
        self.vinyl_rotation_angle = 0
        self._update_vinyl_pixmap()

    def _update_vinyl_pixmap(self):
        size = self.vinyl_label.size()
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.translate(size.width() / 2, size.height() / 2)
        painter.rotate(self.vinyl_rotation_angle)
        painter.translate(-size.width() / 2, -size.height() / 2)
        
        renderer = QSvgRenderer(str(self.svg_file_vinyl))
        renderer.render(painter, QRectF(0, 0, size.width(), size.height()))
        painter.end()

        self.vinyl_label.setPixmap(pixmap)

    def _update_reader_pixmap(self):
        size = self.reader_label.size()
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.translate(size.width() / 2, size.height() / 2)
        painter.rotate(self.reader_rotation_angle)
        painter.translate(-size.width() / 2, -size.height() / 2)
        
        renderer = QSvgRenderer(str(self.svg_file_reader))
        renderer.render(painter, QRectF(0, 0, size.width(), size.height()))
        painter.end()

        self.reader_label.setPixmap(pixmap)



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
