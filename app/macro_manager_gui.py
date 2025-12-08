"""
Macro Manager GUI for editing, creating, and managing action/trigger pairs.
"""
import json
import os
import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QScrollArea, QFrame, QGroupBox, QComboBox, QSpinBox,
    QDoubleSpinBox, QLineEdit, QCheckBox, QTabWidget, QDialog, QMessageBox,
    QTreeWidget, QTreeWidgetItem, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont
import shutil
import platform
try:
    import winsound
except Exception:
    winsound = None


class TriggerEditor(QWidget):
    """Editor for trigger conditions with proper config per type."""
    
    def __init__(self, trigger_data=None):
        super().__init__()
        self.trigger_data = trigger_data or {"type": "voice", "value": ""}
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Trigger type selector
        type_layout = QVBoxLayout()
        type_label = QLabel("Trigger Type:")
        self.trigger_type_combo = QComboBox()
        self.trigger_type_combo.addItems(["voice", "keyboard_shortcut", "gesture", "gaze", "battery"])
        self.trigger_type_combo.currentTextChanged.connect(self.on_trigger_type_changed)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.trigger_type_combo)
        layout.addLayout(type_layout)
        
        # Container for trigger-type-specific editors
        self.editor_container = QWidget()
        self.editor_layout = QVBoxLayout()
        self.editor_container.setLayout(self.editor_layout)
        layout.addWidget(self.editor_container)
        
        # Initialize editors
        self.voice_editor = VoiceEditor()
        self.keyboard_editor = KeyboardEditor()
        self.battery_editor = BatteryEditor()
        self.gaze_editor = GazeEditor()
        self.gesture_editor = GestureEditor()
        
        # Load current data
        if self.trigger_data:
            trigger_type = self.trigger_data.get("type", "voice")
            self.trigger_type_combo.setCurrentText(trigger_type)
            self._load_trigger_data(trigger_type)
            # Ensure the correct editor widget is shown for the current trigger type
            self.on_trigger_type_changed(trigger_type)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def _load_trigger_data(self, trigger_type):
        """Load trigger data into appropriate editor."""
        if trigger_type == "voice":
            self.voice_editor.set_value(self.trigger_data.get("value", ""))
        elif trigger_type == "keyboard_shortcut":
            self.keyboard_editor.set_value(self.trigger_data.get("value", ""))
        elif trigger_type == "battery":
            self.battery_editor.set_value(self.trigger_data.get("value", ""))
        elif trigger_type == "gaze":
            self.gaze_editor.set_value(self.trigger_data.get("value", ""))
        elif trigger_type == "gesture":
            self.gesture_editor.set_value(self.trigger_data.get("value", ""))
    
    def on_trigger_type_changed(self, new_type):
        """Switch active editor based on trigger type."""
        # Clear container without deleting the editor widgets (keep instances reusable)
        while self.editor_layout.count():
            item = self.editor_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
        
        # Add appropriate editor and ensure it's visible
        editor_to_show = None
        if new_type == "voice":
            editor_to_show = self.voice_editor
        elif new_type == "keyboard_shortcut":
            editor_to_show = self.keyboard_editor
        elif new_type == "battery":
            editor_to_show = self.battery_editor
        elif new_type == "gaze":
            editor_to_show = self.gaze_editor
        elif new_type == "gesture":
            editor_to_show = self.gesture_editor
        
        if editor_to_show:
            editor_to_show.setVisible(True)
            self.editor_layout.addWidget(editor_to_show)
    
    def get_trigger_data(self):
        """Return the current trigger configuration."""
        trigger_type = self.trigger_type_combo.currentText()
        
        if trigger_type == "voice":
            return {"type": trigger_type, "value": self.voice_editor.get_value()}
        elif trigger_type == "keyboard_shortcut":
            return {"type": trigger_type, "value": self.keyboard_editor.get_value()}
        elif trigger_type == "battery":
            return {"type": trigger_type, "value": self.battery_editor.get_value()}
        elif trigger_type == "gaze":
            return {"type": trigger_type, "value": self.gaze_editor.get_value()}
        elif trigger_type == "gesture":
            return {"type": trigger_type, "value": self.gesture_editor.get_value()}
        else:
            return {"type": trigger_type, "value": ""}


class VoiceEditor(QWidget):
    """Simple text editor for voice commands."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.input = QLineEdit()
        self.input.setPlaceholderText("e.g., 'open notepad', 'record macro'")
        layout.addWidget(QLabel("Voice Command:"))
        layout.addWidget(self.input)
        self.setLayout(layout)
    
    def set_value(self, value):
        self.input.setText(str(value))
    
    def get_value(self):
        return self.input.text()


class KeyboardEditor(QWidget):
    """Editor for keyboard shortcuts."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.input = QLineEdit()
        self.input.setPlaceholderText("e.g., 'ctrl+alt+a', 'shift+f5'")
        layout.addWidget(QLabel("Keyboard Shortcut:"))
        layout.addWidget(self.input)
        self.setLayout(layout)
    
    def set_value(self, value):
        self.input.setText(str(value))
    
    def get_value(self):
        return self.input.text()


class BatteryEditor(QWidget):
    """Editor for battery level triggers with operators."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(QLabel("Battery Level Condition:"))
        
        # Operator selector
        op_layout = QHBoxLayout()
        op_layout.addWidget(QLabel("Battery is"))
        self.operator = QComboBox()
        self.operator.addItems(["<", "<=", ">", ">=", "==", "!="])
        op_layout.addWidget(self.operator)
        
        # Value spinbox
        self.value_spin = QSpinBox()
        self.value_spin.setMinimum(0)
        self.value_spin.setMaximum(100)
        self.value_spin.setValue(50)
        self.value_spin.setSuffix("%")
        op_layout.addWidget(self.value_spin)
        op_layout.addStretch()
        layout.addLayout(op_layout)
        
        layout.addWidget(QLabel("Example: < 20% triggers when battery drops below 20%"))
        layout.addStretch()
        self.setLayout(layout)
    
    def set_value(self, value):
        """Parse stored value like '<20' or '<=30'."""
        if not value:
            return
        value_str = str(value)
        # Extract operator and number
        for op in ["<=", ">=", "==", "!=", "<", ">"]:
            if value_str.startswith(op):
                self.operator.setCurrentText(op)
                try:
                    num = int(value_str[len(op):].strip())
                    self.value_spin.setValue(num)
                except:
                    pass
                return
    
    def get_value(self):
        """Return value like '<20' or '<=30'."""
        return f"{self.operator.currentText()}{self.value_spin.value()}"


class GazeEditor(QWidget):
    """UI for configuring gaze trigger (looking/away)."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        
        info_label = QLabel(
            "👁️ Gaze Detection:\n"
            "• 'looking' - Triggers when user looks at screen\n"
            "• 'away' - Triggers when user looks away"
        )
        info_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(info_label)
        
        # Gaze value selector
        gaze_layout = QVBoxLayout()
        gaze_label = QLabel("Select Gaze State:")
        self.gaze_combo = QComboBox()
        self.gaze_combo.addItems(["looking", "away"])
        gaze_layout.addWidget(gaze_label)
        gaze_layout.addWidget(self.gaze_combo)
        layout.addLayout(gaze_layout)
        
        self.setLayout(layout)
    
    def set_value(self, value):
        """Set gaze value from trigger data."""
        if value in ["looking", "away"]:
            self.gaze_combo.setCurrentText(str(value))
    
    def get_value(self):
        """Get selected gaze value."""
        return self.gaze_combo.currentText()


