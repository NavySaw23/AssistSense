#!/usr/bin/env python3
"""
Quick test to verify newly saved macros are registered and can be triggered.
"""
import os
import json
from macros.player import MacroPlayerService
from macros.trigger import MacroTriggerService

# Initialize services
player = MacroPlayerService(macro_dir='Macros_json')
trigger_service = MacroTriggerService(player=player, macro_dir='Macros_json')

print("=" * 60)
print("Registered triggers after load:")
print(trigger_service.voice_trigger_map)
print("=" * 60)

# Get the most recently saved macro (should be macro_20251207_162422.json with 'opera' trigger)
macro_files = sorted([f for f in os.listdir('Macros_json') if f.endswith('.json')])
if macro_files:
    latest = macro_files[-1]
    with open(os.path.join('Macros_json', latest)) as f:
        data = json.load(f)
        print(f"\nLatest macro file: {latest}")
        print(f"Trigger in JSON: {data.get('trigger')}")
        print(f"Macro name in JSON: {data.get('name')}")

# Now reload triggers to simulate what main.py does after saving
print("\nReloading triggers...")
trigger_service._load_triggers()

print("\nRegistered triggers after reload:")
print(trigger_service.voice_trigger_map)

# Try to trigger with 'opera'
print("\nTesting voice command 'opera'...")
trigger_service.on_voice_command('opera')

print("\nTest complete!")
