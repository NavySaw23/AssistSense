# AssistSense Quick Reference Card

## 🚀 Getting Started (30 Seconds)

```
1. Run:    .\.venv\Scripts\python.exe main.py
2. Press:  Ctrl+' (Macro Manager opens)
3. Click:  "Create New Macro"
4. Say:    A voice command to trigger it
5. Click:  "Save Macro"
6. Test:   Say the voice command aloud
```

---

## ⌨️ Essential Hotkeys

| Key Combo | Action |
|-----------|--------|
| `Ctrl+Shift+0` | ▶ START/STOP recording macro |
| `Ctrl+'` | 📋 OPEN Macro Manager |
| `Alt+F4` | ❌ CLOSE window |

---

## 🎯 What Can Macros Do?

```
✓ Move mouse to position
✓ Click (left/right/middle button)
✓ Type text
✓ Press keyboard keys (Enter, Tab, Shift, etc.)
✓ Show notification popups
✓ Launch applications
✓ Execute with IF/THEN/ELSE logic
```

---

## 🎙️ Recording a Macro

```
HOTKEY METHOD (Fastest):
1. Press Ctrl+Shift+0 to START
2. Move mouse, click, type, press keys
3. Press Ctrl+Shift+0 to STOP
4. Choose trigger type (voice/hotkey/gesture/etc.)
5. DONE - Macro auto-saved

MANUAL METHOD (More Control):
1. Open Macro Manager (Ctrl+')
2. Click "Create New Macro"
3. Set Name & Trigger
4. Go to "Actions" tab
5. Click "Add Action" repeatedly
6. Configure each action
7. Click "Save Macro"
```

---

## 📝 Macro Manager Tabs Explained

### Trigger Tab
Sets what activates the macro.

```
Trigger Type Options:
├─ voice         → Say a phrase ("open notepad")
├─ keyboard_shortcut → Press keys ("ctrl+alt+a")
├─ gesture       → Hand gesture / finger pattern
├─ gaze          → Eye gaze ("looking" or "away")
└─ battery       → Battery level ("20" for <20%)
```

#### Gaze Trigger Quick Reference
```
"looking" → Triggers when user looks at screen
"away"    → Triggers when user looks away

Example: Pause video when user looks away
```

#### Gesture Trigger Quick Reference
```
10-finger array: [finger0, finger1, ..., finger9]
├─ Index 0-4: Left hand (pinky→thumb)
├─ Index 5-9: Right hand (thumb→pinky)
└─ Value: 0=closed, 1=open, -1=not detected

Examples:
├─ [1,1,1,1,1,-1,-1,-1,-1,-1] → Left hand all open
├─ [0,0,0,0,1,-1,-1,-1,-1,-1] → Left thumbs up
└─ [1,0,0,0,0,0,0,0,0,1] → Left pinky + right pinky (peace)
```

### Actions Tab
List of things the macro does (in order).

```
Available Actions:
├─ mouse_move     → Move cursor to X,Y
├─ mouse_click    → Click at X,Y (left/right/middle)
├─ keyboard_text  → Type text
├─ keyboard_key   → Press key (return, shift, etc.)
├─ notification   → Show popup message
└─ open_application → Launch app (notepad, calc, etc.)

USAGE:
1. Click "Add Action"
2. Pick action type
3. Fill in details
4. Click OK
5. Repeat to add more
```

### Conditionals Tab (IF/THEN/ELSE)
Advanced: Make macros smart with conditional logic.

```
Structure:
┌─ IF Condition ─────────────────────┐
│ Does this condition apply?         │
│ Options: true, voice_match,        │
│          battery, custom           │
└────────────────────────────────────┘
         │ YES → ↓
┌─ THEN Actions ─────────────────────┐
│ Execute these actions               │
│ [Add Action to THEN] button        │
└────────────────────────────────────┘

         │ NO → ↓
┌─ ELSE Actions (Optional) ──────────┐
│ Execute these fallback actions      │
│ [Add Action to ELSE] button        │
└────────────────────────────────────┘
```

---

## 🔧 Action Configuration Quick Guide

### Mouse Move
```
X: 500        (horizontal position)
Y: 300        (vertical position)
Delay: 50     (wait 50ms after moving)
```

### Mouse Click
```
X: 500        (click position X)
Y: 300        (click position Y)
Button: left  (or: right, middle)
Delay: 100    (wait after clicking)
```

### Type Text
```
Text: "Hello World"
Delay: 50     (wait after typing)
```

### Press Key
```
Key: "return"  (or: shift, ctrl, alt, tab, etc.)
Delay: 100
```

### Notification
```
Message: "Task Complete!"
(Appears as Windows notification)
```

