import os
import json
from pathlib import Path
from PyQt6.QtWidgets import QLabel, QWidget, QScrollArea, QVBoxLayout, QGraphicsColorizeEffect
from PyQt6.QtCore import QSize, Qt, QRect
from app.utils.helpers import load_svg, load_svg_from_string
from PyQt6.QtWidgets import QLabel, QWidget, QScrollArea, QVBoxLayout, QGraphicsColorizeEffect


class AddMacroPane(QLabel):
    def __init__(self, parent, scalefactor):
        super().__init__(parent)
        self.scalefactor = scalefactor
        
        width = 328 * self.scalefactor
        height = 48 * self.scalefactor
        self.setFixedSize(int(width), int(height))
        
        svg_path = str(Path(__file__).parent.parent.parent / "assets" / "svg" / "MacroitemAdd.svg")
        with open(svg_path, 'r') as f:
            self.svg_normal = f.read()
        
        self.svg_hover = self.svg_normal.replace("#D9D9D9", "#A1A1A1")
        
        load_svg_from_string(self.svg_normal, self, self.size())

        self.setMouseTracking(True)

    def enterEvent(self, event):
        load_svg_from_string(self.svg_hover, self, self.size())

    def leaveEvent(self, event):
        load_svg_from_string(self.svg_normal, self, self.size())

    def mousePressEvent(self, event):
        print("Add new macro button clicked. Implement new window opening here.")
        super().mousePressEvent(event)


class Macropane(QLabel):
    def __init__(self, parent, scalefactor, name, status, file_path):
        super().__init__(parent)
        self.scalefactor = scalefactor
        self.name = name
        self.status = status
        self.file_path = file_path
        
        width = 328 * self.scalefactor
        height = 48 * self.scalefactor
        self.setFixedSize(int(width), int(height))
        
        self.update_background()

        self.name_label = QLabel(self.name, self)
        self.name_label.setGeometry(int(50 * self.scalefactor), int(8 * self.scalefactor), int(258 * self.scalefactor), int(32 * self.scalefactor))
        font_size = int(16 * self.scalefactor)
        self.name_label.setStyleSheet(f"font-family: montserrat; font-size: {font_size}px; color: black; background: transparent;")
        self.setMouseTracking(True)

    def update_background(self):
        svg_name = "MacroitemSelected.svg" if self.status == "on" else "Macroitem.svg"
        svg_path = str(Path(__file__).parent.parent.parent / "assets" / "svg" / svg_name)
        with open(svg_path, 'r') as f:
            self.svg_normal = f.read()
        
        self.svg_hover = self.svg_normal.replace("#D9D9D9", "#A1A1A1")
        
        load_svg_from_string(self.svg_normal, self, self.size())

    def enterEvent(self, event):
        load_svg_from_string(self.svg_hover, self, self.size())

    def leaveEvent(self, event):
        load_svg_from_string(self.svg_normal, self, self.size())

    def mousePressEvent(self, event):
        click_rect = QRect(int(7 * self.scalefactor), int(7 * self.scalefactor), int(33 * self.scalefactor), int(33 * self.scalefactor))
        if click_rect.contains(event.pos()):
            self.status = "off" if self.status == "on" else "on"
            
            try:
                with open(self.file_path, 'r+') as f:
                    data = json.load(f)
                    data['status'] = self.status
                    f.seek(0)
                    json.dump(data, f, indent=2)
                    f.truncate()
            except Exception as e:
                print(f"Error updating file {self.file_path}: {e}")

            self.update_background()
        super().mousePressEvent(event)


class MacroPaneContent(QWidget):
    def __init__(self, parent, scalefactor):
        super().__init__(parent)
        self.scalefactor = scalefactor
        self.setGeometry(0,0, int(parent.width()), int(parent.height()))

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry(int(9 * self.scalefactor), int(135 * self.scalefactor), int(354 * self.scalefactor), int(385 * self.scalefactor))
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(int(10 * self.scalefactor), 0, 0, 0)
        self.scroll_layout.setSpacing(int(8 * self.scalefactor))
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.scroll_content.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.scroll_area.setWidget(self.scroll_content)

        # Make the scroll area transparent
        self.scroll_area.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 5px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #454545;
                min-height: 20px;
                border-radius: 2px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        self.scroll_content.setStyleSheet("background: transparent;")

        self.update_macro_panes()

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def update_macro_panes(self, selected_app="global"):
        self.clear_layout(self.scroll_layout)
        
        # Add the "Add New Macro" button first
        add_macro_pane = AddMacroPane(self.scroll_content, self.scalefactor)
        self.scroll_layout.addWidget(add_macro_pane)

        macros_dir = Path(__file__).parent.parent.parent / "Macros_json"
        if macros_dir.exists() and macros_dir.is_dir():
            for file_name in sorted(os.listdir(macros_dir)):
                if file_name.endswith(".json"):
                    file_path = macros_dir / file_name
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                        
                        macro_app = data.get("app", "global")
                        if macro_app == selected_app:
                            macro_name = data.get("name", "Unnamed Macro")
                            macro_status = data.get("status", "off")
                            self.scroll_layout.addWidget(Macropane(self.scroll_content, self.scalefactor, macro_name, macro_status, file_path))

                    except json.JSONDecodeError:
                        print(f"Error decoding JSON from file: {file_name}")
                    except Exception as e:
                        print(f"An error occurred: {e}")
