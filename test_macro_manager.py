#!/usr/bin/env python3
"""
Quick test to verify macro manager GUI imports and initialization works.
"""
import sys
sys.path.insert(0, '.')

print("Testing macro manager GUI components...")

try:
    from app.macro_manager_gui import (
        TriggerEditor, ActionEditor, MacroEditorPanel, 
        NewMacroPanel, ActionDialog, MacroManagerWindow
    )
    print("✓ Macro manager GUI components imported successfully")
except ImportError as e:
    print(f"✗ Failed to import macro manager GUI: {e}")
    sys.exit(1)

try:
    from macros.macro_json_manager import MacroJsonManager
    print("✓ MacroJsonManager imported successfully")
except ImportError as e:
    print(f"✗ Failed to import MacroJsonManager: {e}")
    sys.exit(1)

try:
    manager = MacroJsonManager()
    macros = manager.list_macros()
    print(f"✓ MacroJsonManager initialized, found {len(macros)} macros")
except Exception as e:
    print(f"✗ Failed to initialize MacroJsonManager: {e}")
    sys.exit(1)

print("\n✓ All macro manager components loaded successfully!")
print("\nTo open the macro manager GUI while the app is running, press: Ctrl + '")
