from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QTimer, Qt

class VoiceDisplayWidget(QLabel):
    def __init__(self, parent, scalefactor, controller, debug_mode):
        super().__init__(parent)
        self.scalefactor = scalefactor
        self.controller = controller
        self.debug_mode = debug_mode
        x = 578 * self.scalefactor
        y = 440 * self.scalefactor
        width = 209 * self.scalefactor
        height = 296 * self.scalefactor
        self.setGeometry(int(x), int(y), int(width), int(height))
        font_size = int(24 * self.scalefactor)
        self.setStyleSheet(f"font-family: montserrat; font-size: {font_size}px; color: #A033B6; background: transparent; font-weight: bold;")
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        if self.debug_mode:
            self.setStyleSheet("border: 1px solid red; color: #A033B6; font-weight: bold; font-family: montserrat;")

        self.voice_timer = QTimer(self)
        self.voice_timer.timeout.connect(self._update_voice_text)
        self.voice_timer.start(200)

    def _update_voice_text(self):
        if self.debug_mode:
            self.setText("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt")
            return
        text = self.controller.get_listened_text()
        self.setText(text if text else "")
