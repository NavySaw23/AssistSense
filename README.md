# AssistSense
A PC automation manager that utilizes hand gestures, gaze detection and voice commands to execute macros

## Latest Updates (Battery Trigger Implementation)

### What's New

✅ **Battery Trigger System** - Complete operator-based battery level monitoring:
- Real-time battery level checking every 30 seconds
- Support for all comparison operators: `<`, `<=`, `>`, `>=`, `==`, `!=`
- Examples: `< 20%`, `<= 30%`, `>= 80%`, `== 50%`
- Automatic macro execution when battery level matches trigger condition
- Use case: "If battery drops below 80%, show notification and play sound"

### Features

- **Trigger Types Supported**:
  - Voice commands (e.g., "open notepad")
  - Keyboard shortcuts (e.g., "ctrl+alt+a")
  - Battery level with operators (e.g., "< 80%")
  - Gaze detection ("looking" or "away")
  - Gesture recognition (hand position patterns)

- **Action Types**:
  - Mouse movements and clicks
  - Keyboard text/key input
  - Notifications
  - Application launch
  - Sound playback (with repeat count)

- **Conditional Execution**:
  - IF/THEN/ELSE blocks
  - Multiple ELIF chains
  - Inline action editing
  - Nested conditions support

### Installation

```bash
pip install -r requirements.txt
```

### Running

```bash
python main.py
```

### Documentation

- `Documentation/README_COMPLETE_GUIDE.md` - Full system guide with examples
- `Documentation/QUICK_REFERENCE.md` - Quick lookup for trigger types and actions
- `Documentation/SYSTEM_ARCHITECTURE_DIAGRAMS.md` - System flow diagrams

