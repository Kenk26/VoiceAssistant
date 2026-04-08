"""
Voice Recognition Module
Handles microphone input and speech-to-text conversion.
"""

import speech_recognition as sr
import threading
from typing import Callable, Optional


class VoiceListener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self._calibrated = False

        # Adjust recognizer settings for better accuracy
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3

    def calibrate(self, status_callback: Optional[Callable] = None):
        """Calibrate microphone for ambient noise."""
        if status_callback:
            status_callback("Calibrating microphone for ambient noise...")
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
            self._calibrated = True
            if status_callback:
                status_callback("Microphone calibrated. Ready to listen!")
        except Exception as e:
            if status_callback:
                status_callback(f"Calibration warning: {e}. Using default settings.")

    def listen_once(
        self,
        on_result: Callable[[str], None],
        on_error: Callable[[str], None],
        on_status: Callable[[str], None]
    ):
        """Listen for a single voice command and return transcribed text."""
        def _listen():
            try:
                on_status("🎤 Listening... Speak now!")
                with self.microphone as source:
                    if not self._calibrated:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)

                on_status("🔄 Processing your voice...")

                # Try Google first, fallback options available
                text = self.recognizer.recognize_google(audio)
                on_result(text)

            except sr.WaitTimeoutError:
                on_error("No speech detected. Please try again.")
            except sr.UnknownValueError:
                on_error("Could not understand the audio. Please speak clearly.")
            except sr.RequestError as e:
                on_error(f"Speech recognition service error: {e}")
            except Exception as e:
                on_error(f"Unexpected error: {e}")

        thread = threading.Thread(target=_listen, daemon=True)
        thread.start()
        return thread

    def listen_continuous(
        self,
        on_result: Callable[[str], None],
        on_error: Callable[[str], None],
        on_status: Callable[[str], None],
        stop_event: threading.Event
    ):
        """Continuously listen for voice commands until stop_event is set."""
        def _listen_loop():
            on_status("🎤 Continuous listening mode active...")
            while not stop_event.is_set():
                try:
                    with self.microphone as source:
                        audio = self.recognizer.listen(
                            source, timeout=5, phrase_time_limit=15
                        )
                    text = self.recognizer.recognize_google(audio)
                    if text.strip():
                        on_result(text)
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    on_error(f"Service error: {e}")
                    break
                except Exception as e:
                    if not stop_event.is_set():
                        on_error(f"Error: {e}")
                    break

        thread = threading.Thread(target=_listen_loop, daemon=True)
        thread.start()
        return thread
