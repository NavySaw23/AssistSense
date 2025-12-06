from PyQt6.QtWidgets import QWidget, QComboBox, QPushButton
import pygetwindow as gw

class InfoBoxContentWidget(QWidget):
    def __init__(self, parent, scalefactor):
        super().__init__(parent)
        self.process_dropdown = QComboBox(self)
        self.process_dropdown.setGeometry(int(20 * scalefactor), int(20 * scalefactor), int(350 * scalefactor), int(30 * scalefactor))

        self.refresh_button = QPushButton("↻", self)
        self.refresh_button.setGeometry(int(380 * scalefactor), int(20 * scalefactor), int(60 * scalefactor), int(30 * scalefactor))
        self.refresh_button.clicked.connect(self.populate_processes)

        self.populate_processes()

    def populate_processes(self):
        self.process_dropdown.clear()
        window_titles = []
        for w in gw.getAllWindows():
            if w.title:
                window_titles.append(w.title)
        
        self.process_dropdown.addItems(sorted(list(set(window_titles))))
