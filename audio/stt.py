from __future__ import annotations
import speech_recognition as sr

class SpeechToText:
    def __init__(
        self,
        language: str = "de-DE",
        energy_threshold: int = 300,
        pause_threshold: float = 0.8,
    ) -> None:
        self.language = language
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.pause_threshold = pause_threshold

    def listen_once(
        self,
        timeout: float = 5.0,
        phrase_time_limit: float = 8.0,
    ) -> str | None:
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.6)
            print("Listening for command...")
            audio = self.recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit,
            )

        try:
            text = self.recognizer.recognize_google(audio, language=self.language)
            text = text.strip()
            print(f"Recognized: {text}")
            return text.lower()
        except sr.UnknownValueError:
            print("Could not understand the audio.")
            return None
        except sr.RequestError as exc:
            print(f"Speech recognition service error: {exc}")
            return None