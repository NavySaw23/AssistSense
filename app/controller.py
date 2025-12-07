import sys
import os
import threading
import time

# Add the project root to the Python path to allow direct execution of this file
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from voiceRecog import VoiceListener
import config

# recorder/player imports
from macros.recorder import MacroRecorderService
from pynput import keyboard as _pynput_keyboard


class Controller:
    def __init__(self, wakeword="hello", silencetimeout=4):
        # voice listener
        self.listener = VoiceListener(wakeword, silencetimeout, config.VOICE_RECOGNITION_MODE)

        # macro recorder (stores JSON into Macros_json by default)
        self.recorder = MacroRecorderService(macro_dir='Macros_json')
        self._is_recording = False
        self._current_macro_name = None

        # start global hotkey for toggling recording: Ctrl+Shift+0
        try:
            self.hotkeys = _pynput_keyboard.GlobalHotKeys({
                '<ctrl>+<shift>+0': self.toggle_recording
            })
            # run hotkey listener in a background thread
            self._hotkey_thread = threading.Thread(target=self.hotkeys.start, daemon=True)
            self._hotkey_thread.start()
            print("Global hotkey for recording (Ctrl+Shift+0) registered.")
        except Exception as e:
            print(f"Failed to register global hotkey: {e}")

    def is_listening(self):
        return self.listener.is_listening()

    def get_listened_text(self):
        return self.listener.get_listened_text()

    def stop(self):
        self.listener.stop()
        try:
            if hasattr(self, 'hotkeys') and self.hotkeys:
                self.hotkeys.stop()
        except Exception:
            pass

    def set_voice_recognition_mode(self, mode):
        """Sets the voice recognition mode (online/offline)"""
        if mode in ["online", "offline"]:
            config.VOICE_RECOGNITION_MODE = mode
            # You might need to restart the listener for the change to take effect.
            print(f"Voice recognition mode set to: {mode}")
        else:
            print(f"Invalid mode: {mode}. Please use 'online' or 'offline'.")

    def finalize_macro(self, trigger_info: dict) -> bool:
        """After recording stops, update trigger info and save the macro.
        Returns True if successful, False otherwise.
        """
        try:
            self.recorder.update_trigger(trigger_info)
            self.recorder.save_macro()
            return True
        except Exception as e:
            print(f"Error finalizing macro: {e}")
            return False

    def toggle_recording(self, parent_widget=None):
        """Toggle recording on/off. If starting, auto-generate a name and use a hotkey trigger.
        If stopping, emit a signal or show a dialog to configure the trigger.
        parent_widget: the QWidget parent for the trigger dialog (optional).
        """
        if not self._is_recording:
            # start recording
            name = f"macro_{time.strftime('%Y%m%d_%H%M%S')}"
            trigger_info = {'type': 'hotkey', 'value': 'ctrl+shift+0'}
            self.recorder.start_recording(name, trigger_info)
            self._is_recording = True
            self._current_macro_name = name
            print(f"Recording started: {name}")
        else:
            # stop recording
            self.recorder.stop_recording()
            self._is_recording = False
            print("Recording stopped")
            # Return the macro name so caller can show trigger dialog
            return self._current_macro_name
        return None


# Create a single Controller instance
controller = Controller()

if __name__ == '__main__':
    # This block will be executed only when the script is run directly
    # It can be used for testing the Controller class independently
    print("Controller script running directly for testing.")
    try:
        while True:
            print(f"Listening flag: {controller.is_listening()} | Heard: {controller.get_listened_text()}")
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        controller.stop()
        print("Controller script stopped.")