class GestureEditor(QWidget):
    """UI for configuring gesture trigger (10-finger array)."""
    
    def __init__(self):
        super().__init__()
        self.finger_buttons = []
        self.finger_states = [0] * 10  # 0=closed, 1=open, -1=not detected
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        
        info_label = QLabel(
            "✋ Gesture Detection (10-finger array):\n"
            "• Left hand (0-4): Pinky, Ring, Middle, Index, Thumb\n"
            "• Right hand (5-9): Thumb, Index, Middle, Ring, Pinky\n"
            "• Click each finger: 0=closed, 1=open, -1=not detected"
        )
        info_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(info_label)
        
        # Finger selector buttons
        finger_labels = [
            "L-Pinky(0)", "L-Ring(1)", "L-Middle(2)", "L-Index(3)", "L-Thumb(4)",
            "R-Thumb(5)", "R-Index(6)", "R-Middle(7)", "R-Ring(8)", "R-Pinky(9)"
        ]
        
        fingers_layout = QVBoxLayout()
        
        # Left hand
        left_hand_layout = QVBoxLayout()
        left_hand_layout.addWidget(QLabel("LEFT HAND:"))
        left_row = QVBoxLayout()
        for i in range(5):
            btn = QPushButton(finger_labels[i])
            btn.setMaximumWidth(100)
            btn.setToolTip(f"Click to cycle: closed (0) → open (1) → not detected (-1)")
            btn.clicked.connect(lambda checked, idx=i: self.cycle_finger(idx))
            self.finger_buttons.append(btn)
            left_row.addWidget(btn)
        left_hand_layout.addLayout(left_row)
        fingers_layout.addLayout(left_hand_layout)
        
        # Right hand
        right_hand_layout = QVBoxLayout()
        right_hand_layout.addWidget(QLabel("RIGHT HAND:"))
        right_row = QVBoxLayout()
        for i in range(5, 10):
            btn = QPushButton(finger_labels[i])
            btn.setMaximumWidth(100)
            btn.setToolTip(f"Click to cycle: closed (0) → open (1) → not detected (-1)")
            btn.clicked.connect(lambda checked, idx=i: self.cycle_finger(idx))
            self.finger_buttons.append(btn)
            right_row.addWidget(btn)
        right_hand_layout.addLayout(right_row)
        fingers_layout.addLayout(right_hand_layout)
        
        layout.addLayout(fingers_layout)
        
        # Display current array
        self.array_display = QLineEdit()
        self.array_display.setReadOnly(True)
        self.array_display.setText(str(self.finger_states))
        layout.addWidget(QLabel("Current Pattern:"))
        layout.addWidget(self.array_display)
        
        self.setLayout(layout)
    
    def cycle_finger(self, index):
        """Cycle finger state: 0 → 1 → -1 → 0"""
        current = self.finger_states[index]
        if current == 0:
            self.finger_states[index] = 1
        elif current == 1:
            self.finger_states[index] = -1
        else:
            self.finger_states[index] = 0
        
        self.update_display()
    
    def update_display(self):
        """Update button colors and array display."""
        state_colors = {0: "#ffcccc", 1: "#ccffcc", -1: "#cccccc"}
        state_labels = {0: "CLOSED", 1: "OPEN", -1: "NOT_DETECTED"}
        
        for i, btn in enumerate(self.finger_buttons):
            state = self.finger_states[i]
            btn.setStyleSheet(f"background-color: {state_colors[state]};")
            btn.setText(btn.text().split("(")[0] + f"({i})\n{state_labels[state]}")
        
        self.array_display.setText(str(self.finger_states))
    
    def set_value(self, value):
        """Load gesture pattern from trigger data."""
        try:
            if isinstance(value, str):
                # Parse string like "[1,1,1,1,1,-1,-1,-1,-1,-1]"
                import ast
                parsed = ast.literal_eval(value)
                if isinstance(parsed, list) and len(parsed) == 10:
                    self.finger_states = parsed
            elif isinstance(value, list) and len(value) == 10:
                self.finger_states = value
            self.update_display()
        except:
            pass  # Keep default if parsing fails
    
    def get_value(self):
        """Get gesture pattern as array string."""
        return str(self.finger_states)



class ActionEditor(QWidget):
    """Editor for macro actions with collapsible action groups."""
    
    def __init__(self, actions_data=None):
        super().__init__()
        self.actions_data = actions_data or []
        self.action_widgets = []
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        # Action tree - grouped by action type
        self.action_tree = QTreeWidget()
        self.action_tree.setHeaderLabels(["Action Type", "Details"])
        self.action_tree.setColumnCount(2)
        self.action_tree.itemDoubleClicked.connect(self.on_item_double_clicked)

        layout.addWidget(QLabel("Actions (organized by type):"))
        layout.addWidget(self.action_tree)

        # Add action button
        add_action_btn = QPushButton("Add Action")
        add_action_btn.clicked.connect(self.add_action)
        layout.addWidget(add_action_btn)

        self.setLayout(layout)

        # Build initial tree from actions_data
        self.rebuild_tree()
    
    def get_action_details(self, action):
        """Get a readable string for an action."""
        action_type = action.get("type", "")
        if action_type == "mouse_click":
            return f"Click at ({action.get('x')}, {action.get('y')})"
        elif action_type == "mouse_move":
            return f"Move to ({action.get('x')}, {action.get('y')})"
        elif action_type == "keyboard_text":
            return f"Type: '{action.get('text')}'"
        elif action_type == "keyboard_key":
            return f"Press: {action.get('key')}"
        elif action_type == "notification":
            return f"Show: {action.get('message', 'notification')}"
        elif action_type == "open_application":
            return f"Open: {action.get('app_path', 'application')}"
        elif action_type == "sound":
            return f"Sound: {action.get('path', '')} x{action.get('repeat',1)}"
        return str(action)
    
    def add_action(self):
        """Add a new action."""
        # Ask the user which action type to add
        type_dialog = QDialog(self)
        type_dialog.setWindowTitle("Select Action Type")
        dlg_layout = QVBoxLayout()
        cmb = QComboBox()
        cmb.addItems(["mouse_click", "mouse_move", "keyboard_text", "keyboard_key", "notification", "open_application", "sound"])
        dlg_layout.addWidget(QLabel("Action Type:"))
        dlg_layout.addWidget(cmb)
        btn_layout = QHBoxLayout()
        ok = QPushButton("OK")
        cancel = QPushButton("Cancel")
        btn_layout.addWidget(ok)
        btn_layout.addWidget(cancel)
        dlg_layout.addLayout(btn_layout)
        type_dialog.setLayout(dlg_layout)

        ok.clicked.connect(type_dialog.accept)
        cancel.clicked.connect(type_dialog.reject)

        if type_dialog.exec() == QDialog.DialogCode.Accepted:
            action_type = cmb.currentText()
            dialog = ActionDialog(action_type)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                action = dialog.get_action()
                self.actions_data.append(action)
                self.rebuild_tree()
    
    def get_actions_data(self):
        """Return all actions."""
        return self.actions_data

    def rebuild_tree(self):
        """Rebuild the action tree from the flat actions_data list."""
        self.action_tree.clear()
        groups = {}
        for idx, action in enumerate(self.actions_data):
            groups.setdefault(action.get('type', 'unknown'), []).append((idx, action))

        for action_type, items in groups.items():
            group_item = QTreeWidgetItem([action_type.upper(), f"{len(items)} actions"])
            for i, (idx, action) in enumerate(items):
                details = self.get_action_details(action)
                child_item = QTreeWidgetItem([f"Action {i+1}", details])
                child_item.action_index = idx
                group_item.addChild(child_item)
            self.action_tree.addTopLevelItem(group_item)

    def on_item_double_clicked(self, item, column):
        # Only allow editing child items that have an action_index
        if hasattr(item, 'action_index'):
            idx = item.action_index
            action = self.actions_data[idx]
            dialog = ActionDialog(action.get('type'), existing=action)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_action = dialog.get_action()
                self.actions_data[idx] = new_action
                self.rebuild_tree()


