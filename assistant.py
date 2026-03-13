from __future__ import annotations

import asyncio

from config import Settings
from audio.stt import SpeechToText
from audio.tts import TextToSpeech
from audio.wakeword import WakeWordListener
from capabilities.spotify import SpotifyCapability
from capabilities.weather import WeatherCapability
from capabilities.wiki import WikipediaCapability
from router import CommandRouter, RouteResult


class HomeLabAssistant:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.settings.validate_base_config()

        self.tts = TextToSpeech(settings)
        self.stt = SpeechToText(language=settings.language)
        self.wakeword = WakeWordListener(settings)
        self.router = CommandRouter()

        self.weather = WeatherCapability(settings)
        self.wiki = WikipediaCapability(language="de")
        self.spotify = SpotifyCapability(settings)

    def run_forever(self) -> None:
        self.tts.speak(f"{self.settings.assistant_name} ist bereit.")

        try:
            while True:
                detected = self.wakeword.wait_for_wakeword()
                if not detected:
                    continue

                self.tts.speak("Ja?")
                command = self.stt.listen_once()

                if not command:
                    self.tts.speak("Ich habe nichts verstanden.")
                    continue

                print(f"Command: {command}")
                response = self.handle_command(command)
                print(f"Response: {response}")
                self.tts.speak(response)
        except KeyboardInterrupt:
            print("Shutting down assistant...")
        finally:
            self.shutdown()

    def handle_command(self, command: str) -> str:
        route = self.router.route(command)

        try:
            return self._dispatch(route)
        except Exception as exc:
            print(f"Error while handling command: {exc}")
            return f"Bei der Verarbeitung ist ein Fehler aufgetreten: {exc}"

    def _dispatch(self, route: RouteResult) -> str:
        if route.capability == "weather":
            city = route.payload.get("city")
            return asyncio.run(self.weather.get_weather_report(city))

        if route.capability == "wiki":
            topic = route.payload["topic"]
            return self.wiki.get_summary(topic)

        if route.capability == "spotify":
            if route.action == "play":
                return self.spotify.play_track(route.payload["query"])
            if route.action == "pause":
                return self.spotify.pause()
            if route.action == "resume":
                return self.spotify.resume()
            if route.action == "next":
                return self.spotify.next_track()
            if route.action == "current":
                return self.spotify.current_playback()

        if route.capability == "tapo":
            device_name = route.payload["device_name"]

            if route.action == "turn_on":
                return self.tapo.turn_on(device_name)
            if route.action == "turn_off":
                return self.tapo.turn_off(device_name)
            if route.action == "status":
                return self.tapo.get_status(device_name)

        return (
            "Dafür habe ich aktuell noch keine passende Capability. "
            "Aktuell unterstütze ich Wetter, Spotify und Wikipedia."
        )

    def shutdown(self) -> None:
        self.wakeword.close()