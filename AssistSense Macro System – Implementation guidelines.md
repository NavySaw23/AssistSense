AssistSense Macro System – Implementation Gameplan

(Working doc: step by step how to add normalized, cross-device macros with multiple initiation types.)

I’ll break it into 7 chunks
architecture
data model
recording pipeline
playback pipeline
normalization and screen handling
initiation system (voice, gesture, etc)
safety and testing

1. Architecture: where this lives in AssistSense

Think in terms of three main services

1. MacroRecorderService
   Listens to global input
   Builds an in-memory list of events
   Serializes to JSON when recording stops

2. MacroPlayerService
   Loads JSON
   Converts normalized coords to actual screen coords
   Uses SendInput plus SetCursorPos to replay events with timing

3. MacroTriggerService
   Maps trigger events to macro files
   Trigger event can come from
   voice
   gesture
   shortcut
   anything
   Once triggered, calls MacroPlayerService.Play(macroName)

Project wise

1. Core
   Define interfaces
   IMacroRecorder
   IMacroPlayer
   IMacroTrigger

2. Modules
   MacroRecorderModule
   MacroPlayerModule
   MacroTriggerModule

3. Data
   Macros folder
   Each macro as a JSON file

2) Data model: how a macro is stored

You want something flexible but simple.

{
  "name": "youtube_mode",
  "version": 1,
  "createdAt": "2025-12-06T15:00:00Z",
  "screen": {
    "width": 1920,
    "height": 1080
  },
  "normalized": true,
  "trigger": {
    "type": "voice",
    "value": "youtube mode"
  },
  "actions": [
    {
      "dt": 0,
      "type": "mouse_move",
      "xNorm": 0.741,
      "yNorm": 0.472
    },
    {
      "dt": 60,
      "type": "mouse_click",
      "button": "left",
      "xNorm": 0.741,
      "yNorm": 0.472
    },
    {
      "dt": 300,
      "type": "keyboard_text",
      "text": "abc def"
    },
    {
      "dt": 120,
      "type": "keyboard_key",
      "key": "enter"
    }
  ]
}


Macro file JSON

```
{
  "name": "youtube_mode",
  "version": 1,
  "createdAt": "2025-12-06T15:00:00Z",
  "screen": {
    "width": 1920,
    "height": 1080
  },
  "normalized": true,
  "trigger": {
    "type": "voice",
    "value": "youtube mode"
  },
  "actions": [
    {
      "dt": 0,
      "type": "mouse_move",
      "xNorm": 0.741,
      "yNorm": 0.472
    },
    {
      "dt": 60,
      "type": "mouse_click",
      "button": "left",
      "xNorm": 0.741,
      "yNorm": 0.472
    },
    {
      "dt": 300,
      "type": "keyboard_text",
      "text": "abc def"
    },
    {
      "dt": 120,
      "type": "keyboard_key",
      "key": "enter"
    }
  ]
}
```

Rules

1. dt in milliseconds since previous action

2. Always store mouse positions as xNorm and yNorm in range 0 to 1

3. Also store original screen width and height at recording time for debugging and maybe future scaling strategies

4. For keyboard events, you can store either text or virtual key codes

3) Recording pipeline: from “start” to JSON

Components you need

1. GlobalInputHook
   Uses SetWindowsHookEx for
   WH_MOUSE_LL
   WH_KEYBOARD_LL
   Calls back into MacroRecorderService with low level events

2. MacroRecorderService
   Has an internal list of RecordedAction
   Has state
   IsRecording
   LastEventTime

3. Recorder control
   Something that calls StartRecording and StopRecording
   Could be a hotkey, UI button, or even a voice command like “start recording macro”

Flow

1. StartRecording(name, triggerInfo)
   Clear list
   Set IsRecording true
   Set LastEventTime = now
   Capture current screen resolution Screen.PrimaryScreen.Bounds

2. On mouse event from hook
   If not IsRecording then ignore
   Get absolute screen coordinates with GetCursorPos
   Normalize
   xNorm = x / screenWidth
   yNorm = y / screenHeight
   Compute dt = now − LastEventTime
   LastEventTime = now
   Depending on event
   mouse move
   mouse button down
   mouse button up
   mouse wheel
   build a RecordedAction and add to list

3. On keyboard event from hook
   Same dt logic
   For text, you can either
   treat each key press as a separate action
   or buffer into keyboard_text events
   Start simple: record per key as keyDown and keyUp