class ConditionalsEditor(QWidget):
    """Editor for structured if/else conditional blocks."""
    
    def __init__(self, condition_blocks=None):
        super().__init__()
        self.condition_blocks = condition_blocks or []
        self.block_widgets = []
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        main_layout.addWidget(QLabel("Conditional Blocks (If/Then/Else):"))
        
        # Scrollable area for blocks
        self.blocks_scroll = QScrollArea()
        self.blocks_scroll.setWidgetResizable(True)
        self.blocks_container = QWidget()
        self.blocks_layout = QVBoxLayout()
        self.blocks_container.setLayout(self.blocks_layout)
        self.blocks_scroll.setWidget(self.blocks_container)
        
        main_layout.addWidget(self.blocks_scroll)
        
        # Add block button
        add_block_btn = QPushButton("+ Add If/Else Block")
        add_block_btn.clicked.connect(self.add_block)
        main_layout.addWidget(add_block_btn)
        
        self.setLayout(main_layout)
        self.rebuild_blocks()
    
    def add_block(self):
        """Add a new if/else block."""
        new_block = {
            "if": {"type": "true"},
            "then": [],
            "else": []
        }
        self.condition_blocks.append(new_block)
        self.rebuild_blocks()
    
    def rebuild_blocks(self):
        """Rebuild all conditional blocks UI."""
        # Clear existing layouts
        for i in reversed(range(self.blocks_layout.count())):
            widget = self.blocks_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        self.block_widgets = []
        for idx, block in enumerate(self.condition_blocks):
            block_widget = self.create_block_widget(idx, block)
            self.blocks_layout.addWidget(block_widget)
        
        self.blocks_layout.addStretch()
    
    def create_block_widget(self, block_idx, block_data):
        """Create a visual widget for a single conditional block."""
        frame = QFrame()
        frame.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 10px;")
        frame.setLineWidth(2)
        layout = QVBoxLayout()
        
        # IF section
        if_group = QGroupBox("IF Condition")
        if_layout = QVBoxLayout()
        if_label = QLabel("Condition type:")
        if_combo = QComboBox()
        if_combo.addItems(["true", "voice_match", "battery", "custom"])
        # Determine initial displayed combo value; support legacy dict form
        stored_if = block_data.get('if', {})
        if isinstance(stored_if, dict):
            # Example legacy form: {"type": "system", "name": "battery", "op": "<", "value": 20}
            if_val = 'battery' if stored_if.get('type') == 'system' and stored_if.get('name') == 'battery' else 'custom'
        else:
            if_val = str(stored_if or 'true')
        if_combo.setCurrentText(if_val if if_val in ["true", "voice_match", "battery", "custom"] else "custom")
        if_layout.addWidget(if_label)
        if_layout.addWidget(if_combo)

        # Detail widget area for condition parameters (battery operator/value, voice phrase, custom expression)
        if_detail = QWidget()
        if_detail_layout = QHBoxLayout()
        if_detail_layout.setContentsMargins(0, 0, 0, 0)

        # Battery controls
        bat_op = QComboBox()
        bat_op.addItems(["<", "<=", ">", ">=", "==", "!="]) 
        bat_spin = QSpinBox()
        bat_spin.setRange(0, 100)
        bat_spin.setSuffix("%")

        # Voice controls
        voice_input = QLineEdit()
        voice_input.setPlaceholderText("Voice phrase to match")

        # Custom expression
        custom_input = QLineEdit()
        custom_input.setPlaceholderText("Custom condition expression")

        if_detail_layout.addWidget(bat_op)
        if_detail_layout.addWidget(bat_spin)
        if_detail_layout.addWidget(voice_input)
        if_detail_layout.addWidget(custom_input)
        if_detail.setLayout(if_detail_layout)

        # Populate detail controls from stored_if if present
        try:
            if isinstance(stored_if, dict) and stored_if.get('type') == 'system' and stored_if.get('name') == 'battery':
                bat_op.setCurrentText(stored_if.get('op', '<'))
                try:
                    bat_spin.setValue(int(stored_if.get('value', 0)))
                except Exception:
                    pass
            elif not isinstance(stored_if, dict) and str(stored_if):
                # simple string like 'true' or other
                pass
        except Exception:
            pass

        # show/hide detail controls according to combo
        def _update_if_detail(selected):
            bat_visible = (selected == 'battery')
            voice_visible = (selected == 'voice_match')
            custom_visible = (selected == 'custom')
            bat_op.setVisible(bat_visible)
            bat_spin.setVisible(bat_visible)
            voice_input.setVisible(voice_visible)
            custom_input.setVisible(custom_visible)
            # update underlying block_data when switching
            if selected == 'battery':
                block_data['if'] = { 'type': 'system', 'name': 'battery', 'op': bat_op.currentText(), 'value': bat_spin.value() }
            elif selected == 'voice_match':
                block_data['if'] = { 'type': 'voice', 'value': voice_input.text() }
            elif selected == 'custom':
                block_data['if'] = { 'type': 'custom', 'expr': custom_input.text() }
            else:
                block_data['if'] = {'type': 'true'}

        # wire change events to keep model in sync
        if_combo.currentTextChanged.connect(_update_if_detail)
        bat_op.currentTextChanged.connect(lambda v: _update_if_detail('battery'))
        bat_spin.valueChanged.connect(lambda v: _update_if_detail('battery'))
        voice_input.textChanged.connect(lambda txt: _update_if_detail('voice_match'))
        custom_input.textChanged.connect(lambda txt: _update_if_detail('custom'))

        if_layout.addWidget(if_detail)
        # Initialize visibility and model from current selection
        try:
            _update_if_detail(if_combo.currentText())
        except Exception:
            pass
        if_group.setLayout(if_layout)
        layout.addWidget(if_group)
        
        # THEN section (actions)
        # THEN section (actions) - show editable list
        then_group = QGroupBox("THEN - Actions to perform")
        then_layout = QVBoxLayout()
        then_list = QListWidget()
        then_actions = block_data.get('then', [])
        for a in then_actions:
            then_list.addItem(self._action_summary(a))
        then_list.itemDoubleClicked.connect(lambda it, bi=block_idx, sec='then', lst=then_list: self.edit_action_in_block(bi, sec, lst.row(it)))
        then_layout.addWidget(then_list)

        add_then_btn = QPushButton("Add Action to THEN")
        add_then_btn.clicked.connect(lambda: self.add_action_to_block(block_idx, "then"))
        then_layout.addWidget(add_then_btn)
        then_group.setLayout(then_layout)
        layout.addWidget(then_group)
        
        # ELSE section (optional actions)
        # ELIFs area (0..N)
        elifs = block_data.get('elif', [])
        if elifs:
            for e_idx, elif_block in enumerate(elifs):
                elif_group = QGroupBox(f"ELIF #{e_idx+1} - Condition & Actions")
                elif_layout = QVBoxLayout()
                # condition summary
                cond_lbl = QLabel(f"Condition: {elif_block.get('if', {})}")
                elif_layout.addWidget(cond_lbl)
                # actions list
                elif_list = QListWidget()
                for a in elif_block.get('then', []):
                    elif_list.addItem(self._action_summary(a))
                elif_list.itemDoubleClicked.connect(lambda it, bi=block_idx, sec=('elif', e_idx), lst=elif_list: self.edit_action_in_block(bi, sec, lst.row(it)))
                elif_layout.addWidget(elif_list)
                add_elif_then_btn = QPushButton("Add Action to ELIF")
                add_elif_then_btn.clicked.connect(lambda _, bi=block_idx, idx=e_idx: self.add_action_to_block(bi, ('elif', idx)))
                elif_layout.addWidget(add_elif_then_btn)
                elif_group.setLayout(elif_layout)
                layout.addWidget(elif_group)

        # ELSE section (optional actions)
        else_group = QGroupBox("ELSE - Fallback actions (optional)")
        else_layout = QVBoxLayout()
        else_list = QListWidget()
        for a in block_data.get('else', []):
            else_list.addItem(self._action_summary(a))
        else_list.itemDoubleClicked.connect(lambda it, bi=block_idx, sec='else', lst=else_list: self.edit_action_in_block(bi, sec, lst.row(it)))
        else_layout.addWidget(else_list)
        add_else_btn = QPushButton("Add Action to ELSE")
        add_else_btn.clicked.connect(lambda: self.add_action_to_block(block_idx, "else"))
        else_layout.addWidget(add_else_btn)
        else_group.setLayout(else_layout)
        layout.addWidget(else_group)

        # Add Else-If button
        add_elif_btn = QPushButton("+ Add Else-If")
        add_elif_btn.clicked.connect(lambda _, bi=block_idx: self.add_elif_to_block(bi))
        layout.addWidget(add_elif_btn)
        
        # Delete block button
        delete_btn = QPushButton("Delete This Block")
        delete_btn.setStyleSheet("color: red;")
        delete_btn.clicked.connect(lambda: self.delete_block(block_idx))
        layout.addWidget(delete_btn)
        
        frame.setLayout(layout)
        return frame
    
    def add_action_to_block(self, block_idx, section):
        """Add an action to a block's then or else section."""
        if block_idx >= len(self.condition_blocks):
            return

        title_section = ""
        if isinstance(section, tuple) and section[0] == 'elif':
            title_section = f"ELIF[{section[1]}]"
        elif isinstance(section, str):
            title_section = section.upper()

        # Show action type selector
        type_dialog = QDialog(self)
        type_dialog.setWindowTitle(f"Add Action to {title_section}")
        dlg_layout = QVBoxLayout()
        cmb = QComboBox()
        cmb.addItems(["mouse_click", "mouse_move", "keyboard_text", "keyboard_key", "notification", "open_application", "sound"])
        dlg_layout.addWidget(QLabel("Action Type:"))
        dlg_layout.addWidget(cmb)
        btn_layout = QHBoxLayout()
        ok = QPushButton("OK")
        cancel = QPushButton("Cancel")
        btn_layout.addWidget(ok)
        btn_layout.addWidget(cancel)
        dlg_layout.addLayout(btn_layout)
        type_dialog.setLayout(dlg_layout)
        
        ok.clicked.connect(type_dialog.accept)
        cancel.clicked.connect(type_dialog.reject)
        
        if type_dialog.exec() == QDialog.DialogCode.Accepted:
            action_type = cmb.currentText()
            dialog = ActionDialog(action_type)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                action = dialog.get_action()

                if isinstance(section, tuple) and section[0] == 'elif':
                    e_idx = section[1]
                    try:
                        self.condition_blocks[block_idx]['elif'][e_idx]['then'].append(action)
                    except (KeyError, IndexError):
                        # Block structure might be faulty, maybe just return
                        return
                else:
                    self.condition_blocks[block_idx].setdefault(section, []).append(action)
                
                self.rebuild_blocks()
    
    def delete_block(self, block_idx):
        """Delete a conditional block."""
        if block_idx < len(self.condition_blocks):
            reply = QMessageBox.question(self, "Confirm Delete", 
                                        "Delete this conditional block?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                del self.condition_blocks[block_idx]
                self.rebuild_blocks()
    
    def get_condition_blocks(self):
        """Return all condition blocks."""
        return self.condition_blocks

    def add_elif_to_block(self, block_idx):
        """Add an else-if (elif) to the given block."""
        if block_idx >= len(self.condition_blocks):
            return
        block = self.condition_blocks[block_idx]
        if 'elif' not in block:
            block['elif'] = []
        block['elif'].append({"if": {"type": "custom"}, "then": []})
        self.rebuild_blocks()

    def _action_summary(self, action):
        t = action.get('type', 'action')
        if t == 'notification':
            return f"Notification: {action.get('message', '')}"
        if t == 'open_application':
            return f"Open App: {action.get('app_path', action.get('app', ''))}"
        if t == 'sound':
            return f"Sound: {action.get('path', '')} x{action.get('repeat',1)}"
        if t == 'mouse_click':
            return f"Click ({action.get('x')},{action.get('y')}) {action.get('button','left')}"
        if t == 'mouse_move':
            return f"Move ({action.get('x')},{action.get('y')})"
        if t == 'keyboard_text':
            return f"Type: {action.get('text','')}"
        if t == 'keyboard_key':
            return f"Key: {action.get('key','')}"
        return json.dumps(action)

    def edit_action_in_block(self, block_idx, section, action_idx):
        """Edit an existing action inside a block (then/else/elif)."""
        if block_idx >= len(self.condition_blocks):
            return
        # locate the action
        if isinstance(section, tuple) and section[0] == 'elif':
            e_idx = section[1]
            try:
                action = self.condition_blocks[block_idx]['elif'][e_idx]['then'][action_idx]
            except Exception:
                return
            dialog = ActionDialog(action.get('type'), existing=action)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_action = dialog.get_action()
                self.condition_blocks[block_idx]['elif'][e_idx]['then'][action_idx] = new_action
                self.rebuild_blocks()
        else:
            try:
                action = self.condition_blocks[block_idx].get(section, [])[action_idx]
            except Exception:
                return
            dialog = ActionDialog(action.get('type'), existing=action)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_action = dialog.get_action()
                self.condition_blocks[block_idx].setdefault(section, [])[action_idx] = new_action
                self.rebuild_blocks()


class MacroEditorPanel(QWidget):
    """Panel to edit a selected macro's triggers and actions."""
    
    def __init__(self, macro_data=None, on_save_callback=None):
        super().__init__()
        self.macro_data = macro_data or {"name": "new_macro", "trigger": {}, "actions": []}
        self.on_save_callback = on_save_callback
        self.init_ui()
    
    
    def _get_running_apps(self):
        """Get list of running applications (Windows-specific)."""
        apps = []
        try:
            # Use window titles (pygetwindow) like the main app does for a concise selector
            import pygetwindow as gw
            for w in gw.getAllWindows():
                try:
                    title = w.title
                    if title and title.strip() and title not in apps:
                        apps.append(title.strip())
                except Exception:
                    pass
            # Deduplicate and limit to a reasonable number
            unique = list(dict.fromkeys(apps))
            return unique[:30]
        except Exception:
            # Fallback to psutil process names if pygetwindow not available
            try:
                import psutil
                for proc in psutil.process_iter(['name']):
                    try:
                        app_name = proc.info['name']
                        if app_name and app_name not in apps and not app_name.startswith('svchost'):
                            apps.append(app_name.replace('.exe', ''))
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                return sorted(list(set(apps)))[:50]
            except Exception:
                return []
    
    def _extract_actions(self):
        """Extract actions from macro_data, supporting both flat and structured formats."""
        # Check for structured condition_blocks first
        condition_blocks = self.macro_data.get("condition_blocks", [])
        if condition_blocks:
            # Flatten all "then" actions from condition blocks
            all_actions = []
            for block in condition_blocks:
                if isinstance(block, dict) and "then" in block:
                    all_actions.extend(block["then"])
            return all_actions
        # Fall back to flat actions list (backward compatibility)
        return self.macro_data.get("actions", [])
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Macro name
        name_layout = QVBoxLayout()
        name_label = QLabel("Macro Name:")
        self.name_input = QLineEdit(self.macro_data.get("name", ""))
        self.name_input.setReadOnly(True)  # Name shouldn't change
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Status and App selection (top row)
        settings_layout = QHBoxLayout()
        
        # Status
        status_label = QLabel("Status:")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["on", "off"])
        self.status_combo.setCurrentText(self.macro_data.get("status", "on"))
        settings_layout.addWidget(status_label)
        settings_layout.addWidget(self.status_combo)
        
        settings_layout.addSpacing(20)
        
        # App selector
        app_label = QLabel("App:")
        self.app_combo = QComboBox()
        self.app_combo.addItems(["global"] + self._get_running_apps())
        app_value = self.macro_data.get("app", "global")
        idx = self.app_combo.findText(app_value)
        if idx >= 0:
            self.app_combo.setCurrentIndex(idx)
        settings_layout.addWidget(app_label)
        settings_layout.addWidget(self.app_combo)
        settings_layout.addStretch()
        layout.addLayout(settings_layout)
        
        # Loop settings
        loop_layout = QHBoxLayout()
        self.loop_checkbox = QCheckBox("Loop Macro")
        self.loop_checkbox.setChecked(self.macro_data.get("loop", False))
        loop_layout.addWidget(self.loop_checkbox)
        
        loop_interval_label = QLabel("Loop Interval (ms):")
        self.loop_interval_spin = QSpinBox()
        self.loop_interval_spin.setMinimum(100)
        self.loop_interval_spin.setMaximum(60000)
        self.loop_interval_spin.setValue(self.macro_data.get("loop_interval", 1000))
        loop_layout.addWidget(loop_interval_label)
        loop_layout.addWidget(self.loop_interval_spin)
        loop_layout.addStretch()
        layout.addLayout(loop_layout)
        
        # Tabs for trigger, actions, and conditionals
        tabs = QTabWidget()
        
        # Trigger tab
        self.trigger_editor = TriggerEditor(self.macro_data.get("trigger", {}))
        tabs.addTab(self.trigger_editor, "Trigger")
        
        # Actions tab (merged into conditionals editor)
        self.conditionals_editor = ConditionalsEditor(self.macro_data.get("condition_blocks", []))
        tabs.addTab(self.conditionals_editor, "Actions")
        
        layout.addWidget(tabs)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        
        # Save button
        save_btn = QPushButton("Save Macro")
        save_btn.clicked.connect(self.save_macro)
        button_layout.addWidget(save_btn)
        
        # Delete button
        delete_btn = QPushButton("Delete Macro")
        delete_btn.clicked.connect(self.delete_macro)
        button_layout.addWidget(delete_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def save_macro(self):
        """Save macro to JSON with all fields."""
        from macros.macro_json_manager import MacroJsonManager
        import json
        
        macro_name = self.name_input.text()
        manager = MacroJsonManager()
        
        try:
            # Gather all data from UI
            trigger_data = self.trigger_editor.get_trigger_data()
            condition_blocks = self.conditionals_editor.get_condition_blocks()
            else_actions = self.macro_data.get('else_actions', [])
            loop_enabled = self.loop_checkbox.isChecked()
            loop_interval = self.loop_interval_spin.value()
            status = self.status_combo.currentText()
            app = self.app_combo.currentText()
            
            print(f"\n{'='*60}")
            print(f"[GUI SAVE] Starting save for macro: {macro_name}")
            print(f"[GUI SAVE] Status: {status}")
            print(f"[GUI SAVE] App: {app}")
            print(f"[GUI SAVE] Loop: {loop_enabled} (interval: {loop_interval}ms)")
            print(f"[GUI SAVE] Trigger: {json.dumps(trigger_data)}")
            print(f"[GUI SAVE] Has {len(condition_blocks)} condition block(s)")
            print(f"{'='*60}\n")
            
            # Load existing macro data to preserve fields not being edited
            existing = manager.load_macro(macro_name)
            
            # Update with all new values
            existing['trigger'] = trigger_data
            existing['condition_blocks'] = condition_blocks if condition_blocks else existing.get('condition_blocks', [])
            existing['else_actions'] = else_actions
            existing['loop'] = loop_enabled
            existing['loop_interval'] = loop_interval
            existing['status'] = status
            existing['app'] = app
            existing['modified'] = datetime.datetime.now().isoformat()
            
            # Write directly to file (bypass update_macro to have full control)
            filepath = os.path.join(manager.macro_dir, f"{macro_name}.json")
            with open(filepath, 'w') as f:
                json.dump(existing, f, indent=2)
            
            print(f"[GUI SAVE] Successfully wrote to: {filepath}")
            print(f"[GUI SAVE] File size: {os.path.getsize(filepath)} bytes")
            print(f"[GUI SAVE] Modified timestamp: {os.path.getmtime(filepath)}")
            
            # Verify by reading back
            with open(filepath, 'r') as f:
                verify = json.load(f)
            print(f"[GUI SAVE] Verification: trigger.value = {verify.get('trigger', {}).get('value')}")
            print(f"[GUI SAVE] Verification: status = {verify.get('status')}")
            print(f"[GUI SAVE] Verification: app = {verify.get('app')}")
            print(f"[GUI SAVE] Save complete!\n")
            # Reload the saved file into the editor so the UI reflects on-disk state
            try:
                loaded = manager.load_macro(macro_name)
                self.macro_data = loaded
                # Update status and app
                try:
                    self.status_combo.setCurrentText(loaded.get('status', 'on'))
                except Exception:
                    pass
                app_val = loaded.get('app', 'global')
                try:
                    if self.app_combo.findText(app_val) == -1:
                        self.app_combo.addItem(app_val)
                    self.app_combo.setCurrentText(app_val)
                except Exception:
                    pass

                # Update loop settings
                try:
                    self.loop_checkbox.setChecked(bool(loaded.get('loop', False)))
                    self.loop_interval_spin.setValue(int(loaded.get('loop_interval', 1000)))
                except Exception:
                    pass

                # Update trigger editor
                try:
                    trig = loaded.get('trigger', {}) or {}
                    ttype = trig.get('type', 'voice')
                    self.trigger_editor.trigger_type_combo.setCurrentText(ttype)
                    # load value into the specific editor
                    self.trigger_editor._load_trigger_data(ttype)
                    self.trigger_editor.on_trigger_type_changed(ttype)
                except Exception:
                    pass

                # Update conditionals editor
                try:
                    self.conditionals_editor.condition_blocks = loaded.get('condition_blocks', []) or []
                    self.conditionals_editor.rebuild_blocks()
                except Exception:
                    pass

                print("[GUI SAVE] UI reloaded from disk after save")
            except Exception as e:
                print(f"[GUI SAVE] Failed to reload UI from disk: {e}")

            QMessageBox.information(self, "Success", f"Macro '{macro_name}' saved successfully!")
            if self.on_save_callback:
                self.on_save_callback()
        except Exception as e:
            print(f"\n[GUI SAVE ERROR] {str(e)}")
            import traceback
            traceback.print_exc()
            print()
            QMessageBox.critical(self, "Error", f"Failed to save macro: {str(e)}")
    
    def delete_macro(self):
        """Delete macro after confirmation."""
        macro_name = self.name_input.text()
        reply = QMessageBox.question(self, "Confirm Delete", 
                                     f"Are you sure you want to delete '{macro_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            from macros.macro_json_manager import MacroJsonManager
            manager = MacroJsonManager()
            
            try:
                manager.delete_macro(macro_name)
                QMessageBox.information(self, "Success", f"Macro '{macro_name}' deleted successfully!")
                if self.on_save_callback:
                    self.on_save_callback()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete macro: {str(e)}")


class NewMacroPanel(QWidget):
    """Panel for creating new macros from scratch."""
    
    def __init__(self):
        super().__init__()
        self.actions_data = []
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Macro name
        name_layout = QVBoxLayout()
        name_label = QLabel("Macro Name:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., my_automation")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Loop settings
        loop_layout = QVBoxLayout()
        self.loop_checkbox = QCheckBox("Loop Macro")
        self.loop_checkbox.setChecked(False)
        loop_label = QLabel("(Press ESC to stop looping)")
        loop_layout.addWidget(self.loop_checkbox)
        loop_layout.addWidget(loop_label)
        layout.addLayout(loop_layout)
        
        # Timing
        timing_layout = QVBoxLayout()
        timing_label = QLabel("Loop Interval (ms):")
        self.timing_spinbox = QSpinBox()
        self.timing_spinbox.setMinimum(0)
        self.timing_spinbox.setMaximum(10000)
        self.timing_spinbox.setValue(1000)
        timing_layout.addWidget(timing_label)
        timing_layout.addWidget(self.timing_spinbox)
        layout.addLayout(timing_layout)
        
        # Trigger editor
        trigger_label = QLabel("Trigger:")
        self.trigger_editor = TriggerEditor()
        layout.addWidget(trigger_label)
        layout.addWidget(self.trigger_editor)
        
        # Action list with add buttons
        actions_label = QLabel("Actions:")
        layout.addWidget(actions_label)
        
        self.actions_list = QListWidget()
        layout.addWidget(self.actions_list)
        
        # Add action buttons
        buttons_layout = QVBoxLayout()
        
        add_click_btn = QPushButton("Add Mouse Click")
        add_click_btn.clicked.connect(self.add_mouse_click)
        buttons_layout.addWidget(add_click_btn)
        
        add_move_btn = QPushButton("Add Mouse Move")
        add_move_btn.clicked.connect(self.add_mouse_move)
        buttons_layout.addWidget(add_move_btn)
        
        add_type_btn = QPushButton("Add Keyboard Type")
        add_type_btn.clicked.connect(self.add_keyboard_type)
        buttons_layout.addWidget(add_type_btn)
        
        add_key_btn = QPushButton("Add Keyboard Key")
        add_key_btn.clicked.connect(self.add_keyboard_key)
        buttons_layout.addWidget(add_key_btn)
        
        add_notification_btn = QPushButton("Add Notification")
        add_notification_btn.clicked.connect(self.add_notification)
        buttons_layout.addWidget(add_notification_btn)

        add_sound_btn = QPushButton("Add Sound")
        add_sound_btn.clicked.connect(self.add_sound)
        buttons_layout.addWidget(add_sound_btn)
        
        # Delete action button
        delete_btn = QPushButton("Delete Selected Action")
        delete_btn.clicked.connect(self.delete_action)
        buttons_layout.addWidget(delete_btn)
        
        layout.addLayout(buttons_layout)
        
        # Save button
        save_btn = QPushButton("Create Macro")
        save_btn.clicked.connect(self.create_macro)
        layout.addWidget(save_btn)        
        layout.addStretch()
        self.setLayout(layout)
    
    def add_mouse_click(self):
        """Add a mouse click action."""
        dialog = ActionDialog("mouse_click")
        if dialog.exec():
            action = dialog.get_action()
            self.actions_data.append(action)
            self.actions_list.addItem(f"Click at ({action['x']}, {action['y']}) - {action['button']}")
    
    def add_mouse_move(self):
        """Add a mouse move action."""
        dialog = ActionDialog("mouse_move")
        if dialog.exec():
            action = dialog.get_action()
            self.actions_data.append(action)
            self.actions_list.addItem(f"Move to ({action['x']}, {action['y']})")
    
    def add_keyboard_type(self):
        """Add a keyboard type action."""
        dialog = ActionDialog("keyboard_text")
        if dialog.exec():
            action = dialog.get_action()
            self.actions_data.append(action)
            self.actions_list.addItem(f"Type: '{action['text']}'")
    
    def add_keyboard_key(self):
        """Add a keyboard key press action."""
        dialog = ActionDialog("keyboard_key")
        if dialog.exec():
            action = dialog.get_action()
            self.actions_data.append(action)
            self.actions_list.addItem(f"Press: {action['key']}")

    def add_notification(self):
        dialog = ActionDialog("notification")
        if dialog.exec():
            action = dialog.get_action()
            self.actions_data.append(action)
            self.actions_list.addItem(f"Notification: {action.get('message','')}")

    def add_sound(self):
        dialog = ActionDialog("sound")
        if dialog.exec():
            action = dialog.get_action()
            self.actions_data.append(action)
            self.actions_list.addItem(f"Sound: {action.get('path','')} x{action.get('repeat',1)}")
    
    def delete_action(self):
        """Delete the selected action."""
        current_row = self.actions_list.currentRow()
        if current_row >= 0:
            self.actions_list.takeItem(current_row)
            self.actions_data.pop(current_row)
    
    def create_macro(self):
        """Create and save the new macro."""
        if not self.name_input.text():
            QMessageBox.warning(self, "Error", "Please enter a macro name")
            return
        
        if not self.actions_data:
            QMessageBox.warning(self, "Error", "Please add at least one action")
            return
        
        from macros.macro_json_manager import MacroJsonManager
        
        manager = MacroJsonManager()
        try:
            manager.save_macro(
                macro_name=self.name_input.text(),
                trigger=self.trigger_editor.get_trigger_data(),
                actions=self.actions_data,
                loop=self.loop_checkbox.isChecked(),
                loop_interval=self.timing_spinbox.value()
            )
            QMessageBox.information(self, "Success", f"Macro '{self.name_input.text()}' created successfully!")
            # Notify parent window to refresh macro list if available
            win = self.window()
            try:
                if hasattr(win, 'refresh_macros'):
                    win.refresh_macros()
            except Exception:
                pass
            self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create macro: {str(e)}")
    
    def clear_form(self):
        """Clear the form."""
        self.name_input.clear()
        self.actions_list.clear()
        self.actions_data = []
        self.loop_checkbox.setChecked(False)
        self.timing_spinbox.setValue(1000)



class ActionDialog(QDialog):
    """Dialog to configure a single action."""
    
    def __init__(self, action_type, existing=None):
        super().__init__()
        self.action_type = action_type
        self.action_data = {}
        self.existing = existing or {}
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        if self.action_type == "mouse_click":
            layout.addWidget(QLabel("X coordinate:"))
            self.x_spin = QSpinBox()
            self.x_spin.setMaximum(5000)
            if 'x' in self.existing:
                self.x_spin.setValue(int(self.existing.get('x', 0)))
            layout.addWidget(self.x_spin)
            
            layout.addWidget(QLabel("Y coordinate:"))
            self.y_spin = QSpinBox()
            self.y_spin.setMaximum(5000)
            if 'y' in self.existing:
                self.y_spin.setValue(int(self.existing.get('y', 0)))
            layout.addWidget(self.y_spin)
            
            layout.addWidget(QLabel("Button:"))
            self.button_combo = QComboBox()
            self.button_combo.addItems(["left", "right", "middle"])
            if 'button' in self.existing:
                self.button_combo.setCurrentText(self.existing.get('button'))
            layout.addWidget(self.button_combo)
            
            layout.addWidget(QLabel("Delay after (ms):"))
            self.dt_spin = QSpinBox()
            self.dt_spin.setMaximum(5000)
            self.dt_spin.setValue(int(self.existing.get('dt', 100)))
            layout.addWidget(self.dt_spin)
        
        elif self.action_type == "mouse_move":
            layout.addWidget(QLabel("X coordinate:"))
            self.x_spin = QSpinBox()
            self.x_spin.setMaximum(5000)
            if 'x' in self.existing:
                self.x_spin.setValue(int(self.existing.get('x', 0)))
            layout.addWidget(self.x_spin)
            
            layout.addWidget(QLabel("Y coordinate:"))
            self.y_spin = QSpinBox()
            self.y_spin.setMaximum(5000)
            if 'y' in self.existing:
                self.y_spin.setValue(int(self.existing.get('y', 0)))
            layout.addWidget(self.y_spin)
            
            layout.addWidget(QLabel("Delay after (ms):"))
            self.dt_spin = QSpinBox()
            self.dt_spin.setMaximum(5000)
            self.dt_spin.setValue(int(self.existing.get('dt', 50)))
            layout.addWidget(self.dt_spin)
        
        elif self.action_type == "keyboard_text":
            layout.addWidget(QLabel("Text to type:"))
            self.text_input = QLineEdit()
            if 'text' in self.existing:
                self.text_input.setText(str(self.existing.get('text', '')))
            layout.addWidget(self.text_input)
            
            layout.addWidget(QLabel("Delay after (ms):"))
            self.dt_spin = QSpinBox()
            self.dt_spin.setMaximum(5000)
            self.dt_spin.setValue(int(self.existing.get('dt', 50)))
            layout.addWidget(self.dt_spin)
        
        elif self.action_type == "keyboard_key":
            layout.addWidget(QLabel("Key to press:"))
            self.key_input = QLineEdit()
            self.key_input.setPlaceholderText("e.g., 'return', 'shift', 'ctrl'")
            if 'key' in self.existing:
                self.key_input.setText(str(self.existing.get('key', '')))
            layout.addWidget(self.key_input)
            
            layout.addWidget(QLabel("Delay after (ms):"))
            self.dt_spin = QSpinBox()
            self.dt_spin.setMaximum(5000)
            self.dt_spin.setValue(int(self.existing.get('dt', 100)))
            layout.addWidget(self.dt_spin)
        
        elif self.action_type == "notification":
            layout.addWidget(QLabel("Notification Message:"))
            self.message_input = QLineEdit()
            if 'message' in self.existing:
                self.message_input.setText(str(self.existing.get('message', '')))
            layout.addWidget(self.message_input)
        
        elif self.action_type == "sound":
            layout.addWidget(QLabel("Sound File:"))
            file_layout = QHBoxLayout()
            self.sound_path_input = QLineEdit()
            if 'path' in self.existing:
                self.sound_path_input.setText(str(self.existing.get('path', '')))
            browse_btn = QPushButton("Browse")
            def on_browse():
                path, _ = QFileDialog.getOpenFileName(self, "Select Sound File", "", "Audio Files (*.wav *.mp3);;All Files (*)")
                if path:
                    self.sound_path_input.setText(path)
            browse_btn.clicked.connect(on_browse)
            file_layout.addWidget(self.sound_path_input)
            file_layout.addWidget(browse_btn)
            layout.addLayout(file_layout)
            layout.addWidget(QLabel("Repeat count (1 = once):"))
            self.repeat_spin = QSpinBox()
            self.repeat_spin.setMinimum(1)
            self.repeat_spin.setMaximum(9999)
            self.repeat_spin.setValue(int(self.existing.get('repeat', 1)))
            layout.addWidget(self.repeat_spin)
        
        elif self.action_type == "open_application":
            layout.addWidget(QLabel("Application to open:"))
            self.app_combo = QComboBox()
            # Populate with common applications on Windows
            common_apps = [
                ("Notepad", "notepad.exe"),
                ("Calculator", "calc.exe"),
                ("Paint", "mspaint.exe"),
                ("Word", "winword.exe"),
                ("Excel", "excel.exe"),
                ("PowerPoint", "powerpnt.exe"),
                ("Chrome", "chrome.exe"),
                ("Firefox", "firefox.exe"),
                ("Edge", "msedge.exe"),
                ("VSCode", "code.exe"),
                ("Custom Path", "")
            ]
            for app_name, app_path in common_apps:
                self.app_combo.addItem(app_name, app_path)
            if 'app_path' in self.existing:
                # Try to find matching app
                app_path = self.existing.get('app_path', '')
                idx = self.app_combo.findData(app_path)
                if idx >= 0:
                    self.app_combo.setCurrentIndex(idx)
            layout.addWidget(self.app_combo)
            
            # Allow custom path if needed
            layout.addWidget(QLabel("Custom path (leave empty for default):"))
            self.app_path_input = QLineEdit()
            if 'app_path' in self.existing:
                self.app_path_input.setText(str(self.existing.get('app_path', '')))
            layout.addWidget(self.app_path_input)
        
        # OK/Cancel buttons
        button_layout = QVBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.setWindowTitle(f"Configure {self.action_type}")
    
    def get_action(self):
        """Return the configured action."""
        action = {"type": self.action_type}
        
        if self.action_type == "mouse_click":
            action["x"] = self.x_spin.value()
            action["y"] = self.y_spin.value()
            action["button"] = self.button_combo.currentText()
            action["dt"] = self.dt_spin.value()
        elif self.action_type == "mouse_move":
            action["x"] = self.x_spin.value()
            action["y"] = self.y_spin.value()
            action["dt"] = self.dt_spin.value()
        elif self.action_type == "keyboard_text":
            action["text"] = self.text_input.text()
            action["dt"] = self.dt_spin.value()
        elif self.action_type == "keyboard_key":
            action["key"] = self.key_input.text()
            action["dt"] = self.dt_spin.value()
        elif self.action_type == "notification":
            action["message"] = self.message_input.text()
        elif self.action_type == "open_application":
            custom_path = self.app_path_input.text().strip()
            if custom_path:
                action["app_path"] = custom_path
            else:
                action["app_path"] = self.app_combo.currentData()
        elif self.action_type == "sound":
            action["path"] = self.sound_path_input.text()
            action["repeat"] = int(self.repeat_spin.value())
        
        return action


class MacroManagerWindow(QMainWindow):
    """Main window for macro management."""
    
    def __init__(self, file_path=None):
        super().__init__()
        self.macro_dir = "Macros_json"
        self.macros = {}
        self.load_macros()
        self.init_ui()

        if file_path:
            # Extract macro name from file path (e.g., "Macros_json/my_macro.json" -> "my_macro")
            macro_name = os.path.splitext(os.path.basename(file_path))[0]
            items = self.macros_list.findItems(macro_name, Qt.MatchFlag.MatchExactly)
            if items:
                # Select the item and trigger the editor to open
                self.macros_list.setCurrentItem(items[0])
                self.on_macro_selected(items[0])
    
    def init_ui(self):
        self.setWindowTitle("Macro Manager")
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Window)
        self.showMaximized()
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Left panel
        left_layout = QVBoxLayout()
        
        # Macros list
        macros_label = QLabel("Macros:")
        left_layout.addWidget(macros_label)
        
        self.macros_list = QListWidget()
        self.macros_list.itemClicked.connect(self.on_macro_selected)
        for macro_name in self.macros.keys():
            self.macros_list.addItem(macro_name)
        left_layout.addWidget(self.macros_list)
        
        # Create new macro button
        create_btn = QPushButton("Create New Macro")
        create_btn.clicked.connect(self.create_new_macro)
        left_layout.addWidget(create_btn)
        
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setMaximumWidth(300)
        
        # Right panel - editor
        self.right_layout = QVBoxLayout()
        
        # Add placeholder text
        placeholder = QLabel("Select a macro to edit or create a new one")
        placeholder.setStyleSheet("color: gray; font-style: italic;")
        self.right_layout.addWidget(placeholder)
        self.right_layout.addStretch()
        
        self.editor_widget = QWidget()
        self.editor_widget.setLayout(self.right_layout)
        
        scroll = QScrollArea()
        scroll.setWidget(self.editor_widget)
        scroll.setWidgetResizable(True)
        
        # Add panels to main layout
        main_layout.addWidget(left_widget)
        main_layout.addWidget(scroll)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def load_macros(self):
        """Load all macros from Macros_json folder."""
        if os.path.exists(self.macro_dir):
            for filename in os.listdir(self.macro_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.macro_dir, filename)
                    with open(filepath, 'r') as f:
                        macro_data = json.load(f)
                        self.macros[macro_data.get('name', filename)] = macro_data
    
    def on_macro_selected(self, item):
        """Handle macro selection."""
        macro_name = item.text()
        macro_data = self.macros.get(macro_name)
        
        # Clear right panel
        for i in reversed(range(self.right_layout.count())):
            widget = self.right_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Show editor for selected macro
        editor = MacroEditorPanel(macro_data, on_save_callback=self.refresh_macros)
        self.right_layout.addWidget(editor)
    
    def refresh_macros(self):
        """Refresh the macros list."""
        self.macros = {}
        self.load_macros()
        self.macros_list.clear()
        for macro_name in self.macros.keys():
            self.macros_list.addItem(macro_name)
    
    def create_new_macro(self):
        """Show interface for creating new macro."""
        # Clear right panel
        for i in reversed(range(self.right_layout.count())):
            widget = self.right_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Show new macro panel
        panel = NewMacroPanel()
        self.right_layout.addWidget(panel)
        self.right_layout.addStretch()

    def closeEvent(self, event):
        """Ensure controller reference is cleared when the window closes."""
        try:
            # Avoid circular import at module load time
            from app import controller as app_controller
            if hasattr(app_controller, 'controller'):
                app_controller.controller.macro_manager_window = None
        except Exception:
            pass
        super().closeEvent(event)
