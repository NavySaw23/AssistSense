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
from macros.player import MacroPlayerService
from macros.trigger import MacroTriggerService
from pynput import keyboard as _pynput_keyboard
from PyQt6.QtCore import QObject, pyqtSignal, QThread

# Battery monitoring
try:
    import psutil
    BATTERY_AVAILABLE = True
except ImportError:
    print("Warning: psutil not available. Battery triggers will not work.")
    BATTERY_AVAILABLE = False


class ControllerSignals(QObject):
    """Signals for controller events (threading safe)."""
    open_macro_manager = pyqtSignal(str)
    show_trigger_dialog = pyqtSignal(str)


class VoiceCommandWorker(QThread):
    """
    Runs the voice listener polling in a background thread to avoid freezing the UI.
    Moved from main.py to be managed by the Controller.
    """
    command_received = pyqtSignal(str)

    def __init__(self, listener: VoiceListener):
        super().__init__()
        self.listener = listener
        self._is_running = True

    def run(self):
        while self._is_running:
            if self.listener.is_listening():
                command = self.listener.pop_listened_text()
                if command:
                    self.command_received.emit(command)
            time.sleep(0.1)

    def stop(self):
        self._is_running = False
        self.listener.stop()


class Controller:
    def __init__(self, wakeword="hello", silencetimeout=4):
        # Core services
        self.listener = VoiceListener(wakeword, silencetimeout, config.VOICE_RECOGNITION_MODE)
        self.recorder = MacroRecorderService(macro_dir='Macros_json')
        self.player = MacroPlayerService(macro_dir="Macros_json")
        self.trigger_service = MacroTriggerService(self.player, macro_dir='Macros_json')

        # State flags
        self._is_recording = False
        self._current_macro_name = None

        # GUI references
        self.main_window = None
        self.macro_manager_window = None

        # Signals for thread-safe GUI operations
        self.signals = ControllerSignals()
        self.signals.open_macro_manager.connect(self._create_macro_manager_window)
        self.signals.show_trigger_dialog.connect(self._create_trigger_dialog)

        # Background services & threads
        self.voice_worker = VoiceCommandWorker(listener=self.listener)
        self.voice_worker.command_received.connect(self.process_voice_command)
        self._hotkey_thread = None
        self._battery_monitor_thread = None
        self._battery_monitoring = False
        self._last_battery_level = None

        # start global hotkeys
        self._initialize_hotkeys()

    def _initialize_hotkeys(self):
        """Register all global hotkeys."""
        try:
            self.hotkeys = _pynput_keyboard.GlobalHotKeys({
                '<ctrl>+<shift>+0': self.toggle_recording,
                '<ctrl>+\'': self.open_macro_manager,
                '<esc>': self.stop_all_macros
            })
            self._hotkey_thread = threading.Thread(target=self.hotkeys.start, daemon=True)
            print("Global hotkey for recording (Ctrl+Shift+0) registered.")
            print("Global hotkey for macro manager (Ctrl+') registered.")
            print("Global hotkey for stopping playback/recording (Esc) registered.")
        except Exception as e:
            print(f"Failed to register global hotkey: {e}")

    def run(self, main_window):
        """Starts all background services."""
        self.main_window = main_window
        if self._hotkey_thread:
            self._hotkey_thread.start()
        self.voice_worker.start()
        if BATTERY_AVAILABLE:
            self._start_battery_monitoring()
        print("✓ Controller started all services.")

    def process_voice_command(self, text: str):
        """Handles all incoming voice commands and routes them appropriately."""
        from app.trigger_dialog import TriggerConfigDialog
        cmd = text.lower().strip()

        # State-aware command handling: if recording, only listen for "stop"
        if self._is_recording:
            if any(kw in cmd for kw in ["stop recording", "stop"]):
                macro_name = self.toggle_recording()
                if macro_name:
                    # Use the thread-safe method to show the dialog
                    self.signals.show_trigger_dialog.emit(macro_name)
                self.listener.force_active_mode = False
            return # Ignore all other commands during recording

        # If not recording, check for start command
        if any(kw in cmd for kw in ["record", "start recording", "start"]):
            self.listener.force_active_mode = True
            self.toggle_recording()
            return

        # Otherwise, dispatch to the macro trigger service
        self.listener.force_active_mode = True
        self.trigger_service.on_voice_command(text)
        self.listener.force_active_mode = False

    def _start_battery_monitoring(self):
        """Start a background thread to monitor battery level and check triggers."""
        if self._battery_monitor_thread and self._battery_monitor_thread.is_alive():
            return

        self._battery_monitoring = True
        self._battery_monitor_thread = threading.Thread(target=self._battery_monitor_loop, daemon=True)
        self._battery_monitor_thread.start()
        print("Battery monitoring started")

    def _battery_monitor_loop(self):
        """Continuously monitor battery level and check triggers."""
        while self._battery_monitoring:
            try:
                if BATTERY_AVAILABLE and self.trigger_service:
                    battery = psutil.sensors_battery()
                    if battery is not None:
                        current_level = int(battery.percent)
                        if current_level != self._last_battery_level:
                            print(f"Battery level: {current_level}%")
                            self.trigger_service.check_battery_trigger(current_level)
                            self._last_battery_level = current_level
                time.sleep(30)
            except Exception as e:
                print(f"Error in battery monitor loop: {e}")
                time.sleep(30) # Prevent rapid failure loops

    def stop_battery_monitoring(self):
        self._battery_monitoring = False
        if self._battery_monitor_thread:
            self._battery_monitor_thread.join(timeout=2)

    def is_listening(self):
        """Returns the listening status from the voice listener."""
        return self.listener.is_listening()

    def get_listened_text(self):
        """Returns the latest display text from the voice listener."""
        return self.listener.get_listened_text()

    def stop_all_macros(self):
        """A global hotkey callback to stop all macro playback or recording."""
        if self.player and self.player.is_playing:
            print("Escape key pressed. Stopping macro playback.")
            self.player.stop_playback()

        if self._is_recording:
            print("Escape key pressed. Stopping recording.")
            macro_name = self.toggle_recording()
            if macro_name:
                # Emit a signal to safely create the dialog in the main thread
                self.signals.show_trigger_dialog.emit(macro_name)

    def stop(self):
        self.voice_worker.stop()
        self.stop_battery_monitoring()
        if hasattr(self, 'hotkeys') and self.hotkeys:
            self.hotkeys.stop()

    def set_voice_recognition_mode(self, mode):
        if mode in ["online", "offline"]:
            config.VOICE_RECOGNITION_MODE = mode
            print(f"Voice recognition mode set to: {mode}")
        else:
            print(f"Invalid mode: {mode}. Please use 'online' or 'offline'.")

    def finalize_macro(self, trigger_info: dict) -> bool:
        try:
            self.recorder.update_trigger(trigger_info)
            self.recorder.save_macro()
            return True
        except Exception as e:
            print(f"Error finalizing macro: {e}")
            return False

    def toggle_recording(self):
        if not self._is_recording:
            name = f"macro_{time.strftime('%Y%m%d_%H%M%S')}"
            trigger_info = {'type': 'hotkey', 'value': 'ctrl+shift+0'}
            self.recorder.start_recording(name, trigger_info)
            self._is_recording = True
            self._current_macro_name = name
            print(f"Recording started: {name}")
            return None
        else:
            self.recorder.stop_recording()
            self._is_recording = False
            print("Recording stopped")
            return self._current_macro_name

    def open_macro_manager(self, file_path=None):
        self.signals.open_macro_manager.emit(str(file_path or ''))

    def _create_macro_manager_window(self, file_path=None):
        if self.macro_manager_window and self.macro_manager_window.isVisible():
            self.macro_manager_window.raise_()
            self.macro_manager_window.activateWindow()
            return

        try:
            from app.macro_manager_gui import MacroManagerWindow
            # Pass file_path, which can be None
            self.macro_manager_window = MacroManagerWindow(file_path=file_path)
            self.macro_manager_window.show()
            print("Macro manager window opened")
        except Exception as e:
            print(f"Error opening macro manager: {e}")

    def _create_trigger_dialog(self, macro_name: str):
        """Creates and shows the trigger dialog in the main GUI thread."""
        from app.trigger_dialog import TriggerConfigDialog
        dialog = TriggerConfigDialog(macro_name, parent=self.main_window)
        if dialog.exec():
            trigger_info = dialog.get_trigger_info()
            if self.finalize_macro(trigger_info):
                print(f"Macro '{macro_name}' saved with trigger: {trigger_info}")
                self.trigger_service._load_triggers()
        self.listener.force_active_mode = False


# Create a global instance of the Controller
controller = Controller()
