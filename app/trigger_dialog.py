"""
Post-recording trigger configuration dialog.
This dialog reuses the TriggerEditor from the main macro manager GUI
to provide a consistent and up-to-date UI for all trigger types.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QFrame
)
# Reuse the comprehensive TriggerEditor from the main GUI
from app.macro_manager_gui import TriggerEditor


class TriggerConfigDialog(QDialog):
    """Dialog to configure trigger type and value for a macro."""

    def __init__(self, macro_name: str, parent=None):
        super().__init__(parent)
        self.macro_name = macro_name
        self.trigger_info = None
        self.init_ui()

    def init_ui(self):
        """Initialize UI components."""
        self.setWindowTitle("Configure Macro Trigger")
        self.setMinimumSize(450, 350)

        layout = QVBoxLayout()

        # Title
        title = QLabel(f"Configure trigger for: <b>{self.macro_name}</b>")
        title.setStyleSheet("font-size: 14px;")
        layout.addWidget(title)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # Embed the TriggerEditor
        self.trigger_editor = TriggerEditor()
        layout.addWidget(self.trigger_editor)

        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Macro")
        save_btn.clicked.connect(self.save_trigger)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def save_trigger(self):
        """Validate and save trigger configuration by getting data from the editor."""
        self.trigger_info = self.trigger_editor.get_trigger_data()
        
        # Basic validation
        if not self.trigger_info.get("value"):
            QMessageBox.warning(self, "Input Error", "Please provide a value for the trigger.")
            return

        self.accept()

    def get_trigger_info(self) -> dict:
        """Return the configured trigger info from the editor."""
        return self.trigger_info
