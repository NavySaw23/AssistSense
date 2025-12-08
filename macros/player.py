import json
import time
import os
from pynput import mouse, keyboard
from screeninfo import get_monitors
import threading

from .interfaces import IMacroPlayer
import platform
try:
    import winsound
except Exception:
    winsound = None

# Optional notification/sound helpers
try:
    from plyer import notification as plyer_notification
except Exception:
    plyer_notification = None

try:
    from win10toast import ToastNotifier
    _toast_notifier = ToastNotifier()
except Exception:
    _toast_notifier = None

try:
    from playsound import playsound as _playsound
except Exception:
    _playsound = None

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class MacroPlayerService(IMacroPlayer):
    def __init__(self, macro_dir="Macros_json"):
        self.macro_dir = macro_dir
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.is_playing = False
        self.stop_event = threading.Event()
    
    def _evaluate_condition(self, condition_dict):
        """Evaluate a single condition and return True/False."""
        try:
            # Handle simple string conditions like "true"
            if isinstance(condition_dict, str):
                return condition_dict.lower() == 'true'

            cond_type = condition_dict.get('type', '')

            # Handle the case where the condition is {"type": "true"}
            if cond_type == 'true':
                return True
            
            if cond_type == 'system':
                system_name = condition_dict.get('name', '')
                op = condition_dict.get('op') or condition_dict.get('operator', '==')
                target_value = condition_dict.get('value')
                
                if system_name == 'battery':
                    if PSUTIL_AVAILABLE:
                        battery = psutil.sensors_battery()
                        if battery:
                            current = int(battery.percent)
                            return self._compare_values(current, op, target_value)
                    return False
            
            return True
        
        except Exception as e:
            print(f"Error evaluating condition: {e}")
            return False
    
    def _compare_values(self, current, operator, target):
        """Compare current value against target using operator."""
        try:
            if operator == '<':
                return current < target
            elif operator == '<=':
                return current <= target
            elif operator == '>':
                return current > target
            elif operator == '>=':
                return current >= target
            elif operator == '==':
                return current == target
            elif operator == '!=':
                return current != target
            else:
                return False
        except Exception as e:
            print(f"Error comparing values: {e}")
            return False
    
    def _execute_actions(self, actions_list):
        """Execute a list of actions."""
        if not actions_list:
            return
        
        for action in actions_list:
            if self.stop_event.is_set():
                break
            self._execute_single_action(action)
    
    def _execute_single_action(self, action):
        """Execute a single action."""
        try:
            primary_monitor = [m for m in get_monitors() if m.is_primary][0]
            current_width, current_height = primary_monitor.width, primary_monitor.height
            
            time.sleep(action.get('dt', 0) / 1000.0)
            
            action_type = action.get('type')
            details = action.get('details', {})
            
            # Helper to get parameters from either the action root or a 'details' sub-dict
            def get_param(key, default=None):
                return action.get(key, details.get(key, default))

            if action_type == "mouse_move":
                xNorm = get_param('xNorm')
                yNorm = get_param('yNorm')
                if xNorm is not None and yNorm is not None:
                    x = int(xNorm * current_width)
                    y = int(yNorm * current_height)
                else: # Fallback to absolute coords
                    x = int(get_param('x', 0))
                    y = int(get_param('y', 0))
                self.mouse_controller.position = (x, y)
            
            elif action_type == "mouse_click":
                xNorm = get_param('xNorm')
                yNorm = get_param('yNorm')
                if xNorm is not None and yNorm is not None:
                    x = int(xNorm * current_width)
                    y = int(yNorm * current_height)
                else: # Fallback to absolute coords for legacy/flat format
                    x = int(get_param('x', 0))
                    y = int(get_param('y', 0))

                self.mouse_controller.position = (x, y)
                
                btn_name = get_param('button', 'left')
                btn_key = btn_name.lower()
                button = getattr(mouse.Button, btn_key, None)
                if button is None:
                    try:
                        button = mouse.Button[btn_name]
                    except Exception:
                        button = mouse.Button.left
                
                pressed = get_param('pressed', True)
                print(f"MacroPlayer: mouse_click {btn_name} at ({x},{y}) pressed={pressed}")
                
                if pressed:
                    self.mouse_controller.press(button)
                    time.sleep(0.08)
                else:
                    self.mouse_controller.release(button)
            
            elif action_type == "keyboard_key":
                key_str = get_param('key')
                pressed = get_param('pressed', True)
                try:
                    if isinstance(key_str, str) and key_str.startswith('Key.'):
                        key_name = key_str.split('.', 1)[1]
                        key_obj = getattr(keyboard.Key, key_name)
                    else:
                        k = key_str
                        if isinstance(k, str) and len(k) >= 2 and ((k[0] == "'" and k[-1] == "'") or (k[0] == '"' and k[-1] == '"')):
                            k = k[1:-1]
                        key_obj = k
                    
                    if pressed:
                        self.keyboard_controller.press(key_obj)
                        time.sleep(0.06)
                    else:
                        self.keyboard_controller.release(key_obj)
                except Exception:
                    txt = key_str if isinstance(key_str, str) else str(key_str)
                    self.keyboard_controller.type(txt)
            
            elif action_type == "keyboard_text":
                text = get_param('text', '')
                if text:
                    self.keyboard_controller.type(text)
            
            elif action_type == "notification":
                msg = get_param('message', 'Notification')
                # Try system notification backends if available
                try:
                    if plyer_notification:
                        plyer_notification.notify(title="AssistSense", message=str(msg), timeout=5)
                    elif _toast_notifier:
                        try:
                            _toast_notifier.show_toast("AssistSense", str(msg), duration=5, threaded=True)
                        except Exception:
                            print(f"Notification: {msg}")
                    else:
                        # Fallback: try showing a non-modal Qt message if a QApplication exists
                        try:
                            from PyQt6.QtWidgets import QMessageBox
                            from PyQt6.QtCore import QTimer, Qt
                            # Create a non-modal message box and auto-close it
                            app_box = QMessageBox()
                            app_box.setWindowTitle('AssistSense')
                            app_box.setText(str(msg))
                            app_box.setStandardButtons(QMessageBox.StandardButton.NoButton)
                            app_box.setWindowModality(Qt.WindowModality.NonModal)
                            app_box.show()
                            QTimer.singleShot(3000, app_box.close)
                        except Exception:
                            print(f"Notification: {msg}")
                except Exception as e:
                    print(f"Notification failed: {e}. Fallback to print: {msg}")
            
            elif action_type == "sound":
                sound_path = get_param('path')
                repeat = int(get_param('repeat', 1))
                if not sound_path or not os.path.exists(sound_path):
                    print(f"Sound file not found: {sound_path}")
                else:
                    # Determine best playback method
                    try:
                        played = False
                        ext = os.path.splitext(sound_path)[1].lower()
                        # Winsound supports WAV only
                        if platform.system() == 'Windows' and winsound and ext == '.wav':
                            for _ in range(repeat):
                                winsound.PlaySound(sound_path, winsound.SND_FILENAME)
                            played = True
                        # Try sounddevice + soundfile (supports many formats if soundfile installed)
                        if not played:
                            try:
                                import sounddevice as sd
                                import soundfile as sf
                                data, fs = sf.read(sound_path, dtype='float32')
                                for _ in range(repeat):
                                    sd.play(data, fs)
                                    sd.wait()
                                played = True
                            except Exception as e:
                                # Not available or failed
                                print(f"sounddevice/soundfile playback failed: {e}")
                        # Try playsound module (simple, supports mp3/wav)
                        if not played and _playsound:
                            try:
                                for _ in range(repeat):
                                    _playsound(sound_path)
                                played = True
                            except Exception as e:
                                print(f"playsound playback failed: {e}")
                        # Final fallback on Windows: try opening the file with default app (os.startfile)
                        if not played and platform.system() == 'Windows':
                            try:
                                os.startfile(sound_path)
                                played = True
                            except Exception as e:
                                print(f"os.startfile fallback failed: {e}")
                        if not played:
                            print(f"No suitable audio backend was available to play: {sound_path}")
                    except Exception as e:
                        print(f"Error playing sound: {e}")
        
        except Exception as e:
            print(f"Error executing action: {e}")
    
    def _execute_conditional_blocks(self, condition_blocks, else_actions):
        """Execute conditional blocks (IF/ELIF/ELSE logic)."""
        for block in condition_blocks:
            if self.stop_event.is_set():
                break
            
            if_cond = block.get('if')
            if self._evaluate_condition(if_cond):
                then_actions = block.get('then', [])
                self._execute_actions(then_actions)
                return
            
            elif_blocks = block.get('elif', [])
            if elif_blocks:
                for elif_block in elif_blocks:
                    if self.stop_event.is_set():
                        break
                    
                    elif_cond = elif_block.get('condition')
                    if self._evaluate_condition(elif_cond):
                        elif_actions = elif_block.get('actions', [])
                        self._execute_actions(elif_actions)
                        return
        
        self._execute_actions(else_actions)

    def play(self, macro_name: str) -> None:
        """Play a macro by name."""
        file_path = os.path.join(self.macro_dir, f"{macro_name}.json")
        if not os.path.exists(file_path):
            print(f"Error: Macro '{macro_name}' not found.")
            return

        with open(file_path, 'r') as f:
            macro_data = json.load(f)

        self.is_playing = True
        self.stop_event.clear()
        print(f"Playing macro: {macro_name}")

        is_looping = macro_data.get('loop', False)
        loop_interval_ms = macro_data.get('loop_interval', 1000)

        def _play_once():
            # Check if macro has condition_blocks (conditional execution)
            condition_blocks = macro_data.get('condition_blocks', [])
            if condition_blocks:
                # Execute conditional logic
                else_actions = macro_data.get('else_actions', [])
                self._execute_conditional_blocks(condition_blocks, else_actions)
            else:
                # Execute plain actions (backward compatibility)
                actions = macro_data.get('actions', [])
                self._execute_actions(actions)

        if is_looping:
            while not self.stop_event.is_set():
                _play_once()
                # Check stop event again before sleeping
                if self.stop_event.is_set():
                    break
                time.sleep(loop_interval_ms / 1000.0)
        else:
            _play_once()

        self.is_playing = False
        print("Playback finished.")

    def stop_playback(self) -> None:
        """Stop macro playback."""
        if self.is_playing:
            self.stop_event.set()
