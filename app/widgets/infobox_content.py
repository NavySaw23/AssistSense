from PyQt6.QtWidgets import QWidget, QComboBox, QPushButton, QLabel
import pygetwindow as gw
import sounddevice as sd
import cv2

class InfoBoxContentWidget(QWidget):
    def __init__(self, parent, scalefactor):
        super().__init__(parent)
        self.process_dropdown = QComboBox(self)
        self.process_dropdown.setGeometry(int(20 * scalefactor), int(20 * scalefactor), int(350 * scalefactor), int(30 * scalefactor))
        self.process_dropdown.setStyleSheet("font-family: montserrat; font-size: 14px; color: #FFFFFF; background: #282a36;")

        self.refresh_button = QPushButton("↻", self)
        self.refresh_button.setGeometry(int(380 * scalefactor), int(20 * scalefactor), int(60 * scalefactor), int(30 * scalefactor))
        self.refresh_button.setStyleSheet("font-family: montserrat; font-size: 14px; color: #FFFFFF; background: #282a36;")
        self.refresh_button.clicked.connect(self.populate_processes)

        self.mic_label = QLabel("Mic", self)
        self.mic_label.setGeometry(int(20 * scalefactor), int(60 * scalefactor), int(80 * scalefactor), int(30 * scalefactor))
        self.mic_label.setStyleSheet("font-family: montserrat; font-size: 14px; color: #000000;")

        self.mic_dropdown = QComboBox(self)
        self.mic_dropdown.setGeometry(int(110 * scalefactor), int(60 * scalefactor), int(170 * scalefactor), int(30 * scalefactor))
        self.mic_dropdown.setStyleSheet("font-family: montserrat; font-size: 14px; color: #FFFFFF; background: #282a36;")
        self.populate_mics()

        self.mic_on_off_button = QPushButton("Off", self)
        self.mic_on_off_button.setCheckable(True)
        self.mic_on_off_button.setGeometry(int(290 * scalefactor), int(60 * scalefactor), int(80 * scalefactor), int(30 * scalefactor))
        self.mic_on_off_button.setStyleSheet("font-family: montserrat; font-size: 14px; color: #FFFFFF; background: #282a36;")
        self.mic_on_off_button.clicked.connect(self.toggle_mic)

        self.camera_label = QLabel("Camera", self)
        self.camera_label.setGeometry(int(20 * scalefactor), int(100 * scalefactor), int(80 * scalefactor), int(30 * scalefactor))
        self.camera_label.setStyleSheet("font-family: montserrat; font-size: 14px; color: #000000;")

        self.camera_dropdown = QComboBox(self)
        self.camera_dropdown.setGeometry(int(110 * scalefactor), int(100 * scalefactor), int(170 * scalefactor), int(30 * scalefactor))
        self.camera_dropdown.setStyleSheet("font-family: montserrat; font-size: 14px; color: #FFFFFF; background: #282a36;")
        self.populate_cameras()
        
        self.camera_on_off_button = QPushButton("Off", self)
        self.camera_on_off_button.setCheckable(True)
        self.camera_on_off_button.setGeometry(int(290 * scalefactor), int(100 * scalefactor), int(80 * scalefactor), int(30 * scalefactor))
        self.camera_on_off_button.setStyleSheet("font-family: montserrat; font-size: 14px; color: #FFFFFF; background: #282a36;")
        self.camera_on_off_button.clicked.connect(self.toggle_camera)

        self.populate_processes()

    def populate_processes(self):
        self.process_dropdown.clear()
        window_titles = []
        for w in gw.getAllWindows():
            if w.title:
                window_titles.append(w.title)
        
        self.process_dropdown.addItems(sorted(list(set(window_titles))))

    def populate_mics(self):
        self.mic_dropdown.clear()
        mics = sd.query_devices()
        mic_names = [mic['name'] for mic in mics if mic['max_input_channels'] > 0 and mic['hostapi'] != 0]
        self.mic_dropdown.addItems(mic_names)

    def populate_cameras(self):
        self.camera_dropdown.clear()
        cameras = []
        for i in range(5): # Check for 5 cameras max
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                cameras.append(f"Camera {i}")
                cap.release()
        self.camera_dropdown.addItems(cameras)

    def toggle_mic(self, checked):
        if checked:
            self.mic_on_off_button.setText("On")
        else:
            self.mic_on_off_button.setText("Off")

    def toggle_camera(self, checked):
        if checked:
            self.camera_on_off_button.setText("On")
        else:
            self.camera_on_off_button.setText("Off")