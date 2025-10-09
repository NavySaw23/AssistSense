import sys
from PyQt6.QtWidgets import QApplication
from app.gui import MainMenuWindow # Import from your other file

if __name__ == '__main__':

    APP_SCALEFACTOR = 0.5
    DEBUG_MODE = True
    # DEBUG_MODE = False
    
    app = QApplication(sys.argv)
    window = MainMenuWindow(scalefactor=APP_SCALEFACTOR, DebugMode=DEBUG_MODE)
    window.show()
    
    sys.exit(app.exec()) 