4. StopRecording
   Set IsRecording false
   Create a Macro object
   fill meta info
   name
   screen size
   trigger info
   actions list
   Serialize to JSON
   Save as Macros/name.json

Important detail for normalized coords

1. Always use the same reference
   For now, use primary monitor full resolution

2. Do not record dx dy at all
   Only absolute cursor position normalized

4) Playback pipeline: how to simulate the macro

Components

1. MacroPlayerService

Public API
Play(string macroName)
Play(Macro macro)

Steps

1. Load Macro
   Read JSON Macros/macroName.json
   Deserialize

2. Resolve screen resolution
   Get current screen width and height
   If you want to still support original resolution, you can compare
   but simplest version
   x = macro.actions[i].xNorm * currentWidth
   y = macro.actions[i].yNorm * currentHeight

3. Replay loop
   For each action in order
   If dt > 0 then await Task.Delay(dt) or Thread.Sleep(dt)
   Then
   if type == mouse_move
   SetCursorPos(x, y)
   if type == mouse_click
   SetCursorPos(x, y)
   SendInput mouse down
   SendInput mouse up
   if type == mouse_down or mouse_up separately
   do them individually
   if type == keyboard_key
   SendInput with KEYBDINPUT
   if type == keyboard_text
   loop through characters and synthesize key events

4. Cancel handling
   Allow a way to cancel playback, for example a global “panic key”
   MacroPlayerService keeps a token that can be set to cancel

Timing detail

Do not try to be super precise at first. dt with normal Sleep is fine.
Later you can refine with a high precision timer if needed.

5. Normalization strategy and screen handling

You already decided on normalized coords. Good.
Add these considerations

1. Basic rule
   recorded xNorm, yNorm always in 0 to 1
   on playback
   x = Math.Round(xNorm * currentWidth)
   y = Math.Round(yNorm * currentHeight)

2. Multi monitor
   Decide what you consider “screen space”
   simplest approach
   only support primary monitor for now
   or treat the full desktop bounds as one big rectangle

3. DPI scaling
   If you use GetCursorPos and SetCursorPos you are in physical pixel space
   which generally matches what you want
   so as long as you normalize correctly, macros should still work at different DPI

4. Possible future refinement
   Store the name of the foreground window for certain actions
   On playback, make sure the right app has focus
   But this is extra, not required for v1

6) Initiation system: mapping triggers to macros

You want the same macro to be callable by many possible initiation types.
So separate the idea of triggers from the macro file itself.

Design

1. Macro registry
   Keeps a mapping from trigger to macroName

   For example
   Voice:
   "youtube mode" → "youtube_mode"

   Shortcut
   "Ctrl+Alt+Y" → "youtube_mode"

   Gesture
   "GestureId_3" → "youtube_mode"

2. MacroTriggerService

Public API

1. RegisterTrigger(TriggerType type, string value, string macroName)
2. OnTrigger(TriggerType type, string value)

When a subsystem detects something

Voice subsystem
finishes STT and gets text
calls MacroTriggerService.OnTrigger(TriggerType.Voice, text)

Gesture subsystem
recognizes “swipe up then left” as an ID
calls MacroTriggerService.OnTrigger(TriggerType.Gesture, "SwipeUpLeft")

Keybind subsystem
detects hotkey
calls MacroTriggerService.OnTrigger(TriggerType.Shortcut, "Ctrl+Alt+Y")

Inside OnTrigger

1. Look up key (type, value) in dictionary
2. If macroName found
   call MacroPlayerService.Play(macroName)

Recording time linkage

When you stop recording a macro, let user set a trigger immediately
For example, you can store a default trigger inside the macro JSON
but the registry can override it.

7. Safety, edge cases, and testing

Safety

1. Panic key
   Define something like Ctrl+Alt+Esc that
   stops any ongoing playback
   disables recording if it is on

2. Block recursive triggering
   While playing a macro, do not record input
   or else you can create weird loops

3. Blacklist input while recording
   You might want a way to exclude certain actions
   like blocking Windows key or Alt+Tab from being recorded

Edge cases

1. User changes resolution between record and playback
   With normalized coords, this will mostly work fine, but some UI layouts may shift
2. Apps not in the same state
   You can mitigate by
   starting macros from a known baseline
   or including “open app” steps inside macro

Testing strategy

1. Start with a simple macro
   Record
   move to browser icon
   click it
   wait
   type “youtube.com”
   press enter

2. Change your mouse starting position
   Run macro
   check it still works

3. Change resolution
   test again

4. Try multiple macros and make sure they do not interfere
   and that the panic key always works
