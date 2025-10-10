import time

from voiceRecog import VoiceListener

listener = VoiceListener()

try:
    while True:
        print(f"Listening flag: {listener.is_listening()} | Heard: {listener.get_listened_text()}")
        time.sleep(1)
except KeyboardInterrupt:
    listener.stop()
