"""
Text-to-Speech Module
Converts agent text responses back to spoken audio.
"""

import threading
from typing import Optional


class TextToSpeech:
    def __init__(self):
        self._engine = None
        self._available = False
        self._speaking = False
        self._init_engine()

    def _init_engine(self):
        """Initialize pyttsx3 TTS engine."""
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", 175)   # Speed
            self._engine.setProperty("volume", 0.9)  # Volume

            # Try to set a pleasant voice
            voices = self._engine.getProperty("voices")
            if voices:
                # Prefer female voices if available
                for voice in voices:
                    if "female" in voice.name.lower() or "zira" in voice.id.lower():
                        self._engine.setProperty("voice", voice.id)
                        break

            self._available = True
        except ImportError:
            self._available = False
        except Exception:
            self._available = False

    @property
    def is_available(self) -> bool:
        return self._available

    @property
    def is_speaking(self) -> bool:
        return self._speaking

    def speak(self, text: str, on_done: Optional[callable] = None):
        """Speak the given text asynchronously."""
        if not self._available or not text.strip():
            if on_done:
                on_done()
            return

        def _speak():
            self._speaking = True
            try:
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception:
                pass
            finally:
                self._speaking = False
                if on_done:
                    on_done()

        thread = threading.Thread(target=_speak, daemon=True)
        thread.start()

    def stop(self):
        """Stop current speech."""
        if self._available and self._speaking:
            try:
                self._engine.stop()
            except Exception:
                pass
            self._speaking = False

    def set_rate(self, rate: int):
        """Set speech rate (default ~175 wpm)."""
        if self._available:
            self._engine.setProperty("rate", rate)

    def set_volume(self, volume: float):
        """Set volume 0.0 to 1.0."""
        if self._available:
            self._engine.setProperty("volume", volume)
