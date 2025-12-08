# Macro Manager GUI - User Guide

## Accessing the Macro Manager

**Global Hotkey:** `Ctrl + '` (Ctrl + Single Quote)

Press this key combination anywhere while the application is running to open the macro manager GUI.

---

## Features

### Left Panel - Macro List

1. **Macros List**: Shows all existing macros loaded from `Macros_json/` folder
   - Click on any macro to edit it
   - Macros are displayed by their names

2. **Create New Macro**: Button at the bottom to create a new macro from scratch

### Right Panel - Editor

#### Editing Existing Macros

When you click on a macro in the left panel:

1. **Macro Name**: Displays the name (read-only)
2. **Trigger Tab**: 
   - **Trigger Type**: Select from:
     - `voice` - Voice command (e.g., "record", "play macro")
     - `keyboard_shortcut` - Key combination
     - `gesture` - Gesture input
     - `gaze` - Eye gaze
     - `battery` - Battery percentage condition
   - **Trigger Value**: Enter the specific trigger (e.g., "record macro")
   
3. **Actions Tab**:
   - Shows all actions organized by type
   - Click on action categories to expand/collapse
   - View all mouse clicks, movements, keyboard inputs, etc.

4. **Buttons**:
   - **Save Macro**: Save all changes to the macro JSON file
   - **Delete Macro**: Delete this macro permanently

#### Creating New Macros

When you click "Create New Macro":

1. **Macro Name**: Enter a unique name for your macro (e.g., "my_automation")

2. **Loop Settings**:
   - **Loop Macro**: Toggle to enable/disable looping
   - When enabled, the macro runs in a loop until you press **ESC**
   - **Loop Interval**: Set delay between loops (in milliseconds)

3. **Trigger Configuration**:
   - Select trigger type and enter trigger value (same as editing)

4. **Actions**: Add actions to perform
   - Buttons for each action type:
     - **Add Mouse Click**: Click at specific coordinates
       - X, Y coordinates
       - Button: left/right/middle
       - Delay after action (ms)
     - **Add Mouse Move**: Move mouse to coordinates
       - X, Y coordinates
       - Delay after action (ms)
     - **Add Keyboard Type**: Type text
       - Text to type
       - Delay after action (ms)
     - **Add Keyboard Key**: Press a key
       - Key name (e.g., "return", "shift", "ctrl+a")
       - Delay after action (ms)
   - **Delete Selected Action**: Remove an action from the list

5. **Create Macro**: Click to save the macro JSON file

---

## Action Details

### Mouse Click
- X, Y: Screen coordinates where to click
- Button: left, right, or middle mouse button
- Delay: Time to wait after click (typically 50-200ms)

### Mouse Move
- X, Y: Screen coordinates to move to
- Delay: Time to wait after moving (typically 10-50ms)

### Keyboard Type
- Text: Any text to type (e.g., "Hello World")
- Delay: Time to wait after typing (typically 20-50ms)

### Keyboard Key
- Key: Key name or combination (e.g., "return", "shift", "ctrl+a", "escape")
- Delay: Time to wait after key press (typically 50-100ms)

---

## JSON File Format

Macros are saved as JSON files in `Macros_json/` folder with the following structure:

```json
{
  "name": "my_macro",
  "created": "2025-12-07T10:30:00.123456",
  "modified": "2025-12-07T10:35:00.123456",
  "trigger": {
    "type": "voice",
    "value": "record"
  },
  "actions": [
    {
      "type": "mouse_move",
      "x": 100,
      "y": 200,
      "dt": 50
    },
    {
      "type": "mouse_click",
      "x": 100,
      "y": 200,
      "button": "left",
      "dt": 100
    },
    {
      "type": "keyboard_text",
      "text": "Hello",
      "dt": 50
    }
  ],
  "loop": false,
  "loop_interval": 1000
}
```

---

## Tips & Tricks

1. **For Looping Macros**: Always set a reasonable `loop_interval` to avoid CPU overload. 100ms minimum recommended.

2. **Stopping Loops**: Press **ESC** key to stop any looping macro.

3. **Precise Coordinates**: Get screen coordinates by hovering over target areas in your applications.

4. **Delays**: Add appropriate delays between actions for the system to register clicks/inputs:
   - Mouse clicks: 100-200ms
   - Keyboard: 50-100ms
   - After complex operations: 500ms+

5. **Testing**: Always test a macro with a small number of actions before expanding it.

---

## Macro Files Location

All macros are stored in: `Macros_json/` directory as `.json` files.

You can manually edit these files or use the GUI. Changes made in the GUI automatically update the JSON files.
