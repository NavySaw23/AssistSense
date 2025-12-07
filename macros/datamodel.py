import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ScreenInfo:
    width: int
    height: int


@dataclass
class TriggerInfo:
    type: str  # e.g., "voice", "gesture", "shortcut"
    value: str  # e.g., "youtube mode", "swipe_up", "Ctrl+Alt+Y"


@dataclass
class Action:
    dt: int  # milliseconds
    type: str
    # Using Any for flexibility, but you can create specific Action subclasses
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Macro:
    name: str
    screen: ScreenInfo
    trigger: TriggerInfo
    actions: List[Action]
    version: int = 1
    normalized: bool = True
    createdAt: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    def to_json(self) -> Dict[str, Any]:
        # A helper to convert to the dictionary format you specified
        # This can be made more robust with a custom JSON encoder
        return self.__dict__
