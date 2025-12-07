import json
import time
import os
from pynput import mouse, keyboard
from screeninfo import get_monitors
import threading

from .interfaces import IMacroPlayer

class MacroPlayerService(IMacroPlayer):
    def __init__(self, macro_dir="Macros_json"):
        self.macro_dir = macro_dir
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.is_playing = False
        self.stop_event = threading.Event()

    def play(self, macro_name: str) -> None:
        file_path = os.path.join(self.macro_dir, f"{macro_name}.json")
        if not os.path.exists(file_path):
            print(f"Error: Macro '{macro_name}' not found.")
            return

        with open(file_path, 'r') as f:
            macro_data = json.load(f)

        self.is_playing = True
        self.stop_event.clear()
        print(f"Playing macro: {macro_name}")

        primary_monitor = [m for m in get_monitors() if m.is_primary][0]
        current_width, current_height = primary_monitor.width, primary_monitor.height

        for action in macro_data['actions']:
            if self.stop_event.is_set():
                print("Playback cancelled.")
                break

            time.sleep(action['dt'] / 1000.0)

            action_type = action['type']
            details = action['details']

            if action_type == "mouse_move":
                # Use integer coordinates for the controller
                x = int(details['xNorm'] * current_width)
                y = int(details['yNorm'] * current_height)
                self.mouse_controller.position = (x, y)
            
            elif action_type == "mouse_click":
                # Move to position first (use integer coords)
                x = int(details['xNorm'] * current_width)
                y = int(details['yNorm'] * current_height)
                self.mouse_controller.position = (x, y)

                # Resolve button name safely (accept strings like 'left'/'right')
                btn_name = details.get('button', 'left')
                btn_key = btn_name.lower()
                button = getattr(mouse.Button, btn_key, None)
                if button is None:
                    try:
                        button = mouse.Button[btn_name]
                    except Exception:
                        button = mouse.Button.left

                pressed = details.get('pressed', True)
                # Debug output to help visibility when testing
                print(f"MacroPlayer: mouse_click {btn_name} at ({x},{y}) pressed={pressed}")

                if pressed:
                    self.mouse_controller.press(button)
                    # small pause so OS registers the press (helps right-click context menus)
                    time.sleep(0.08)
                else:
                    self.mouse_controller.release(button)

            elif action_type == "keyboard_key":
                # Handle single key presses/releases. Expected formats:
                # - details['key'] might be "Key.enter" or "'a'" or "a".
                key_str = details.get('key')
                pressed = details.get('pressed', True)
                try:
                    # If it's a Key.* value
                    if isinstance(key_str, str) and key_str.startswith('Key.'):
                        key_name = key_str.split('.', 1)[1]
                        key_obj = getattr(keyboard.Key, key_name)
                    else:
                        # strip surrounding quotes if present
                        k = key_str
                        if isinstance(k, str) and len(k) >= 2 and ((k[0] == "'" and k[-1] == "'") or (k[0] == '"' and k[-1] == '"')):
                            k = k[1:-1]
                        key_obj = k

                    if pressed:
                        self.keyboard_controller.press(key_obj)
                        # short pause so presses are registered visibly
                        time.sleep(0.06)
                    else:
                        self.keyboard_controller.release(key_obj)
                except Exception:
                    # Fallback: try typing the string as text
                    txt = key_str if isinstance(key_str, str) else str(key_str)
                    self.keyboard_controller.type(txt)

            elif action_type == "keyboard_text":
                # Type a string of text
                text = details.get('text', '')
                if text:
                    self.keyboard_controller.type(text)

        self.is_playing = False
        print("Playback finished.")

    def stop_playback(self) -> None:
        if self.is_playing:
            self.stop_event.set()
