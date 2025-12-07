import sys
import time
import argparse
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication

from app.gui import MainMenuWindow
from app.controller import controller
from app.trigger_dialog import TriggerConfigDialog
from macros.player import MacroPlayerService
from macros.trigger import MacroTriggerService
from voiceRecog.voiceRecog import VoiceListener


class VoiceCommandWorker(QThread):
    """
    Runs the voice listener polling in a background thread to avoid freezing the UI.
    """
    command_received = pyqtSignal(str)

    def __init__(self, listener: VoiceListener):
        super().__init__()
        self.listener = listener
        self._is_running = True

    def run(self):
        while self._is_running:
            if self.listener.is_listening():
                # Use pop_listened_text() to consume and clear the text after reading it
                command = self.listener.pop_listened_text()
                if command:
                    self.command_received.emit(command)
                    # Wait a moment to prevent re-triggering on the same text
                    time.sleep(2)
            time.sleep(0.1)

    def stop(self):
        self._is_running = False
        self.listener.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["online", "offline"], help="Set the voice recognition mode")
    args = parser.parse_args()

    if args.mode:
        controller.set_voice_recognition_mode(args.mode)

    # Launcher settings merged from user snippet
    APP_SCALEFACTOR = 0.8
    # Set to True to enable debug UI features; change as needed
    DEBUG_MODE = False

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # 1. Initialize services
    voice_listener = controller.listener
    player_service = MacroPlayerService(macro_dir="Macros_json")
    trigger_service = MacroTriggerService(player=player_service, macro_dir="Macros_json")
    
    # Initialize controller's trigger service for battery monitoring and other triggers
    controller.initialize_triggers(player_service)

    # Create the main window first so dialogs have a parent
    window = MainMenuWindow(scalefactor=APP_SCALEFACTOR, DebugMode=DEBUG_MODE)
    window.show()

    # Connect macro manager signal to create window in main thread
    controller.signals.open_macro_manager.connect(controller._create_macro_manager_window)

    # 2. Set up and start the background voice worker
    voice_worker = VoiceCommandWorker(listener=voice_listener)

    # Handle voice commands: special-case 'record' to toggle recording, otherwise forward to trigger_service
    def handle_voice_command(text: str):
        cmd = text.lower().strip()

        # Check for recording commands
        if any(kw in cmd for kw in ["record", "start recording", "start"]):
            # Enable force active mode so no need to say wake word again during recording
            voice_listener.force_active_mode = True
            macro_name = controller.toggle_recording(parent_widget=window)
            # If recording just stopped, show trigger config dialog
            if macro_name:
                dialog = TriggerConfigDialog(macro_name, parent=window)
                if dialog.exec():
                    trigger_info = dialog.get_trigger_info()
                    if controller.finalize_macro(trigger_info):
                        print(f"Macro '{macro_name}' saved with trigger: {trigger_info}")
                        # Reload triggers so newly saved macro is available immediately
                        trigger_service._load_triggers()
                # Disable force active mode after recording ends
                voice_listener.force_active_mode = False
            return
        if any(kw in cmd for kw in ["stop recording", "stop"]):
            # ensure recording stops and trigger dialog shows
            if hasattr(controller, 'recorder') and controller._is_recording:
                macro_name = controller.toggle_recording(parent_widget=window)
                if macro_name:
                    dialog = TriggerConfigDialog(macro_name, parent=window)
                    if dialog.exec():
                        trigger_info = dialog.get_trigger_info()
                        if controller.finalize_macro(trigger_info):
                            print(f"Macro '{macro_name}' saved with trigger: {trigger_info}")
                            # Reload triggers so newly saved macro is available immediately
                            trigger_service._load_triggers()
                # Disable force active mode after recording ends
                voice_listener.force_active_mode = False
                return

        # otherwise, dispatch to macro trigger service (and enable force active during playback)
        voice_listener.force_active_mode = True
        trigger_service.on_voice_command(text)
        # Note: playback is typically very fast, but we keep it active to allow quick stop commands
        voice_listener.force_active_mode = False

    voice_worker.command_received.connect(handle_voice_command)
    voice_worker.start()

    # 3. Ensure background threads are stopped when the app closes
    exit_code = app.exec()
    voice_worker.stop()
    controller.stop()
    sys.exit(exit_code)