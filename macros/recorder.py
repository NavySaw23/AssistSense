import json
import time
import os
from pynput import mouse, keyboard
from screeninfo import get_monitors

from .interfaces import IMacroRecorder
from .datamodel import Action, ScreenInfo, TriggerInfo, Macro


class MacroRecorderService(IMacroRecorder):
    def __init__(self, macro_dir="Macros_json"):
        self.macro_dir = macro_dir
        self.is_recording = False
        self.actions = []
        self.last_event_time = 0
        self.screen_info = None
        self.macro_name = ""
        self.trigger_info = None
        self.mouse_listener = None
        self.keyboard_listener = None
        os.makedirs(self.macro_dir, exist_ok=True)

    def start_recording(self, name: str, trigger_info: dict) -> None:
        print(f"Starting recording for macro: {name}")
        self.actions.clear()
        self.macro_name = name
        self.trigger_info = TriggerInfo(**trigger_info)
        
        primary_monitor = [m for m in get_monitors() if m.is_primary][0]
        self.screen_info = ScreenInfo(width=primary_monitor.width, height=primary_monitor.height)
        
        self.last_event_time = time.time()
        self.is_recording = True

        self.mouse_listener = mouse.Listener(on_move=self._on_move, on_click=self._on_click, on_scroll=self._on_scroll)
        self.keyboard_listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self.mouse_listener.start()
        self.keyboard_listener.start()

    def _add_action(self, action_type: str, details: dict):
        if not self.is_recording:
            return
        
        current_time = time.time()
        dt_ms = int((current_time - self.last_event_time) * 1000)
        self.last_event_time = current_time
        
        self.actions.append(Action(dt=dt_ms, type=action_type, details=details))
        print(f"Recorded action: {action_type} with dt={dt_ms}")

    def _on_move(self, x, y):
        details = {
            "xNorm": x / self.screen_info.width,
            "yNorm": y / self.screen_info.height
        }
        self._add_action("mouse_move", details)

    def _on_click(self, x, y, button, pressed):
        details = {
            "xNorm": x / self.screen_info.width,
            "yNorm": y / self.screen_info.height,
            "button": button.name,
            "pressed": pressed
        }
        self._add_action("mouse_click", details)

    def _on_scroll(self, x, y, dx, dy):
        pass # Implement if needed

    def _on_press(self, key):
        # For simplicity, we'll use key name. For text, you might buffer chars.
        details = {"key": str(key), "pressed": True}
        self._add_action("keyboard_key", details)

    def _on_release(self, key):
        details = {"key": str(key), "pressed": False}
        self._add_action("keyboard_key", details)

    def stop_recording(self) -> None:
        if not self.is_recording:
            return
        print("Stopping recording...")
        self.is_recording = False
        if self.mouse_listener: self.mouse_listener.stop()
        if self.keyboard_listener: self.keyboard_listener.stop()
        # Don't save yet—wait for trigger configuration
        print(f"Recording stopped. Waiting for trigger configuration before saving.")

    def update_trigger(self, trigger_info: dict) -> None:
        """Update the macro's trigger info before saving. Useful for post-recording configuration."""
        self.trigger_info = TriggerInfo(**trigger_info)

    def save_macro(self) -> None:
        """Save the current recorded macro with its configured trigger."""
        # Serialize and save
        macro = Macro(name=self.macro_name, screen=self.screen_info, trigger=self.trigger_info, actions=self.actions)
        file_path = os.path.join(self.macro_dir, f"{self.macro_name}.json")
        with open(file_path, 'w') as f:
            # A proper dataclass-to-JSON library would be better for production
            json.dump(macro, f, default=lambda o: o.__dict__, indent=2)
        print(f"Macro saved to {file_path}")
