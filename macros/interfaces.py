from abc import ABC, abstractmethod
from typing import Any


class IMacroRecorder(ABC):
    @abstractmethod
    def start_recording(self, name: str, trigger_info: dict) -> None:
        pass

    @abstractmethod
    def stop_recording(self) -> None:
        pass


class IMacroPlayer(ABC):
    @abstractmethod
    def play(self, macro_name: str) -> None:
        pass

    @abstractmethod
    def stop_playback(self) -> None:
        pass
