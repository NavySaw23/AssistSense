import sys
import argparse
from PyQt6.QtWidgets import QApplication

from app.gui import MainMenuWindow
from app.controller import controller


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["online", "offline"], help="Set the voice recognition mode")
    args = parser.parse_args()

    if args.mode:
        controller.set_voice_recognition_mode(args.mode)

    # Launcher settings
    APP_SCALEFACTOR = 0.8
    DEBUG_MODE = False

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Create the main window and the controller
    window = MainMenuWindow(scalefactor=APP_SCALEFACTOR, DebugMode=DEBUG_MODE)
    window.show()

    # Start all background services and run the application
    controller.run(main_window=window)

    # Execute the application's main loop
    exit_code = app.exec()

    # Stop all background threads before exiting
    controller.stop()
    sys.exit(exit_code)