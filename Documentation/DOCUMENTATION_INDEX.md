# AssistSense Documentation Index

Welcome to AssistSense! This folder contains complete documentation to help you understand and use the system.

## 📚 Documentation Files

### 1. **README_COMPLETE_GUIDE.md** (START HERE for Comprehensive Info)
**~1500 lines | ~25 min read**

Complete user and developer guide covering:
- ✅ System overview and components
- ✅ Installation & setup (step-by-step)
- ✅ Quick start guide
- ✅ All features explained
- ✅ Macro system details
- ✅ Voice commands guide
- ✅ Advanced conditional macros
- ✅ Troubleshooting section
- ✅ Tips & best practices
- ✅ File structure
- ✅ Glossary

**👉 Read this first if you want complete information**

---

### 2. **QUICK_REFERENCE.md** (START HERE for Quick Lookup)
**~500 lines | ~5 min read**

Quick reference card with:
- 🚀 30-second getting started
- ⌨️ Essential hotkeys (copy-paste ready)
- 🎯 What macros can do
- 📝 All three tabs explained simply
- 🔧 Action configuration quick guide
- 🎛️ Conditional macro examples
- 🎵 Voice commands reference
- 📁 File locations
- ❌ Troubleshooting quick fixes
- 💡 Pro tips
- 🚀 One-minute examples

**👉 Read this for fast answers and quick lookup**

---

### 3. **SYSTEM_ARCHITECTURE_DIAGRAMS.md** (START HERE to Understand How It Works)
**~800 lines | ~15 min read**

Visual diagrams and flows:
- 🏗️ High-level system architecture
- 🔄 Recording flow (step-by-step)
- ▶️ Playback flow (detailed)
- 🎤 Voice command flow
- 🖥️ GUI navigation flow
- 🎛️ Conditional macro execution
- 📊 Data flow diagram
- 🧵 Threading & concurrency model
- 📋 JSON schema examples

**👉 Read this to understand system internals and data flows**

---

### 4. **README.md** (Original Project README)
Original project documentation with implementation guidelines.

---

## 🎯 Quick Navigation

**I'm new, where do I start?**
→ Read **QUICK_REFERENCE.md** (5 min), then **README_COMPLETE_GUIDE.md** (detailed)

**I just need to know how to use it**
→ Read **QUICK_REFERENCE.md** (5 min)

**I need to understand how it works internally**
→ Read **SYSTEM_ARCHITECTURE_DIAGRAMS.md** (15 min)

**I need complete information**
→ Read all three in order:
1. QUICK_REFERENCE.md (overview)
2. README_COMPLETE_GUIDE.md (comprehensive)
3. SYSTEM_ARCHITECTURE_DIAGRAMS.md (internals)

---

## 🚀 Fastest Start (2 Minutes)

```
1. Run:        .\.venv\Scripts\python.exe main.py
2. Press:      Ctrl+' (opens Macro Manager)
3. Click:      "Create New Macro"
4. Enter:      A name and voice command
5. Click:      "Save Macro"
6. Say:        Your voice command aloud
7. Done!       Macro executes
```

See **QUICK_REFERENCE.md** for more examples.

---

## 📋 Key Features Checklist

