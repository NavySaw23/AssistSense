"""
Post-recording trigger configuration dialog.
After a macro is recorded, this dialog lets the user choose:
- Voice command (e.g., "youtube mode")
- Keyboard shortcut (e.g., "Ctrl+Alt+Y")
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt


class TriggerConfigDialog(QDialog):
    """Dialog to configure trigger type and value for a macro."""

    def __init__(self, macro_name: str, parent=None):
        super().__init__(parent)
        self.macro_name = macro_name
        self.trigger_type = None
        self.trigger_value = None
        self.init_ui()

    def init_ui(self):
        """Initialize UI components."""
        self.setWindowTitle("Configure Macro Trigger")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        # Title
        title = QLabel(f"Configure trigger for: {self.macro_name}")
        layout.addWidget(title)

        # Trigger type selection
        type_layout = QHBoxLayout()
        type_label = QLabel("Trigger Type:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["voice", "keyboard_shortcut", "gesture"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)

        # Trigger value input
        value_layout = QHBoxLayout()
        self.value_label = QLabel("Voice Command:")
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("e.g., youtube mode")
        value_layout.addWidget(self.value_label)
        value_layout.addWidget(self.value_input)
        layout.addLayout(value_layout)

        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Macro")
        save_btn.clicked.connect(self.save_trigger)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def on_type_changed(self, new_type: str):
        """Update label and placeholder when trigger type changes."""
        if new_type == "voice":
            self.value_label.setText("Voice Command:")
            self.value_input.setPlaceholderText("e.g., youtube mode")
        elif new_type == "keyboard_shortcut":
            self.value_label.setText("Keyboard Shortcut:")
            self.value_input.setPlaceholderText("e.g., Ctrl+Alt+Y")
        elif new_type == "gesture":
            self.value_label.setText("Gesture:")
            self.value_input.setPlaceholderText("e.g., swipe_up")

    def save_trigger(self):
        """Validate and save trigger configuration."""
        trigger_type = self.type_combo.currentText()
        trigger_value = self.value_input.text().strip()

        if not trigger_value:
            QMessageBox.warning(self, "Input Error", "Please enter a trigger value.")
            return

        self.trigger_type = trigger_type
        self.trigger_value = trigger_value
        self.accept()

    def get_trigger_info(self) -> dict:
        """Return the configured trigger info."""
        return {
            "type": self.trigger_type,
            "value": self.trigger_value
        }