### Open Application
```
App: [Dropdown selection]
Options: Notepad, Calculator, Paint, Word, Excel,
         PowerPoint, Chrome, Firefox, Edge, VSCode
         + Custom path option
```

---

## 🎛️ Conditional Macro Examples

### Example 1: Battery Check
```
Voice Trigger: "battery status"

IF: battery < 20%
  THEN: Show notification "Battery Low!"
  ELSE: Show notification "Battery OK"
```

### Example 2: Time-Based Actions
```
Voice Trigger: "morning routine"

IF: time > 9 AM
  THEN: Open Calculator
  ELSE: Show notification "Too early!"
```

### Example 3: Voice-Activated Menu
```
Voice Trigger: "show menu"

IF: voice matches "show menu"
  THEN: 
    1. Move mouse to (500, 300)
    2. Click (left)
    3. Type "Menu"
```

---

## 🎵 Voice Commands Reference

### How to Use
```
1. Speak the wake word (default: "listen")
2. Listen for recognition tone
3. Say your macro trigger phrase
4. Macro executes!

Default Test Macros:
- "test run"           → Move, click, type
- "battery test"       → Battery check conditional
- "start show"         → Voice match conditional
```

### Adding Custom Voice Command
```
1. Open Macro Manager (Ctrl+')
2. Create/Edit macro
3. Trigger Tab → Type voice command
4. Save macro
5. Say it exactly to trigger
```

---

## 📁 File Locations

```
AssistSense/
├─ main.py                          ← Run this!
├─ Macros_json/                     ← Macro files stored here
│  ├─ test_unconditional.json
│  ├─ test_if_battery_low.json
│  ├─ test_if_voice_then_click.json
│  └─ backup_20251207_120000/       ← Old macros backed up here
└─ .venv/                           ← Virtual environment
```

---

## ❌ Troubleshooting

| Problem | Solution |
|---------|----------|
| **"ModuleNotFoundError"** | Run: `pip install -r requirements.txt` |
| **Mic not working** | Check Windows Sound Settings, restart app |
| **Voice commands don't work** | Say exact phrase, use wake word first ("listen") |
| **Macro not playing** | Check coordinates fit screen, verify actions in tab |
| **Macro Manager is blank** | Close (Alt+F4), reopen with Ctrl+' |
| **Can't save changes** | Check Macros_json/ folder permissions |

---

## 💡 Pro Tips

✓ **Test immediately** after recording to verify it works
✓ **Use notifications** in conditionals so user knows what happened
✓ **Start simple** - record one macro first, add complexity later
✓ **Speak clearly** when using voice commands (near microphone)
✓ **Check console** for debug output if something fails
✓ **Use backups** - old macros saved in backup_TIMESTAMP/ folder

---

## 🔗 Keyboard Codes (For keyboard_key action)

```
Common Keys:
├─ return     (Enter)
├─ shift      (Shift)
├─ ctrl       (Control)
├─ alt        (Alt)
├─ tab        (Tab)
├─ space      (Spacebar)
├─ backspace  (Backspace)
├─ delete     (Delete)
├─ escape     (Escape)
└─ See Python pynput docs for full list
```

---

## 📊 Architecture Overview

```
User Input
    ↓
┌─ Hotkey (Ctrl+Shift+0) ──→ Recorder
├─ Voice Command ───────────→ Voice Listener → Trigger Service
└─ GUI (Ctrl+') ────────────→ Macro Manager
    ↓
Controller (Central Hub)
    ↓
┌─ Trigger Service ─→ Voice Command Matching
├─ Player ──────────→ Execute Actions Sequentially
└─ JSON Manager ────→ Save/Load Macros
    ↓
Output
├─ Mouse/Keyboard Simulation
├─ Notifications
├─ Application Launch
└─ Action Playback
```

---

## 🚀 One-Minute Examples

### Example 1: "Open Notepad and Type Hello"
```
1. Ctrl+' (Open Manager)
2. Create New Macro → name: "quick note"
3. Trigger: voice, value: "quick note"
4. Actions:
   • open_application → Notepad
   • keyboard_text → "Hello, World!"
5. Save
6. Say "quick note" → Done!
```

### Example 2: "Click and Type with IF"
```
1. Ctrl+' (Open Manager)
2. Create New Macro → name: "smart click"
3. Trigger: voice, value: "smart click"
4. Conditionals tab:
   • IF: true (unconditional)
   • THEN:
     - mouse_click at (500, 300)
     - keyboard_text "Data entered"
5. Save
6. Say "smart click" → Clicks then types
```

---

**Need more help?** See `README_COMPLETE_GUIDE.md` for full documentation.

**Last Updated:** December 7, 2025
