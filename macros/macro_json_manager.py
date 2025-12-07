"""
Macro JSON serialization and deserialization utilities.
"""
import json
import os
from datetime import datetime


class MacroJsonManager:
    """Manages reading and writing macro JSON files."""
    
    def __init__(self, macro_dir="Macros_json"):
        self.macro_dir = macro_dir
        os.makedirs(macro_dir, exist_ok=True)
    
    def save_macro(self, macro_name, trigger=None, actions=None, loop=False, loop_interval=1000, condition_blocks=None, else_actions=None):
        """
        Save a macro to JSON file.
        
        Args:
            macro_name: Name of the macro
            trigger: Dict with 'type' and 'value' keys
            actions: List of action dicts
            loop: Whether macro loops
            loop_interval: Interval between loops in ms
        """
        macro_data = {
            "name": macro_name,
            "created": datetime.now().isoformat(),
            "loop": loop,
            "loop_interval": loop_interval
        }

        # Backwards-compatible: either store simple trigger/actions or structured condition blocks
        if condition_blocks is not None:
            macro_data['condition_blocks'] = condition_blocks
            macro_data['else_actions'] = else_actions or []
        else:
            macro_data['trigger'] = trigger or {"type": "voice", "value": ""}
            macro_data['actions'] = actions or []
        
        filename = f"{macro_name}.json"
        filepath = os.path.join(self.macro_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(macro_data, f, indent=2)
        
        print(f"Macro saved: {filepath}")
        return filepath
    
    def load_macro(self, macro_name):
        """Load a macro from JSON file."""
        filename = f"{macro_name}.json"
        filepath = os.path.join(self.macro_dir, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Macro file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            macro_data = json.load(f)
        
        return macro_data
    
    def update_macro(self, macro_name, trigger=None, actions=None, loop=None, loop_interval=None, condition_blocks=None, else_actions=None):
        """
        Update an existing macro.
        
        Args:
            macro_name: Name of the macro to update
            trigger: New trigger dict (optional)
            actions: New actions list (optional)
            loop: New loop setting (optional)
            loop_interval: New loop interval (optional)
        """
        macro_data = self.load_macro(macro_name)
        
        # Update either structured condition blocks or the simple trigger/actions
        if condition_blocks is not None:
            macro_data['condition_blocks'] = condition_blocks
            macro_data['else_actions'] = else_actions or []
            # Keep or update trigger when provided alongside structured condition blocks
            if trigger is not None:
                macro_data['trigger'] = trigger
            # remove flat actions if present (we now prefer structured condition blocks)
            macro_data.pop('actions', None)
        else:
            if trigger is not None:
                macro_data['trigger'] = trigger
            if actions is not None:
                macro_data['actions'] = actions
        if loop is not None:
            macro_data['loop'] = loop
        if loop_interval is not None:
            macro_data['loop_interval'] = loop_interval
        
        macro_data['modified'] = datetime.now().isoformat()
        
        filename = f"{macro_name}.json"
        filepath = os.path.join(self.macro_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(macro_data, f, indent=2)
        
        print(f"Macro updated: {filepath}")
        return filepath
    
    def delete_macro(self, macro_name):
        """Delete a macro JSON file."""
        filename = f"{macro_name}.json"
        filepath = os.path.join(self.macro_dir, filename)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Macro deleted: {filepath}")
        else:
            raise FileNotFoundError(f"Macro file not found: {filepath}")
    
    def list_macros(self):
        """List all macro names in the macro directory."""
        macros = []
        if os.path.exists(self.macro_dir):
            for filename in os.listdir(self.macro_dir):
                if filename.endswith('.json'):
                    macro_name = filename[:-5]  # Remove .json extension
                    macros.append(macro_name)
        return macros
    
    def get_all_macros(self):
        """Get all macro data."""
        all_macros = {}
        for macro_name in self.list_macros():
            try:
                all_macros[macro_name] = self.load_macro(macro_name)
            except Exception as e:
                print(f"Error loading macro {macro_name}: {e}")
        return all_macros


# Example macro structure for reference:
EXAMPLE_MACRO = {
    "name": "example_macro",
    "created": "2025-12-07T10:30:00.123456",
    "modified": "2025-12-07T10:35:00.123456",
    "trigger": {
        "type": "voice",  # voice, keyboard_shortcut, gesture, gaze, battery
        "value": "record"
    },
    "actions": [
        {
            "type": "mouse_move",
            "x": 100,
            "y": 200,
            "dt": 500  # delay in ms
        },
        {
            "type": "mouse_click",
            "x": 100,
            "y": 200,
            "button": "left",  # left, right, middle
            "pressed": True,
            "dt": 100
        },
        {
            "type": "keyboard_text",
            "text": "Hello World",
            "dt": 50
        },
        {
            "type": "keyboard_key",
            "key": "return",  # shift, ctrl, alt, etc.
            "dt": 100
        }
    ],
    "loop": False,
    "loop_interval": 1000  # milliseconds between loops
}
