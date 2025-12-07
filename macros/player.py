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
            cond_type = condition_dict.get('type', '')
            
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
            
            if action_type == "mouse_move":
                x = int(details.get('xNorm', 0) * current_width)
                y = int(details.get('yNorm', 0) * current_height)
                self.mouse_controller.position = (x, y)
            
            elif action_type == "mouse_click":
                x = int(details.get('xNorm', 0) * current_width)
                y = int(details.get('yNorm', 0) * current_height)
                self.mouse_controller.position = (x, y)
                
                btn_name = details.get('button', 'left')
                btn_key = btn_name.lower()
                button = getattr(mouse.Button, btn_key, None)
                if button is None:
                    try:
                        button = mouse.Button[btn_name]
                    except Exception:
                        button = mouse.Button.left
                
                pressed = details.get('pressed', True)
                print(f"MacroPlayer: mouse_click {btn_name} at ({x},{y}) pressed={pressed}")
                
                if pressed:
                    self.mouse_controller.press(button)
                    time.sleep(0.08)
                else:
                    self.mouse_controller.release(button)
            
            elif action_type == "keyboard_key":
                key_str = details.get('key')
                pressed = details.get('pressed', True)
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
                text = details.get('text', '')
                if text:
                    self.keyboard_controller.type(text)
            
            elif action_type == "notification":
                msg = action.get('message') or (details.get('message') if isinstance(details, dict) else None)
                print(f"Notification: {msg}")
            
            elif action_type == "sound":
                sound_path = action.get('path') or (details.get('path') if isinstance(details, dict) else None)
                repeat = int(action.get('repeat', 1)) if action.get('repeat', None) is not None else int(details.get('repeat', 1) if isinstance(details, dict) else 1)
                if not sound_path or not os.path.exists(sound_path):
                    print(f"Sound file not found: {sound_path}")
                else:
                    try:
                        if platform.system() == 'Windows' and winsound:
                            for _ in range(repeat):
                                winsound.PlaySound(sound_path, winsound.SND_FILENAME)
                        else:
                            try:
                                import sounddevice as sd
                                import soundfile as sf
                                data, fs = sf.read(sound_path, dtype='float32')
                                for _ in range(repeat):
                                    sd.play(data, fs)
                                    sd.wait()
                            except Exception as e:
                                print(f"No suitable audio backend available: {e}")
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

        self.is_playing = False
        print("Playback finished.")

    def stop_playback(self) -> None:
        """Stop macro playback."""
        if self.is_playing:
            self.stop_event.set()
