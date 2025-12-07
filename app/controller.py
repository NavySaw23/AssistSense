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
from PyQt6.QtCore import QObject, pyqtSignal

# Battery monitoring
try:
    import psutil
    BATTERY_AVAILABLE = True
except ImportError:
    print("Warning: psutil not available. Battery triggers will not work.")
    BATTERY_AVAILABLE = False


class ControllerSignals(QObject):
    """Signals for controller events (threading safe)."""
    open_macro_manager = pyqtSignal()


class Controller:
    def __init__(self, wakeword="hello", silencetimeout=4):
        # voice listener
        self.listener = VoiceListener(wakeword, silencetimeout, config.VOICE_RECOGNITION_MODE)

        # macro recorder (stores JSON into Macros_json by default)
        self.recorder = MacroRecorderService(macro_dir='Macros_json')
        self._is_recording = False
        self._current_macro_name = None
        
        # macro manager window reference
        self.macro_manager_window = None
        
        # Signals for thread-safe GUI operations
        self.signals = ControllerSignals()
        
        # macro trigger service for executing macros
        self.trigger_service = None
        self._battery_monitor_thread = None
        self._battery_monitoring = False
        self._last_battery_level = None

        # start global hotkey for toggling recording: Ctrl+Shift+0 and opening macro manager: Ctrl+'
        try:
            self.hotkeys = _pynput_keyboard.GlobalHotKeys({
                '<ctrl>+<shift>+0': self.toggle_recording,
                '<ctrl>+\'': self.open_macro_manager
            })
            # run hotkey listener in a background thread
            self._hotkey_thread = threading.Thread(target=self.hotkeys.start, daemon=True)
            self._hotkey_thread.start()
            print("Global hotkey for recording (Ctrl+Shift+0) registered.")
            print("Global hotkey for macro manager (Ctrl+') registered.")
        except Exception as e:
            print(f"Failed to register global hotkey: {e}")
    
    def initialize_triggers(self, player_service):
        """Initialize macro trigger service after player service is created."""
        try:
            from macros.trigger import MacroTriggerService
            self.trigger_service = MacroTriggerService(player_service, macro_dir='Macros_json')
            print("✓ MacroTriggerService initialized")
            # Start battery monitoring if available
            if BATTERY_AVAILABLE:
                self._start_battery_monitoring()
        except Exception as e:
            print(f"Error initializing trigger service: {e}")
    
    def _start_battery_monitoring(self):
        """Start a background thread to monitor battery level and check triggers."""
        if self._battery_monitor_thread is not None and self._battery_monitor_thread.is_alive():
            return  # Already running
        
        self._battery_monitoring = True
        self._battery_monitor_thread = threading.Thread(target=self._battery_monitor_loop, daemon=True)
        self._battery_monitor_thread.start()
        print("Battery monitoring started")
    
    def _battery_monitor_loop(self):
        """Continuously monitor battery level and check triggers (runs in background thread)."""
        while self._battery_monitoring:
            try:
                if BATTERY_AVAILABLE and self.trigger_service:
                    battery = psutil.sensors_battery()
                    if battery is not None:
                        current_level = int(battery.percent)
                        
                        # Only check triggers if battery level changed
                        if current_level != self._last_battery_level:
                            self._last_battery_level = current_level
                            print(f"Battery level: {current_level}%")
                            # Check if any battery triggers match
                            self.trigger_service.check_battery_trigger(current_level)
                
                # Check battery every 30 seconds
                time.sleep(30)
            
            except Exception as e:
                print(f"Error in battery monitor loop: {e}")
                time.sleep(30)
    
    def stop_battery_monitoring(self):
        """Stop the battery monitoring thread."""
        self._battery_monitoring = False
        if self._battery_monitor_thread is not None:
            self._battery_monitor_thread.join(timeout=2)

    def is_listening(self):
        return self.listener.is_listening()

    def get_listened_text(self):
        return self.listener.get_listened_text()

    def stop(self):
        self.listener.stop()
        self.stop_battery_monitoring()
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
    
    def open_macro_manager(self):
        """Emit signal to open the macro manager GUI window (thread-safe)."""
        # Emit the signal which will be handled in the main thread
        self.signals.open_macro_manager.emit()
    
    def _create_macro_manager_window(self):
        """Create macro manager window in the main thread."""
        # If window already exists, bring it to front
        if self.macro_manager_window is not None:
            self.macro_manager_window.raise_()
            self.macro_manager_window.activateWindow()
            return
        
        # Create new window
        try:
            from app.macro_manager_gui import MacroManagerWindow
            self.macro_manager_window = MacroManagerWindow()
            self.macro_manager_window.show()
            print("Macro manager window opened")
        except Exception as e:
            print(f"Error opening macro manager: {e}")


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