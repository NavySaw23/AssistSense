import os
import json
from .player import MacroPlayerService

class MacroTriggerService:
    def __init__(self, player: MacroPlayerService, macro_dir="Macros_json"):
        self.player = player
        self.macro_dir = macro_dir
        self.voice_trigger_map = {}
        self._load_triggers()

    def _load_triggers(self):
        """Scan the macro directory and load voice triggers."""
        print("Loading macro triggers...")
        if not os.path.exists(self.macro_dir):
            print(f"  Warning: Macro directory '{self.macro_dir}' not found.")
            return
        for filename in os.listdir(self.macro_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.macro_dir, filename)
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if data.get('trigger', {}).get('type') == 'voice':
                        voice_command = data['trigger']['value']
                        macro_name = data['name']
                        self.voice_trigger_map[voice_command.lower()] = macro_name
                        print(f"  - Registered voice command '{voice_command}' for macro '{macro_name}'")

    def on_voice_command(self, text: str):
        command = text.lower().strip()
        if command in self.voice_trigger_map:
            macro_name = self.voice_trigger_map[command]
            print(f"Voice command '{command}' matched. Playing macro '{macro_name}'.")
            self.player.play(macro_name)
