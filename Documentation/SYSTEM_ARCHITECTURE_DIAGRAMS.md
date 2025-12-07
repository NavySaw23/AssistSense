# AssistSense - Visual System Flows & Architecture Diagrams

## Table of Contents
1. [High-Level System Architecture](#high-level-system-architecture)
2. [Recording Flow](#recording-flow)
3. [Playback Flow](#playback-flow)
4. [Voice Command Flow](#voice-command-flow)
5. [GUI Navigation Flow](#gui-navigation-flow)
6. [Conditional Macro Execution](#conditional-macro-execution)
7. [Data Flow Diagram](#data-flow-diagram)

---

## High-Level System Architecture

### Main Components & Interactions

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ASSISTSENSE SYSTEM                          │
│                        (main.py - Entry Point)                      │
└────────────────────────┬────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌─────────┐    ┌──────────┐    ┌──────────────┐
    │ Hotkey  │    │ Voice    │    │ GUI Windows  │
    │Handler  │    │Listener  │    │(PyQt6)       │
    └────┬────┘    └────┬─────┘    └──────┬───────┘
         │              │                  │
         └──────────────┼──────────────────┘
                        │
                        ▼
            ╔═══════════════════════════╗
            ║      CONTROLLER           ║
            ║   (Central Orchestrator)  ║
            ╚═════════┬═════════════════╝
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
    ┌─────────┐  ┌─────────┐  ┌──────────────────┐
    │Recorder │  │ Trigger │  │ Macro Manager    │
    │Service  │  │ Service │  │ GUI              │
    └────┬────┘  └────┬────┘  └──────┬───────────┘
         │            │              │
         │            ▼              │
         │      ┌──────────┐        │
         │      │ Voice    │        │
         │      │Trigger   │        │
         │      │  Map     │        │
         │      └────┬─────┘        │
         │           │              │
         ▼           ▼              ▼
    ┌────────────────────────────────────────┐
    │     MacroJsonManager                   │
    │   (Load/Save/Update Macros)            │
    └──────────────┬──────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Macros_json/        │
        │  (JSON File Storage) │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────────┐
        │  MacroPlayer             │
        │  (Execute Actions)       │
        └──────────┬───────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
┌─────────┐  ┌──────────┐  ┌──────────────┐
│ Mouse/  │  │Keyboard  │  │ System Events│
│Keyboard │  │ Input    │  │(Notification)│
│Events   │  │Emulation │  │(App Launch)  │
└─────────┘  └──────────┘  └──────────────┘
```

---

## Recording Flow

### Step-by-Step: Recording a Macro via Hotkey

```
User presses Ctrl+Shift+0
        │
        ▼
┌─────────────────────────────┐
│ Controller.toggle_recording()│
│ ACTION: Start Recording     │
└────────┬────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ MacroRecorderService.start()     │
├──────────────────────────────────┤
│ • Initialize listeners:          │
│   - Mouse listener              │
│   - Keyboard listener           │
│ • Reset action list             │
│ • Start timestamp               │
│ • Set recording = True          │
└────────┬─────────────────────────┘
         │
         ▼
    [USER PERFORMS ACTIONS]
    ├─ Moves mouse  → Captured with timing
    ├─ Clicks       → Button + position logged
    ├─ Types text   → Keyboard input logged
    └─ Presses keys → Special keys captured
         │
         ▼
┌─────────────────────────────┐
│ Actions stored with timing: │
├─────────────────────────────┤
│ {dt: 250, type: mouse_move, │
│  x: 100, y: 150}            │
│ {dt: 50, type: mouse_click, │
│  button: left, x: 100, y:150}│
│ {dt: 100, type: keyboard_   │
│  text, text: "Hello"}       │
└────────┬────────────────────┘
         │
  User presses Ctrl+Shift+0
         │
         ▼
┌──────────────────────────────┐
│ Controller.toggle_recording()│
│ ACTION: Stop Recording      │
└────────┬─────────────────────┘
         │
         ▼
┌───────────────────────────────────┐
│ Show TriggerConfigDialog          │
├───────────────────────────────────┤
│ "Configure Trigger"               │
│ Trigger Type: [voice ▼]          │
│ Trigger Value: [_________]        │
│ Button: [Create Macro]            │
└────────┬──────────────────────────┘
         │
         ▼
┌───────────────────────────────────┐
│ Controller.finalize_macro()       │
├───────────────────────────────────┤
│ • Set trigger (voice/hotkey/...)  │
│ • Normalize mouse coordinates     │
│ • Generate macro name (timestamp) │
│ • Save to JSON via MacroJsonMgr   │
└────────┬──────────────────────────┘
         │
         ▼
┌───────────────────────────────────┐
│ MacroJsonManager.save_macro()     │
├───────────────────────────────────┤
│ Generate JSON:                    │
│ {                                 │
│   "name": "macro_20251207_120000",│
│   "trigger": {type, value},       │
│   "actions": [...],               │
│   "created": "timestamp"          │
│ }                                 │
└────────┬──────────────────────────┘
         │
         ▼
┌───────────────────────────────────┐
│ Write to Macros_json/[name].json  │
└────────┬──────────────────────────┘
         │
         ▼
┌───────────────────────────────────┐
│ trigger_service._load_triggers()  │
├───────────────────────────────────┤
│ Reload voice_trigger_map:         │
│ {                                 │
│  "voice_command": "macro_name",   │
│  ...                              │
│ }                                 │
│ Macro now available!              │
└───────────────────────────────────┘
         │
         ▼
    ✓ RECORDING COMPLETE
    Macro ready to use!
```

---

## Playback Flow

### Execution: Playing Back a Macro

```
TRIGGER EVENT (any of):
├─ Voice command matches
├─ Hotkey pressed
├─ Gesture detected
├─ Gaze direction
└─ Battery threshold
         │
         ▼
┌─────────────────────────────────┐
│ MacroTriggerService.on_         │
│ voice_command(text)             │
├─────────────────────────────────┤
│ • Receive voice text            │
│ • Lookup in voice_trigger_map   │
│ • Find macro name               │
└────────┬────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ if text in voice_trigger_map:      │
│   macro_name = map[text]           │
│   → Found!                         │
│ else:                              │
│   → No match, ignore              │
└────────┬─────────────────────────┘
         │
         ▼
┌───────────────────────────────────┐
│ MacroPlayer.play(macro_name)      │
├───────────────────────────────────┤
│ 1. Load macro from JSON           │
│ 2. Check if condition_blocks or   │
│    simple actions                 │
└────────┬──────────────────────────┘
         │
         ▼
    [EXECUTE ACTIONS SEQUENTIALLY]
         │
    ┌────┴────┐
    │          │
    ▼          ▼
 Action   Next Action
 {       {
  type:    type: ...,
  ...      dt: ...,
  dt: X    ...
 }       }
    │          │
    └─────┬────┘
          │
          ▼
    ┌──────────────────┐
    │ Calculate delays │
    │ between actions  │
    └────────┬─────────┘
             │
             ▼
    ┌────────────────────────────┐
    │ Execute each action:       │
    ├────────────────────────────┤
    │                            │
    │ If mouse_move:             │
    │ ├─ Normalize coordinates   │
    │ ├─ Get current screen size │
    │ ├─ Calculate actual pixels │
    │ ├─ Move mouse              │
    │ └─ Sleep(dt) milliseconds  │
    │                            │
    │ If mouse_click:            │
    │ ├─ Move to X, Y            │
    │ ├─ Press button            │
    │ ├─ Release button          │
    │ └─ Sleep(dt) milliseconds  │
    │                            │
    │ If keyboard_text:          │
    │ ├─ Type each character     │
    │ ├─ Respect keyboard layout │
    │ └─ Sleep(dt) milliseconds  │
    │                            │
    │ If keyboard_key:           │
    │ ├─ Press key (e.g., Enter) │
    │ ├─ Release key             │
    │ └─ Sleep(dt) milliseconds  │
    │                            │
    │ If notification:           │
    │ └─ Show Windows notification│
    │                            │
    │ If open_application:       │
    │ └─ subprocess.run(app_path)│
    │                            │
    └────────┬─────────────────┘
             │
             ▼
         [REPEAT]
        For each action
             │
             ▼
    ✓ PLAYBACK COMPLETE
```

---

## Voice Command Flow

### From Speech to Macro Execution

```
┌──────────────────────────────┐
│ Microphone Audio Input       │
│ (Continuous)                 │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ VoiceListener (Passive Mode) │
├──────────────────────────────┤
│ • Audio threshold detection  │
│ • Energy level analysis      │
│ • Listen for speech pattern  │
└────────┬─────────────────────┘
         │
         ▼
    Silence detected?
         │
    ┌────┴────┐
    │ NO      │ YES
    │ Keep    │ Continue
    │ listening
    │         │
    ▼         ▼
[Wait] ┌──────────────────────┐
       │ Recognize Speech     │
       ├──────────────────────┤
       │ Use:                 │
       │ • Google API (online)│
       │ • Whisper (offline)  │
       │ Requires internet or │
       │ offline model loaded │
       └────────┬─────────────┘
                │
                ▼
    ┌───────────────────────┐
    │ Convert to Text       │
    │ (confidence score)    │
    │ e.g., "open notepad"  │
    │ (0.95 confidence)     │
    └────────┬──────────────┘
             │
             ▼
    ┌─────────────────────────┐
    │ Filter by confidence    │
    ├─────────────────────────┤
    │ If confidence > 0.7:    │
    │   → Send to trigger     │
    │ Else:                   │
    │   → Ignore, continue    │
    │     listening           │
    └────────┬────────────────┘
             │
             ▼
┌────────────────────────────────┐
│ MacroTriggerService            │
│ .on_voice_command(text)        │
├────────────────────────────────┤
│ • Lookup text in               │
│   voice_trigger_map            │
│ • Compare exact match           │
└────────┬─────────────────────┘
         │
    ┌────┴────────────┐
    │                 │
    ▼                 ▼
 MATCH           NO MATCH
 Found           Continue
 │               listening
 │
 ▼
┌──────────────────────┐
│ Load Macro JSON      │
│ Get macro details    │
│ (check if            │
│  condition_blocks or │
│  simple actions)     │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│ MacroPlayer.play()   │
└────────┬─────────────┘
         │
         ▼
    Execute all actions
    in sequence
         │
         ▼
    ✓ COMPLETE
```

---

## GUI Navigation Flow

### Macro Manager UI Navigation

```
┌──────────────────────────────────────────┐
│ Press Ctrl+' (Macro Manager Opens)       │
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│        MACRO MANAGER WINDOW              │
├──────────────────────────────────────────┤
│                                          │
│ LEFT PANEL          │  RIGHT PANEL       │
│ (Macros List)       │  (Editor)          │
│                     │                    │
│ [Macro 1]           │  ┌──────────────┐ │
│ [Macro 2]  ◄────────┼─►│ Tabs:        │ │
│ [Macro 3]           │  ├──────────────┤ │
│            ▲        │  │ Trigger      │ │
│ [+Create]  │        │  │ Actions      │ │
│            │        │  │ Conditionals │ │
│            └────────┼─►│              │ │
│                     │  └──────────────┘ │
└──────────────────────────────────────────┘

FLOW 1: Edit Existing Macro
├─ Click macro in list
├─ Macro loaded on right
├─ Go to "Trigger" tab
│  └─ Set trigger type/value
├─ Go to "Actions" tab
│  ├─ Click "Add Action"
│  ├─ Select action type
│  ├─ Configure parameters
│  └─ Click OK
├─ Go to "Conditionals" tab
│  ├─ Click "+ Add If/Else Block"
│  ├─ Configure IF condition
│  ├─ Click "Add Action to THEN"
│  ├─ Click "Add Action to ELSE"
│  └─ Configure actions
├─ Click "Save Macro"
└─ Success!

FLOW 2: Create New Macro
├─ Click "Create New Macro"
├─ "NewMacroPanel" appears
├─ Enter macro name
├─ Go to "Trigger" tab
│  └─ Set trigger type/value
├─ Go to "Actions" tab
│  ├─ Click "Add Action"
│  └─ Configure actions
├─ Click "Create Macro"
└─ Macro list refreshes

FLOW 3: Delete Macro
├─ Click macro in list
├─ Click "Delete Macro" button
├─ Confirm deletion dialog
└─ Macro removed from list & file

FLOW 4: Close Manager
├─ Click X button or Alt+F4
├─ closeEvent() triggered
└─ Macro Manager window closed
```

---

## Conditional Macro Execution

### If/Then/Else Logic Flow

```
CONDITIONAL MACRO STRUCTURE:
┌──────────────────────────────────────────┐
│ condition_blocks: [                      │
│   {                                      │
│     "if": { condition object },          │
│     "then": [ actions to run if true ],  │
│     "else": [ actions if false ]         │
│   },                                     │
│   { next block... }                      │
│ ]                                        │
└──────────────────────────────────────────┘

EXECUTION:
┌──────────────────────────────┐
│ Macro Triggered              │
│ (voice, hotkey, etc.)        │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Load macro JSON              │
│ Check for condition_blocks   │
└────────┬─────────────────────┘
         │
    IF condition_blocks exists:
         │
         ▼
┌──────────────────────────────┐
│ For each block in blocks:    │
└────────┬─────────────────────┘
         │
         ▼
┌────────────────────────────┐
│ Evaluate IF condition      │
├────────────────────────────┤
│ Condition types:           │
│ • true → Always execute    │
│ • voice_match → Check text │
│ • battery → Check level    │
│ • custom → Custom logic    │
└────────┬───────────────────┘
         │
    ┌────┴────────┐
    │             │
    ▼             ▼
 CONDITION    CONDITION
 TRUE         FALSE
 │            │
 ▼            ▼
Execute    Execute
THEN       ELSE
actions    actions
 │            │
 └────┬───────┘
      │
      ▼
Execute next
block or
FINISH

EXAMPLE EXECUTION TRACE:
┌─────────────────────────────────────────────┐
│ Macro: "battery_status"                     │
│ Trigger: voice "battery status"             │
│ Condition Blocks: [1 block]                 │
├─────────────────────────────────────────────┤
│                                             │
│ Block 1:                                    │
│ IF: { type: "battery", value: "20", ... }  │
│                                             │
│ Evaluate: Is battery < 20%?                 │
│ → Check actual battery level                │
│ → System battery: 18%                       │
│ → YES, condition is true!                   │
│                                             │
│ Execute THEN block:                         │
│ ├─ Notification: "Battery Low!"             │
│ ├─ Open Calculator app                      │
│ └─ All THEN actions complete                │
│                                             │
│ Skip ELSE block (condition was true)        │
│                                             │
│ ✓ MACRO COMPLETE                            │
└─────────────────────────────────────────────┘

vs.

┌─────────────────────────────────────────────┐
│ Same macro, but battery is 75%              │
├─────────────────────────────────────────────┤
│                                             │
│ Block 1:                                    │
│ IF: { type: "battery", ... }                │
│                                             │
│ Evaluate: Is battery < 20%?                 │
│ → System battery: 75%                       │
│ → NO, condition is false!                   │
│                                             │
│ Skip THEN block (condition was false)       │
│                                             │
│ Execute ELSE block:                         │
│ ├─ Notification: "Battery is Good"          │
│ └─ All ELSE actions complete                │
│                                             │
│ ✓ MACRO COMPLETE                            │
└─────────────────────────────────────────────┘
```

---

## Data Flow Diagram

### Complete Data Journey

```
INPUT DEVICES              PROCESSING                OUTPUT
───────────────            ──────────                ──────

Microphone       ──►  VoiceListener    ──►  Text
 (Audio)              (recognition)         (Recognized)
                                               │
                                               ▼
Mouse/Keyboard  ──►  Recorder Service ──►  Action Data
 Input              (capture timing)         (JSON-ready)
                                               │
                                    ┌──────────┴──────────┐
                                    │                    │
                                    ▼                    ▼
                          MacroJsonManager          Voice Trigger
                         (serialize/persist)        Service
                                    │                    │
                                    ▼                    ▼
                          Macros_json/              Trigger Map
                         (JSON files)             {cmd → macro}
                                    │                    │
                                    └──────────┬─────────┘
                                               │
                                               ▼
                                          MacroPlayer
                                       (execute actions)
                                               │
    ┌──────────────────┬───────────────────────┼───────────┐
    │                  │                       │           │
    ▼                  ▼                       ▼           ▼
Mouse/Keyboard  Notification      System Events    Applications
Simulation      System Popup      (battery, etc.)  (Launched)
    │                  │                       │           │
    └──────────────────┴───────────────────────┴───────────┘
                       │
                       ▼
                   USER EXPERIENCE
```

---

## Threading & Concurrency Model

### How AssistSense Handles Multiple Operations

```
┌──────────────────────────────────────────────┐
│    MAIN THREAD (Qt Event Loop)               │
│                                              │
│ Responsible for:                            │
│ • GUI rendering                             │
│ • User input handling                       │
│ • Qt signals/slots                          │
│                                              │
│ ┌────────────────────────────────────────┐  │
│ │ GUI Windows (PyQt6)                    │  │
│ │ • Main App Window                      │  │
│ │ • Macro Manager                        │  │
│ │ • Dialogs                              │  │
│ └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
        │         ▲
        │         │ (Qt Signals)
        │         │
        ├─────────┼─────────┐
        │         │         │
        ▼         │         ▼
┌─────────────┐   │  ┌──────────────────┐
│ Hotkey Thrd │   │  │ Voice Listener   │
│ (pynput)    │   │  │ Thrd (background)│
│             │   │  │                  │
│ • Register  │   │  │ • Capture audio  │
│   hotkeys   │   │  │ • Recognize      │
│ • Listen    │   │  │   speech         │
│   for press │   │  │ • Buffer text    │
│ • Emit      │   │  │ • Emit signals   │
│   signal to │   │  └──────────────────┘
│   controller│   │
└─────────────┘   │  ┌──────────────────┐
                  │  │VoiceCommandWorker│
                  │  │(QThread)         │
                  │  │                  │
                  │  │ • Poll for text  │
                  │  │ • Emit to main   │
                  │  │   thread         │
                  │  └──────────────────┘
                  │
                  └─→ Main Thread
                       (safe GUI update)

DATA FLOW:
Microphone Audio
    ↓
Background Thread (VoiceListener)
    ├─ Process audio
    ├─ Recognize speech
    └─ Buffer text
    ↓
Background Thread (VoiceCommandWorker - QThread)
    ├─ Poll for text
    └─ Emit Qt Signal
    ↓
Main Thread (Qt Event Loop)
    ├─ Receive signal
    ├─ Route to controller
    ├─ Update GUI if needed
    └─ No blocking!
```

---

## File Organization & Data Structure

### JSON Schema: Simple Macro

```json
{
  "name": "macro_name",
  "created": "2025-12-07T12:00:00",
  "trigger": {
    "type": "voice|hotkey|gesture|gaze|battery",
    "value": "trigger_value_string"
  },
  "actions": [
    {
      "type": "mouse_move|mouse_click|keyboard_text|keyboard_key",
      "dt": 50,
      "x": 100,
      "y": 200,
      "button": "left",
      "text": "Hello",
      "key": "return"
    }
  ],
  "loop": false,
  "loop_interval": 1000
}
```

### JSON Schema: Structured Conditional Macro

```json
{
  "name": "conditional_macro",
  "created": "2025-12-07T12:00:00",
  "trigger": {
    "type": "voice",
    "value": "smart action"
  },
  "condition_blocks": [
    {
      "if": {
        "type": "battery|voice_match|true|custom",
        "value": "20",
        "op": "<|>|=="
      },
      "then": [
        { "type": "notification", "message": "Condition true" },
        { "type": "mouse_click", "x": 500, "y": 300 }
      ],
      "else": [
        { "type": "notification", "message": "Condition false" }
      ]
    }
  ],
  "loop": false
}
```

---

## State Management

### Macro States During Lifecycle

```
┌─────────┐
│ Created │  (JSON file written)
└────┬────┘
     │
     ▼
┌──────────┐
│ Loaded   │  (Trigger service loads on startup)
└────┬─────┘
     │
     ├─→ Voice Listener Active (waiting for command)
     │
     ├─→ Trigger Match (user speaks/presses trigger)
     │
     ├─→ Execution (MacroPlayer runs actions)
     │
     └─→ Ready (awaiting next trigger)


Controller States:
┌────────────────────────┐
│ is_recording: bool     │
│ • True: Capturing      │
│ • False: Idle          │
└────────────────────────┘

VoiceListener States:
┌────────────────────────┐
│ listening: bool        │
│ • True: Active         │
│ • False: Inactive      │
│                        │
│ force_active_mode: bool│
│ • True: Stay active    │
│   during playback      │
│ • False: Sleep during  │
│   playback             │
└────────────────────────┘
```

---

**End of Visual Diagrams Document**

Last Updated: December 7, 2025
