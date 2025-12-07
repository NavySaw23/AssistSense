import sys
import threading
import time
import config
import speech_recognition as sr


class VoiceListener:
    def __init__(self, wake_word="hello", silence_timeout=3, mode=config.VOICE_RECOGNITION_MODE):
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.stop_flag = False
        self.active = False
        # latest_text is used for trigger consumption; latest_display_text is used by the GUI
        self.latest_text = ""
        self.latest_display_text = ""
        self.wake_word = wake_word.lower()
        self.silence_timeout = silence_timeout
        self.listening_flag = 0  # 1 = active listening, 0 = passive
        self.mode = mode
        self.paused = False
        # When True, always stay in active listening mode (used during recording/playback)
        self.force_active_mode = False

        # Optimize recognizer for faster, more reliable recognition
        self.recognizer.energy_threshold = 4000  # Adjust sensitivity (lower = more sensitive)
        self.recognizer.dynamic_energy_threshold = True  # Auto-adjust to environment
        self.recognizer.phrase_threshold = 0.3  # Lower = accepts shorter phrases
        self.recognizer.non_speaking_duration = 0.8  # Shorter detection of speech end

        # Calibrate mic (2 seconds for better noise profile)
        with self.mic as source:
            print("Calibrating microphone... please stay quiet.")
            self.recognizer.adjust_for_ambient_noise(source, duration=2.0)
            print(f"Calibration complete. Energy threshold: {self.recognizer.energy_threshold}")

        # Run background thread
        self.thread = threading.Thread(target=self._run_listener, daemon=True)
        self.thread.start()

    def _run_listener(self):
        """Main background loop that switches between passive and active modes,
        unless force_active_mode is True (during recording/playback).
        """
        while not self.stop_flag:
            if self.paused:
                time.sleep(0.1)
                continue

            # If force_active_mode is True, always stay active
            if self.force_active_mode:
                if not self.active:
                    self.active = True
                    self.listening_flag = 1
                self._active_listen()
            elif not self.active:
                self._listen_for_wake_word()
            else:
                self._active_listen()

    def _listen_for_wake_word(self):
        """Wait for wake word."""
        with self.mic as source:
            print("(passive) Listening for wake word...")
            audio = self.recognizer.listen(source, phrase_time_limit=2.0)
        try:
            text = ""
            if self.mode == "online":
                text = self.recognizer.recognize_google(audio).lower()
            else:
                text = self.recognizer.recognize_whisper(audio, model="base.en").lower()
            # passive recognition completed
            if self.wake_word in text:
                print("Wake word detected! Entering active mode...")
                self.active = True
                self.listening_flag = 1
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"[recognize] API request error: {e}", file=sys.stderr)

    def _active_listen(self):
        """Listen actively for commands until silence (unless force_active_mode is True)."""
        last_spoken_time = time.time()
        while self.active and not self.stop_flag:
            with self.mic as source:
                print("(active) Listening...")
                audio = self.recognizer.listen(source, phrase_time_limit=5.0)

            try:
                text = ""
                if self.mode == "online":
                    text = self.recognizer.recognize_google(audio)
                else:
                    text = self.recognizer.recognize_whisper(audio, model="base.en")
                # set both consumption and display buffers
                self.latest_text = text
                self.latest_display_text = text
                last_spoken_time = time.time()
            except sr.UnknownValueError:
                # silence or unclear speech
                pass
            except sr.RequestError as e:
                print(f"[recognize] API request error: {e}", file=sys.stderr)

            # If force_active_mode is on, never timeout; stay listening indefinitely
            if self.force_active_mode:
                continue

            # If silence detected for more than timeout seconds, go passive again
            if time.time() - last_spoken_time > self.silence_timeout:
                print("Silence timeout. Returning to passive mode.")
                self.active = False
                self.listening_flag = 0
                # clear both buffers when silence returns
                self.latest_text = ""
                self.latest_display_text = ""
                break

    def get_listened_text(self):
        """Return the most recent active-mode speech for display (non-destructive)."""
        return self.latest_display_text

    def pop_listened_text(self):
        """Return the most recent active-mode speech and clear it so it isn't
        delivered repeatedly. Use this for triggers/commands to avoid re-triggering.
        """
        text = self.latest_text
        # clear after reading to avoid repeated triggers
        self.latest_text = ""
        return text

    def is_listening(self):
        """Return 1 when actively listening (after wake word), else 0."""
        return self.listening_flag

    def stop(self):
        """Stop background loop."""
        print("Stopping listener...")
        self.stop_flag = True

    def pause(self):
        """Pause listening."""
        print("Pausing listener...")
        self.paused = True

    def resume(self):
        """Resume listening."""
        print("Resuming listener...")
        self.paused = False
