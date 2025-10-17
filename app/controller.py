# controller.py
from voiceRecog import VoiceListener


class Controller:
    def __init__(self, wakeword="hello", silencetimeout=4):
        self.listener = VoiceListener(wakeword, silencetimeout)

    def is_listening(self):
        return self.listener.is_listening()
    
    def get_listened_text(self):
        return self.listener.get_listened_text()
    
    def stop(self):
        self.listener.stop()

# Create a single Controller instance
controller = Controller()
