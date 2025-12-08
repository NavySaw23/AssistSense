import os
import json
from .player import MacroPlayerService

# Conditional imports for gaze and gesture engines
try:
    from app.helpers.gazeEngine import GazeEngine
    GAZE_AVAILABLE = True
except Exception as e:
    print(f"Warning: GazeEngine import failed: {e}")
    GazeEngine = None
    GAZE_AVAILABLE = False

try:
    from app.helpers.gestureEngine import GestureEngine
    GESTURE_AVAILABLE = True
except Exception as e:
    print(f"Warning: GestureEngine import failed: {e}")
    GestureEngine = None
    GESTURE_AVAILABLE = False

class MacroTriggerService:
    def __init__(self, player: MacroPlayerService, macro_dir="Macros_json"):
        self.player = player
        self.macro_dir = macro_dir
        self.voice_trigger_map = {}
        self.gaze_trigger_map = {}
        self.gesture_trigger_map = {}
        self.hotkey_trigger_map = {}
        self.battery_trigger_map = {}
        
        # Initialize engines for gaze and gesture
        self.gaze_engine = None
        self.gesture_engine = None
        
        if GAZE_AVAILABLE and GazeEngine:
            try:
                self.gaze_engine = GazeEngine()
                print("[OK] GazeEngine initialized")
            except Exception as e:
                print(f"[ERROR] Failed to initialize GazeEngine: {e}")
        
        if GESTURE_AVAILABLE and GestureEngine:
            try:
                self.gesture_engine = GestureEngine()
                print("[OK] GestureEngine initialized")
            except Exception as e:
                print(f"[ERROR] Failed to initialize GestureEngine: {e}")
        
        self._load_triggers()

    def _load_triggers(self):
        """Scan the macro directory and load all trigger types."""
        print("Loading macro triggers...")
        if not os.path.exists(self.macro_dir):
            print(f"  Warning: Macro directory '{self.macro_dir}' not found.")
            return
        
        for filename in os.listdir(self.macro_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.macro_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        trigger = data.get('trigger', {})
                        trigger_type = trigger.get('type')
                        trigger_value = trigger.get('value')
                        macro_name = data['name']
                        
                        if trigger_type == 'voice':
                            self.voice_trigger_map[trigger_value.lower()] = macro_name
                            print(f"  - Registered voice trigger: '{trigger_value}' -> '{macro_name}'")
                        
                        elif trigger_type == 'gaze':
                            if macro_name not in self.gaze_trigger_map:
                                self.gaze_trigger_map[macro_name] = []
                            self.gaze_trigger_map[macro_name].append(trigger_value)
                            print(f"  - Registered gaze trigger: '{trigger_value}' -> '{macro_name}'")
                        
                        elif trigger_type == 'gesture':
                            if macro_name not in self.gesture_trigger_map:
                                self.gesture_trigger_map[macro_name] = []
                            self.gesture_trigger_map[macro_name].append(trigger_value)
                            print(f"  - Registered gesture trigger: pattern → '{macro_name}'")
                        
                        elif trigger_type == 'keyboard_shortcut':
                            if macro_name not in self.hotkey_trigger_map:
                                self.hotkey_trigger_map[macro_name] = []
                            self.hotkey_trigger_map[macro_name].append(trigger_value)
                            print(f"  - Registered hotkey trigger: '{trigger_value}' -> '{macro_name}'")
                        
                        elif trigger_type == 'battery':
                            if macro_name not in self.battery_trigger_map:
                                self.battery_trigger_map[macro_name] = []
                            self.battery_trigger_map[macro_name].append(trigger_value)
                            print(f"  - Registered battery trigger: '{trigger_value}' -> '{macro_name}'")
                
                except Exception as e:
                    print(f"  Error loading trigger from {filename}: {e}")

    def on_voice_command(self, text: str):
        """Handle voice command triggers."""
        command = text.lower().strip()
        if command in self.voice_trigger_map:
            macro_name = self.voice_trigger_map[command]
            print(f"Voice command '{command}' matched. Playing macro '{macro_name}'.")
            self.player.play(macro_name)
    
    def check_gaze_trigger(self, frame):
        """Check if any gaze trigger matches and execute macro."""
        if not self.gaze_engine or frame is None:
            return
        
        try:
            # Get current gaze status from engine
            self.gaze_engine.process_frame(frame)
            current_status = self.gaze_engine.gazeStatus
            
            # Map status to trigger value
            status_map = {1: "looking", 0: "away", -1: None}
            trigger_value = status_map.get(current_status)
            
            if trigger_value is None:
                return
            
            # Check all macros with gaze triggers
            for macro_name, trigger_values in self.gaze_trigger_map.items():
                if trigger_value in trigger_values:
                    print(f"Gaze trigger '{trigger_value}' matched. Playing macro '{macro_name}'.")
                    self.player.play(macro_name)
        
        except Exception as e:
            print(f"Error checking gaze trigger: {e}")
    
    def check_gesture_trigger(self, frame):
        """Check if any gesture trigger matches and execute macro."""
        if not self.gesture_engine or frame is None:
            return
        
        try:
            # Get current gesture pattern from engine
            self.gesture_engine.process_frame(frame)
            current_pattern = self.gesture_engine.fingerStatus
            
            # Check all macros with gesture triggers
            for macro_name, trigger_patterns in self.gesture_trigger_map.items():
                for trigger_pattern in trigger_patterns:
                    # Parse trigger pattern string to list
                    import ast
                    try:
                        target_pattern = ast.literal_eval(trigger_pattern)
                        if isinstance(target_pattern, list) and len(target_pattern) == 10:
                            # Check if current pattern matches trigger pattern
                            if self._gesture_matches(current_pattern, target_pattern):
                                print(f"Gesture trigger matched. Playing macro '{macro_name}'.")
                                self.player.play(macro_name)
                    except:
                        pass
        
        except Exception as e:
            print(f"Error checking gesture trigger: {e}")
    
    def _gesture_matches(self, current, target):
        """
        Check if current gesture pattern matches target pattern.
        Ignores -1 (not detected) positions in target pattern.
        """
        if len(current) != len(target):
            return False
        
        for i in range(len(current)):
            target_val = target[i]
            if target_val != -1:  # -1 means "don't care" in target
                if current[i] != target_val:
                    return False
        
        return True
    
    def check_battery_trigger(self, current_battery_level):
        """
        Check if any battery trigger matches current battery level and execute macro.
        
        Args:
            current_battery_level (int): Current battery level as percentage (0-100)
        
        Battery trigger format examples: "<20", "<=30", ">50", ">=80", "==100", "!=75"
        """
        for macro_name, trigger_values in self.battery_trigger_map.items():
            for trigger_value in trigger_values:
                # Parse trigger value format: "operator+number" e.g., "<20", ">=80"
                if self._battery_condition_matches(current_battery_level, trigger_value):
                    print(f"Battery trigger '{trigger_value}' matched (current: {current_battery_level}%). Playing macro '{macro_name}'.")
                    self.player.play(macro_name)
    
    def _battery_condition_matches(self, current_level, condition_str):
        """
        Evaluate battery condition string against current battery level.
        
        Args:
            current_level (int): Current battery level (0-100)
            condition_str (str): Condition string e.g., "<20", ">=80", "==50"
        
        Returns:
            bool: True if condition matches, False otherwise
        """
        try:
            # Extract operator and value from condition string
            # Format: operator (1-2 chars) followed by number
            for op_len in [2, 1]:  # Try 2-char operators first (<=, >=, ==, !=), then 1-char
                op = condition_str[:op_len]
                if op in ['<', '<=', '>', '>=', '==', '!=']:
                    try:
                        value = int(condition_str[op_len:])
                    except ValueError:
                        continue
                    
                    # Evaluate condition
                    if op == '<':
                        return current_level < value
                    elif op == '<=':
                        return current_level <= value
                    elif op == '>':
                        return current_level > value
                    elif op == '>=':
                        return current_level >= value
                    elif op == '==':
                        return current_level == value
                    elif op == '!=':
                        return current_level != value
            
            # If we couldn't parse the condition, log it and return False
            print(f"Warning: Could not parse battery trigger condition: '{condition_str}'")
            return False
        
        except Exception as e:
            print(f"Error evaluating battery condition '{condition_str}': {e}")
            return False

