# AssistSense - Complete User & Developer Guide

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Installation & Setup](#installation--setup)
4. [Quick Start](#quick-start)
5. [Features & How to Use](#features--how-to-use)
6. [Macro System](#macro-system)
7. [Voice Commands](#voice-commands)
8. [Advanced: Conditional Macros](#advanced-conditional-macros)
9. [Troubleshooting](#troubleshooting)

---

## Overview

**AssistSense** is an intelligent macro recording and playback system with voice control and advanced conditional logic. It allows you to:

- **Record macros** via hotkey (Ctrl+Shift+0) or voice command
- **Create voice-triggered macros** that execute pre-defined actions
- **Build conditional macros** with if/then/else logic
- **Manage macros** through an intuitive GUI (Ctrl+')
- **Perform complex actions** including mouse movements, clicks, keyboard input, notifications, and launching applications

---

## System Architecture

### High-Level Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        AssistSense Main App                      │
│                     (main.py - Entry Point)                      │
└────────────┬────────────────────────────────────────────────────┘
             │
             ├─────────────────────────────────────────────────┐
             │                                                 │
             ▼                                                 ▼
    ┌──────────────────────┐                       ┌──────────────────────┐
    │   Voice Listener     │                       │   GUI Main Window    │
    │  (voiceRecog.py)     │                       │   (app/gui.py)       │
    │                      │                       │                      │
    │ • Microphone input   │                       │ • Display status     │
    │ • Wake word detect   │                       │ • Show recordings    │
    │ • Speech recogn.     │                       │ • Voice display      │
    │ • Text output        │                       │                      │
    └──────────┬───────────┘                       └──────────┬───────────┘
               │                                              │
               │ (QThread wrapper)                            │
               │                                              │
               ▼                                              ▼
    ┌──────────────────────┐                       ┌──────────────────────┐
    │    Controller        │                       │  Macro Manager GUI   │
    │  (app/controller.py) │                       │ (app/macro_manager   │
    │                      │◄──── Signals ────────►│      _gui.py)        │
    │ • Record toggle      │                       │                      │
    │ • Finalize macro     │                       │ • Edit triggers      │
    │ • Trigger signals    │                       │ • Edit actions       │
    │ • Hotkey handling    │                       │ • Build conditionals │
    └──────────┬───────────┘                       │ • Manage macros      │
               │                                   └──────────┬───────────┘
               │                                              │
        ┌──────┴──────────────────────────────────────────────┴────┐
        │                                                           │
        ▼                                                           ▼
┌─────────────────────────────────┐             ┌────────────────────────────┐
│    Macro Recorder Service       │             │   Macro JSON Manager       │
│   (macros/recorder.py)          │             │  (macros/macro_json_mgr.py)│
│                                 │             │                            │
│ • Capture mouse movements       │             │ • Save macros to JSON      │
│ • Record keyboard input         │             │ • Load macros from file    │
│ • Capture clicks (normalized)   │             │ • Update existing macros   │
│ • Update trigger info           │             │ • Delete macro files       │
│ • Save to JSON                  │             │ • Format: flat or          │
└────────────┬────────────────────┘             │   structured (if/else)    │
             │                                  └────────────┬───────────────┘
             │                                               │
             └───────────────────┬──────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   Macros_json/ Folder  │
                    │                        │
                    │ • test_unconditional   │
                    │ • test_if_battery_low  │
                    │ • test_if_voice_then_  │
                    │   click                │
                    │ • backup/              │
                    │   (old macro backups)  │
                    └────────┬───────────────┘
                             │
                             ▼
                    ┌────────────────────────┐
                    │   Macro Trigger Service│
                    │   (macros/trigger.py)  │
                    │                        │
                    │ • Load triggers on     │
                    │   app startup          │
                    │ • Build voice_trigger_ │
                    │   map                  │
                    │ • On voice command:    │
                    │   match & execute      │
                    └────────┬───────────────┘
                             │
                             ▼
                    ┌────────────────────────┐
                    │   Macro Player         │
                    │   (macros/player.py)   │
                    │                        │
                    │ • Replay recorded      │
                    │   actions sequentially │
                    │ • Normalize coords     │
                    │ • Execute:             │
                    │   - Mouse moves/clicks │
                    │   - Keyboard input     │
                    │   - Notifications      │
                    │   - App launching      │
                    │ • Handle timing delays │
                    └────────────────────────┘
```

### Component Details

| Component | File | Purpose |
|-----------|------|---------|
| **VoiceListener** | `voiceRecog/voiceRecog.py` | Captures microphone input, recognizes speech, buffers text |
| **MacroRecorderService** | `macros/recorder.py` | Records user actions (mouse, keyboard) with timestamps |
| **MacroPlayer** | `macros/player.py` | Replays recorded actions, normalizes coordinates for different screen sizes |
| **MacroTriggerService** | `macros/trigger.py` | Maps voice commands to macros, executes playback on trigger |
| **MacroJsonManager** | `macros/macro_json_manager.py` | Persists macros to JSON files, supports both flat and structured formats |
| **Controller** | `app/controller.py` | Central hub coordinating voice listener, recorder, and trigger service |
| **MacroManagerWindow** | `app/macro_manager_gui.py` | GUI for editing macros, triggers, actions, and conditionals |
| **Main App** | `main.py` | Entry point, initializes all services, registers global hotkeys |

---

## Installation & Setup

### Prerequisites
- Windows OS (for global hotkey support)
- Python 3.8+
- Microphone

### Step 1: Clone/Extract Project
```bash
cd c:\Users\[YourUsername]\OneDrive\Documents\AssistSense
```

### Step 2: Create Virtual Environment
```powershell
python -m venv .venv
```

### Step 3: Activate Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

**Key dependencies:**
- `PyQt6` — GUI framework
- `pyaudio` — Microphone input
- `speech_recognition` — Voice-to-text
- `pynput` — Global hotkeys & input simulation
- `screeninfo` — Screen resolution detection
- `mediapipe` — Optional gesture detection (initialized but not fully used yet)

### Step 5: Run the App
```powershell
.\.venv\Scripts\python.exe main.py
```

On first run:
- Microphone calibration will occur (stay quiet for ~3 seconds)
- Global hotkeys will be registered
- Macro triggers will be loaded
- Voice listener will start in passive mode (waiting for wake word)

---

## Quick Start

### 1. Open Macro Manager
Press **Ctrl+'** (Ctrl + apostrophe) to open the Macro Manager GUI.

### 2. Record a Simple Macro
1. Click **"Create New Macro"** button (left panel)
2. Enter macro name: `"My First Macro"`
3. In the **Trigger** tab, set:
   - Trigger Type: `voice`
   - Trigger Value: `my macro` (what you'll say to trigger it)
4. Click **"Create Macro"**

Now go to the macro in the list and click it to edit.

### 3. Add Actions to the Macro
1. Go to the **Actions** tab
2. Click **"Add Action"** button
3. Select action type, e.g., `keyboard_text`
4. Enter text to type: `Hello World`
5. Click **OK**
6. Click **"Save Macro"**

### 4. Test the Macro
Say the trigger phrase out loud: **"my macro"**
- The macro will execute and type "Hello World"

---

## Features & How to Use

### Recording Macros via Hotkey

**Hotkey:** `Ctrl+Shift+0` (to start/stop recording)

**Steps:**
1. Press **Ctrl+Shift+0** to start recording
2. You'll see a dialog asking for trigger type and value
3. Perform your actions:
   - Move mouse
   - Click buttons
   - Type text
   - Press keys
4. Press **Ctrl+Shift+0** again to stop recording
5. A dialog appears asking how to trigger the macro:
   - Select trigger type (voice, hotkey, gesture, gaze, battery)
   - Enter trigger value (e.g., voice command text)
6. Macro is saved and immediately available

### Macro Manager GUI (`Ctrl+'`)

#### Left Panel - Macro List
- Shows all available macros
- Click a macro to edit it
- **"Create New Macro"** button to start a new one

#### Right Panel - Macro Editor (3 Tabs)

**Tab 1: Trigger**
- Set what activates the macro
- **Each trigger type has its own custom UI editor:**

##### Voice Command Trigger
- Simple text input for voice commands
- Example: "open notepad", "record", "start"
- Triggers when user speaks the exact phrase

##### Keyboard Shortcut Trigger
- Text input for hotkey combinations
- Example: "ctrl+alt+a", "shift+f5"
- Triggers when user presses the hotkey

##### Battery Level Trigger
- **Operator-based configuration with mathematical expressions**
- Select operator: `<`, `<=`, `>`, `>=`, `==`, `!=`
- Select percentage value (0-100%)
- Example configurations:
  - `< 20%` → Triggers when battery drops below 20%
  - `<= 30%` → Triggers when battery is 30% or less
  - `> 50%` → Triggers when battery is above 50%
  - `== 80%` → Triggers when battery is exactly 80%
- Use cases:
  - Low battery warning: `< 15%` → Show notification + play sound
  - Mid-battery check: `>= 40%` → Hide low-battery UI
  - Specific threshold: `== 100%` → Celebration sound on full charge

##### Gesture Trigger (Hand Detection)
- Visual 10-button hand editor
- Click each finger to set state: open (1) / closed (0) / not detected (-1)
- Example patterns:
  - Left hand all open: left side all buttons green
  - Thumbs up: left thumb button green, others red
  - Peace sign: left/right pinky buttons green
- Triggers when detected hand matches the pattern

##### Gaze Trigger (Eye Detection)
- Simple dropdown: "looking" or "away"
- "looking" → Triggers when user looks at screen
- "away" → Triggers when user looks away
- Use cases:
  - Auto-pause video when user looks away
  - Lock screen when user turns head
  - Show notification only when looking

**Tab 2: Actions**
- Merged actions and conditional blocks into one tab
- All action types including **sound** are available here

##### Gaze Trigger (Eye Gaze Detection)

**What it does:** Detects if the user is looking at the screen or looking away using computer vision (mediapipe FaceMesh).

**How to use:**
1. In Macro Manager, set Trigger Type to `gaze`
2. Select trigger value: `"looking"` or `"away"`
3. Macro triggers when the user's gaze matches the selected state

**Technical Details:**
- Uses mediapipe FaceMesh to detect face landmarks
- Calculates gaze direction based on iris center and eye corner positions
- Returns status: `1` (looking at screen) or `0` (looking away)
- Automatically returns `-1` if no face is detected
- Calibrated threshold values: horizontal ratio ∈ [0.00, 0.10], vertical ratio ∈ [-0.40, -0.20]

**Examples:**
- Trigger: `"looking"` → Macro activates when user is actively looking at screen
- Trigger: `"away"` → Macro activates when user looks away (checking phone, etc.)

**Use Cases:**
- "Pause video when I look away"
- "Lock screen when I turn my head"
- "Show notification only when looking at screen"

##### Gesture Trigger (Hand Gesture / Finger Detection)

**What it does:** Detects hand gestures and individual finger positions using computer vision (mediapipe Hands).

**How to use:**
1. In Macro Manager, set Trigger Type to `gesture`
2. Configure finger pattern using 10-element array or visual hand selector
3. Macro triggers when detected hand matches the configured pattern

**Finger Array Structure (10 elements):**
- **Elements 0-4:** Left Hand (from pinky to thumb)
  - `fingerStatus[0]` = Left Pinky
  - `fingerStatus[1]` = Left Ring
  - `fingerStatus[2]` = Left Middle
  - `fingerStatus[3]` = Left Index
  - `fingerStatus[4]` = Left Thumb
- **Elements 5-9:** Right Hand (from thumb to pinky)
  - `fingerStatus[5]` = Right Thumb
  - `fingerStatus[6]` = Right Index
  - `fingerStatus[7]` = Right Middle
  - `fingerStatus[8]` = Right Ring
  - `fingerStatus[9]` = Right Pinky

**Finger Status Values (per element):**
- `0` = Finger closed (fist)
- `1` = Finger open (extended)
- `-1` = Finger not detected (hand not visible)

**Examples:**
- Trigger: `[1, 1, 1, 1, 1, -1, -1, -1, -1, -1]` → Left hand all fingers open, right hand not visible
- Trigger: `[0, 0, 0, 0, 1, -1, -1, -1, -1, -1]` → Left thumbs up, other fingers closed
- Trigger: `[1, 0, 0, 0, 0, 0, 0, 0, 0, 1]` → Left pinky + right pinky open (peace sign both hands)

**Use Cases:**
- "Thumbs up gesture → Play next song"
- "Peace sign with both hands → Take screenshot"
- "Left hand all open → Maximize window"
- "Rock sign (middle + pinky open) → Volume up"

**Tab 2: Actions**
- List of sequential actions to perform when macro triggers
- Supported action types:

| Action Type | Parameters | Example |
|-------------|-----------|---------|
| `mouse_move` | x, y, delay | Move to (500, 300), wait 50ms |
| `mouse_click` | x, y, button, delay | Click at (500, 300) with left button, wait 100ms |
| `keyboard_text` | text, delay | Type "Hello", wait 50ms |
| `keyboard_key` | key, delay | Press Enter key, wait 100ms |
| `notification` | message | Show "Task Complete" notification |
| `open_application` | app_path | Launch Notepad.exe |

**Tab 3: Conditionals (If/Else)** ⭐ **NEW**
- Build structured conditional blocks
- Each block has:
  - **IF** section — Define condition (true, voice_match, battery, custom)
  - **THEN** section — Actions to execute if condition is true
  - **ELSE** section — Fallback actions if condition is false

---

## Macro System

### Data Format

Macros are stored as JSON files in `Macros_json/` folder.

#### Simple Macro Example
```json
{
  "name": "type_hello",
  "created": "2025-12-07T12:00:00",
  "trigger": {
    "type": "voice",
    "value": "say hello"
  },
  "actions": [
    {
      "type": "keyboard_text",
      "text": "Hello, World!",
      "dt": 50
    }
  ],
  "loop": false,
  "loop_interval": 1000
}
```

#### Structured Conditional Macro Example
```json
{
  "name": "battery_check",
  "created": "2025-12-07T12:00:00",
  "trigger": {
    "type": "voice",
    "value": "battery check"
  },
  "condition_blocks": [
    {
      "if": { "type": "battery", "value": "20", "op": "<" },
      "then": [
        { "type": "notification", "message": "Battery Low!" },
        { "type": "open_application", "app_path": "calc.exe" }
      ],
      "else": [
        { "type": "notification", "message": "Battery OK" }
      ]
    }
  ]
}
```

### Macro Lifecycle

```
1. CREATION
   ├─ Via Hotkey Recording (Ctrl+Shift+0)
   │  └─ Actions captured, saved, trigger configured
   │
   └─ Via Manual Creation (Macro Manager GUI)
      └─ Trigger & actions set manually

2. STORAGE
   └─ JSON file written to Macros_json/[name].json

3. LOADING
   ├─ App startup: MacroTriggerService._load_triggers()
   ├─ Reads all JSON files in Macros_json/
   ├─ Builds voice_trigger_map: {voice_command → macro_name}
   └─ Prints registered commands to console

4. EXECUTION
   ├─ User speaks trigger phrase OR presses trigger hotkey
   ├─ MacroTriggerService.on_voice_command() matches trigger
   ├─ Looks up macro name in voice_trigger_map
   ├─ MacroPlayer.play(macro_name)
   ├─ Actions executed sequentially:
   │  ├─ Mouse moves with timing
   │  ├─ Clicks at normalized coordinates
   │  ├─ Keyboard input sent
   │  ├─ Notifications shown
   │  └─ Applications launched
   └─ Macro complete

5. EDITING
   ├─ Open Macro Manager (Ctrl+')
   ├─ Click macro to edit
   ├─ Modify Trigger/Actions/Conditionals tabs
   ├─ Click "Save Macro"
   └─ Changes persisted to JSON immediately

6. DELETION
   └─ Click macro, press "Delete Macro" button
      └─ JSON file deleted from Macros_json/
```

---

## Voice Commands

### How Voice Recognition Works

```
┌──────────────────────────────┐
│   Microphone Input (Passive) │
│   (VoiceListener active)     │
└──────────────┬───────────────┘
               │ (continuous listening)
               ▼
┌──────────────────────────────┐
│   Wake Word Detection        │
│   (Listens for "listen" or   │
│    custom wake word)         │
└──────────────┬───────────────┘
               │ (wake word detected)
               ▼
┌──────────────────────────────┐
│   Recognize Speech           │
│   (Google API or Whisper)    │
│   speech → text              │
└──────────────┬───────────────┘
               │ (text output)
               ▼
┌──────────────────────────────┐
│  Text → MacroTriggerService  │
│  Match against voice_trigger │
│  _map                        │
└──────────────┬───────────────┘
               │ (if matched)
               ▼
┌──────────────────────────────┐
│   Execute Macro              │
│   (MacroPlayer.play)         │
└──────────────────────────────┘
```

### Registered Voice Commands (Default Test Macros)
- **"test run"** — Unconditional macro (move, click, type)
- **"battery test"** — Conditional battery check
- **"start show"** — Conditional voice match + actions

### Add Custom Voice Command

1. Open Macro Manager (Ctrl+')
2. Create or edit a macro
3. In **Trigger** tab:
   - Set Trigger Type: `voice`
   - Set Trigger Value: your phrase (e.g., "open notepad")
4. Save macro
5. Say the exact phrase to trigger it

---

## Advanced: Conditional Macros

### What Are Conditionals?

Conditionals let you define **if → then → else** logic for macros. Instead of always executing the same actions, macros can check conditions and execute different actions based on results.

### Creating a Conditional Macro

**Example: "If battery is low, show alert; else show OK"**

1. Open Macro Manager (Ctrl+')
2. Click a macro to edit (or create new)
3. Go to **Conditionals (If/Else)** tab
4. Click **"+ Add If/Else Block"** button

You'll see:

```
┌─────────────────────────────────────────┐
│          Conditional Block              │
├─────────────────────────────────────────┤
│                                         │
│  ┌────────────────────────────────────┐ │
│  │  IF Condition                      │ │
│  ├────────────────────────────────────┤ │
│  │  Condition type: [Dropdown ▼]      │ │
│  │  Options: true, voice_match,       │ │
│  │           battery, custom          │ │
│  └────────────────────────────────────┘ │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │  THEN - Actions to perform         │ │
│  ├────────────────────────────────────┤ │
│  │  3 actions                         │ │
│  │  [Add Action to THEN] Button       │ │
│  └────────────────────────────────────┘ │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │  ELSE - Fallback actions           │ │
│  ├────────────────────────────────────┤ │
│  │  0 actions                         │ │
│  │  [Add Action to ELSE] Button       │ │
│  └────────────────────────────────────┘ │
│                                         │
│  [Delete This Block] Button             │
└─────────────────────────────────────────┘
```

### Condition Types

| Type | What It Checks | Example |
|------|---|---|
| `true` | Always true (unconditional execution) | Always run these actions |
| `voice_match` | Specific voice command matches | If user said "start" |
| `battery` | System battery level | If battery < 20% |
| `custom` | Custom condition (extensible) | If time > 5 PM |

### Adding Actions to Conditionals

1. Click **"Add Action to THEN"** to add action if condition is true
2. Choose action type (mouse_click, keyboard_text, notification, etc.)
3. Configure action parameters
4. Click OK
5. Repeat for ELSE section if needed
6. Click **"Save Macro"**

### Example: Battery Check Macro

**Scenario:** "When I say 'battery status', check if battery is low"

**Step-by-Step:**
1. Create new macro named `battery_status`
2. Trigger: voice, value: `"battery status"`
3. In Conditionals tab, click **"+ Add If/Else Block"**
4. Set condition: `battery`
5. Add to THEN: notification with message "Battery Low - Plug in soon!"
6. Add to ELSE: notification with message "Battery Level is Good"
7. Save macro

**When user says "battery status":**
- System checks battery level
- If < threshold → shows "Battery Low" notification
- Otherwise → shows "Battery Level is Good" notification

---

## Troubleshooting

### App won't start / "ModuleNotFoundError"

**Solution:**
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt --upgrade
```

### Microphone not detected

**Solution:**
1. Check Windows audio settings (Settings → Sound)
2. Ensure microphone is enabled and not muted
3. Restart the app
4. If issue persists, try another microphone

### Voice commands not working

**Possible causes:**
1. **Not saying exact phrase** — Voice matching is case-sensitive
2. **Wake word not said** — Always say wake word first (default: "listen")
3. **Microphone too quiet** — Speak clearly, closer to mic
4. **Internet issue** — If using Google API, need working internet

**Debug:**
- Check console output for registered voice commands
- Try adjusting microphone volume in Windows Settings

### Macro not playing back

**Causes:**
1. **Coordinates outside screen** — Macros recorded on different resolution
   - Solution: Re-record macro or adjust coordinates in Actions tab
2. **Actions out of order** — Check Actions tab and reorder
3. **Timing issues** — Increase delay between actions

**Debug:**
```powershell
# Add debug prints to macros/player.py to trace playback
# Look for: "Playing macro:" and "MacroPlayer:" debug outputs in console
```

### Macro Manager window is blank/white

**Cause:** GUI rendering issue (fixed in latest version)

**Solution:**
1. Close window (Alt+F4)
2. Restart app
3. Press Ctrl+' again

### Can't save macro changes

**Cause:** JSON permission issue

**Solution:**
1. Ensure `Macros_json/` folder exists
2. Check folder permissions (right-click → Properties → Security)
3. Ensure no other app is locking macro files
4. Restart app

### Old macros disappeared

**Recovery:**
```powershell
# All old macros are in:
# Macros_json/backup_20251207_120000/

# Copy any needed macros back to Macros_json/ folder
Copy-Item "Macros_json/backup_20251207_120000/*.json" "Macros_json/" -Force
```

---

## Tips & Best Practices

### Recording Tips
1. **Move slowly** — Fast movements may not be captured accurately
2. **Clear workspace** — Before recording, close unnecessary windows
3. **Test immediately** — After recording, test the macro to ensure it works
4. **Keep macros short** — Easier to debug, faster to execute

### Voice Commands Best Practices
1. **Use distinct phrases** — "open notepad" not "notepad"
2. **Test in quiet environment** — Background noise reduces accuracy
3. **Speak clearly** — Proper pronunciation improves recognition
4. **Avoid too many similar commands** — "open" and "op" may conflict

### Conditional Macros Best Practices
1. **Start simple** — One condition block, then add complexity
2. **Use meaningful actions** — Notifications help user understand what's happening
3. **Test IF/THEN first** — Before adding ELSE logic
4. **Document your logic** — Use notification messages to explain flow

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+0` | Start/Stop macro recording |
| `Ctrl+'` | Open/Close Macro Manager |
| `Alt+F4` | Close current window |
| `Ctrl+S` | Save macro (in Macro Manager) |
| `Ctrl+Del` | Delete selected macro (in Macro Manager) |

---

## File Structure

```
AssistSense/
├── main.py                          # Entry point
├── config.py                        # Configuration
├── requirements.txt                 # Dependencies
├── README.md                        # Original README
├── README_COMPLETE_GUIDE.md        # This file
│
├── app/
│   ├── __init__.py
│   ├── controller.py                # Central coordinator
│   ├── gui.py                       # Main GUI window
│   ├── macro_manager_gui.py         # Macro editor GUI
│   ├── trigger_dialog.py            # Trigger config dialog
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
│
├── macros/
│   ├── __init__.py
│   ├── datamodel.py                 # Data structures
│   ├── interfaces.py                # Abstract interfaces
│   ├── macro_json_manager.py        # JSON persistence
│   ├── player.py                    # Playback engine
│   ├── recorder.py                  # Recording service
│   └── trigger.py                   # Trigger matching & execution
│
├── voiceRecog/
│   ├── __init__.py
│   ├── voiceRecog.py               # Voice listener
│   └── test_voice_listener.py      # Voice listener tests
│
├── Macros_json/                     # Macro storage
│   ├── test_unconditional.json
│   ├── test_if_battery_low.json
│   ├── test_if_voice_then_click.json
│   └── backup_20251207_120000/     # Backup folder
│
├── assets/
│   └── svg/
│
└── .venv/                          # Python virtual environment
```

---

## Glossary

- **Macro** — Recorded or pre-defined sequence of actions that can be replayed
- **Trigger** — Event that causes a macro to execute (voice, hotkey, gesture, etc.)
- **Voice Command** — Spoken phrase that triggers a macro
- **Action** — Single task performed by macro (move mouse, click, type, etc.)
- **Conditional** — If/then/else logic that changes macro behavior based on conditions
- **Normalized Coordinates** — Mouse positions as percentages (0.0-1.0) rather than pixels, allowing macros to work across different screen resolutions
- **Wake Word** — Phrase that activates voice listening (default: "listen")
- **Playback** — Executing/replaying a macro's recorded actions

---

## Support & Contribution

For bugs, feature requests, or contributions:
1. Check existing issues in the repository
2. Create detailed bug report with:
   - OS version
   - Python version
   - Steps to reproduce
   - Console error output
3. Submit pull request with improvements

---

## License & Attribution

**AssistSense** — Intelligent Macro System with Voice Control

Built with:
- PyQt6 for GUI
- speech_recognition for voice input
- pynput for input simulation
- mediapipe for gesture detection

---

**Last Updated:** December 7, 2025
**Version:** 1.0.0