- ✅ Record macros with Ctrl+Shift+0
- ✅ Manage macros with visual GUI (Ctrl+')
- ✅ Voice-triggered actions
- ✅ Mouse/keyboard automation
- ✅ Conditional if/then/else logic
- ✅ Notifications and app launching
- ✅ JSON-based macro storage
- ✅ Cross-screen coordinate normalization

---

## 🔧 Common Tasks

### Record a Macro
→ See **QUICK_REFERENCE.md** section "Recording a Macro"

### Create a Conditional Macro
→ See **README_COMPLETE_GUIDE.md** section "Advanced: Conditional Macros"

### Add a Voice Command
→ See **QUICK_REFERENCE.md** section "Voice Commands Reference"

### Fix an Issue
→ See **README_COMPLETE_GUIDE.md** section "Troubleshooting" or **QUICK_REFERENCE.md** "Troubleshooting"

### Understand the System
→ See **SYSTEM_ARCHITECTURE_DIAGRAMS.md**

---

## 💻 System Requirements

- Windows OS
- Python 3.8+
- Microphone
- ~500MB disk space
- Internet (for voice recognition API, or offline Whisper model)

---

## 📁 Project Structure

```
AssistSense/
├── main.py                              # Run this to start
├── README.md                            # Original docs
├── README_COMPLETE_GUIDE.md             # Full guide ⭐
├── QUICK_REFERENCE.md                   # Quick lookup ⭐
├── SYSTEM_ARCHITECTURE_DIAGRAMS.md      # System flows ⭐
├── DOCUMENTATION_INDEX.md               # You are here
├── requirements.txt                     # Dependencies
│
├── app/
│   ├── controller.py                    # Central hub
│   ├── gui.py                          # Main window
│   ├── macro_manager_gui.py            # Macro editor
│   └── trigger_dialog.py               # Trigger config
│
├── macros/
│   ├── recorder.py                     # Record actions
│   ├── player.py                       # Play actions
│   ├── trigger.py                      # Match triggers
│   ├── macro_json_manager.py          # Save/load JSON
│   └── datamodel.py                    # Data structures
│
├── voiceRecog/
│   └── voiceRecog.py                  # Voice listener
│
├── Macros_json/                        # Macro storage
│   ├── test_unconditional.json
│   ├── test_if_battery_low.json
│   ├── test_if_voice_then_click.json
│   └── backup_20251207_120000/        # Old macros
│
└── assets/
    └── svg/
```

---

## 🎓 Learning Path

### Beginner (30 min)
1. Read: QUICK_REFERENCE.md
2. Do: Record a simple macro (Ctrl+Shift+0)
3. Test: Say voice command to trigger it
4. Try: Create a macro manually in GUI (Ctrl+')

### Intermediate (2 hours)
1. Read: README_COMPLETE_GUIDE.md
2. Do: Create 3-4 different macro types (voice, hotkey, etc.)
3. Try: Add different action types (click, type, notification)
4. Learn: Edit and delete macros
5. Explore: Save/load macro JSON files

### Advanced (4+ hours)
1. Read: SYSTEM_ARCHITECTURE_DIAGRAMS.md
2. Do: Create conditional macros with if/else
3. Try: Complex multi-action macros
4. Explore: JSON file structure
5. Experiment: Modify action timing and parameters

---

## 🆘 Need Help?

### Common Questions

**Q: How do I record a macro?**
A: Press Ctrl+Shift+0, perform actions, press Ctrl+Shift+0 again.
See QUICK_REFERENCE.md "Recording a Macro"

**Q: How do I make voice commands work?**
A: Create macro with "voice" trigger type, then say that exact phrase.
See QUICK_REFERENCE.md "Voice Commands Reference"

**Q: What's an if/else conditional?**
A: It lets macros check conditions and execute different actions.
See README_COMPLETE_GUIDE.md "Advanced: Conditional Macros"

**Q: Where are my macros saved?**
A: In Macros_json/ folder as JSON files.
See QUICK_REFERENCE.md "File Locations"

**Q: My macro doesn't work. Help!**
A: See README_COMPLETE_GUIDE.md "Troubleshooting" section.
Or see QUICK_REFERENCE.md "Troubleshooting" for quick fixes.

### No Answer Here?

1. Check **README_COMPLETE_GUIDE.md** → Troubleshooting section
2. Check console output for error messages
3. Review **SYSTEM_ARCHITECTURE_DIAGRAMS.md** to understand flows
4. Try re-recording the macro

---

## 📊 Documentation Stats

| Document | Lines | Read Time | Best For |
|----------|-------|-----------|----------|
| QUICK_REFERENCE.md | ~500 | 5 min | Quick answers |
| README_COMPLETE_GUIDE.md | ~1500 | 25 min | Complete info |
| SYSTEM_ARCHITECTURE_DIAGRAMS.md | ~800 | 15 min | Understanding internals |
| This file | ~300 | 5 min | Navigation |

**Total: ~3100 lines of documentation**

---

## ✨ What's Included

### Features Documented
- ✅ Recording macros
- ✅ Creating macros manually
- ✅ Voice commands
- ✅ Conditional logic (if/else)
- ✅ All action types
- ✅ Macro management (edit/delete)
- ✅ GUI navigation
- ✅ Troubleshooting
- ✅ System architecture
- ✅ Data flows
- ✅ Threading model

### Examples Provided
- ✅ 10+ macro examples
- ✅ Step-by-step tutorials
- ✅ Visual diagrams
- ✅ Code flows
- ✅ Conditional examples
- ✅ Keyboard shortcuts
- ✅ Troubleshooting scenarios

---

## 🎉 You're Ready!

You now have everything needed to:
1. ✅ Install and run AssistSense
2. ✅ Create and manage macros
3. ✅ Use voice commands
4. ✅ Build conditional macros
5. ✅ Troubleshoot issues
6. ✅ Understand system internals

**Pick a document above and start reading!**

---

**Last Updated:** December 7, 2025
**Version:** 1.0.0
**Project:** AssistSense - Intelligent Macro System with Voice Control
