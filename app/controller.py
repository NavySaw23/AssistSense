import sys
import os

# Add the project root to the Python path to allow direct execution of this file
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

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

if __name__ == '__main__':
    # This block will be executed only when the script is run directly
    # It can be used for testing the Controller class independently
    print("Controller script running directly for testing.")
    try:
        while True:
            print(f"Listening flag: {controller.is_listening()} | Heard: {controller.get_listened_text()}")
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        controller.stop()
        print("Controller script stopped.")