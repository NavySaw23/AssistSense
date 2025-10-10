import sys
import threading
import time

import speech_recognition as sr


class VoiceListener:
    def __init__(self, wake_word="hello", silence_timeout=3):
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.stop_flag = False
        self.active = False
        self.latest_text = ""
        self.wake_word = wake_word.lower()
        self.silence_timeout = silence_timeout
        self.listening_flag = 0  # 1 = active listening, 0 = passive

        # Calibrate mic
        with self.mic as source:
            print("Calibrating microphone... please stay quiet.")
            self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
            print(f"Calibration complete. Energy threshold: {self.recognizer.energy_threshold}")

        # Run background thread
        self.thread = threading.Thread(target=self._run_listener, daemon=True)
        self.thread.start()

    def _run_listener(self):
        """Main background loop that switches between passive and active modes."""
        while not self.stop_flag:
            if not self.active:
                self._listen_for_wake_word()
            else:
                self._active_listen()

    def _listen_for_wake_word(self):
        """Wait for wake word."""
        with self.mic as source:
            print("(passive) Listening for wake word...")
            audio = self.recognizer.listen(source, phrase_time_limit=3)
        try:
            text = self.recognizer.recognize_google(audio).lower()
            print(f"[passive] Heard: {text}")
            if self.wake_word in text:
                print("Wake word detected! Entering active mode...")
                self.active = True
                self.listening_flag = 1
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"[recognize] API request error: {e}", file=sys.stderr)

    def _active_listen(self):
        """Listen actively for commands until silence."""
        last_spoken_time = time.time()
        while self.active and not self.stop_flag:
            with self.mic as source:
                print("(active) Listening...")
                audio = self.recognizer.listen(source, phrase_time_limit=3)

            try:
                text = self.recognizer.recognize_google(audio)
                self.latest_text = text
                last_spoken_time = time.time()
                print(f"[active] {text}")
            except sr.UnknownValueError:
                # silence or unclear speech
                pass
            except sr.RequestError as e:
                print(f"[recognize] API request error: {e}", file=sys.stderr)

            # If silence detected for more than timeout seconds, go passive again
            if time.time() - last_spoken_time > self.silence_timeout:
                print("Silence timeout. Returning to passive mode.")
                self.active = False
                self.listening_flag = 0
                self.latest_text = ""
                break

    def get_listened_text(self):
        """Return the most recent active-mode speech."""
        return self.latest_text

    def is_listening(self):
        """Return 1 when actively listening (after wake word), else 0."""
        return self.listening_flag

    def stop(self):
        """Stop background loop."""
        print("Stopping listener...")
        self.stop_flag = True
