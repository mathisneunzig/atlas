from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(slots=True)
class RouteResult:
    capability: str
    action: str
    payload: dict


class CommandRouter:
    def route(self, command: str) -> RouteResult:
        text = command.strip().lower()

        weather_result = self._route_weather(text)
        if weather_result:
            return weather_result

        wiki_result = self._route_wikipedia(text)
        if wiki_result:
            return wiki_result

        spotify_result = self._route_spotify(text)
        if spotify_result:
            return spotify_result

        tapo_result = self._route_tapo(text)
        if tapo_result:
            return tapo_result

        return RouteResult(
            capability="fallback",
            action="unknown",
            payload={"original_text": command},
        )

    def _route_weather(self, text: str) -> RouteResult | None:
        if "wetter" not in text:
            return None

        city = None
        match = re.search(r"(?:in|für)\s+([a-zäöüß\s\-]+)$", text)
        if match:
            city = match.group(1).strip()

        return RouteResult(
            capability="weather",
            action="current_weather",
            payload={"city": city},
        )

    def _route_wikipedia(self, text: str) -> RouteResult | None:
        triggers = ["wikipedia", "wiki", "wer ist", "was ist", "erzähl mir etwas über"]
        if not any(trigger in text for trigger in triggers):
            return None

        topic = text
        replacements = [
            "wikipedia",
            "wiki",
            "wer ist",
            "was ist",
            "erzähl mir etwas über",
        ]
        for value in replacements:
            topic = topic.replace(value, "")

        topic = topic.strip()
        if not topic:
            return None

        return RouteResult(
            capability="wiki",
            action="summary",
            payload={"topic": topic},
        )

    def _route_spotify(self, text: str) -> RouteResult | None:
        if "spotify" in text and "pause" in text:
            return RouteResult(
                capability="spotify",
                action="pause",
                payload={},
            )

        if "spotify" in text and ("weiter" in text or "fortsetzen" in text):
            return RouteResult(
                capability="spotify",
                action="resume",
                payload={},
            )

        if "spotify" in text and ("nächster" in text or "weiteres lied" in text or "skip" in text):
            return RouteResult(
                capability="spotify",
                action="next",
                payload={},
            )

        if "spotify" in text and ("was läuft" in text or "aktueller song" in text):
            return RouteResult(
                capability="spotify",
                action="current",
                payload={},
            )

        play_match = re.search(r"(?:spiele|play)\s+(.+?)(?:\s+auf spotify|\s*$)", text)
        if play_match:
            query = play_match.group(1).strip()
            return RouteResult(
                capability="spotify",
                action="play",
                payload={"query": query},
            )

        return None

    def _route_tapo(self, text: str) -> RouteResult | None:
        turn_on_match = re.search(
            r"(?:schalte|mache)\s+(.+?)\s+(?:an|ein)$",
            text,
        )
        if turn_on_match:
            device_name = turn_on_match.group(1).strip()
            return RouteResult(
                capability="tapo",
                action="turn_on",
                payload={"device_name": device_name},
            )

        turn_off_match = re.search(
            r"(?:schalte|mache)\s+(.+?)\s+(?:aus)$",
            text,
        )
        if turn_off_match:
            device_name = turn_off_match.group(1).strip()
            return RouteResult(
                capability="tapo",
                action="turn_off",
                payload={"device_name": device_name},
            )

        status_match = re.search(
            r"(?:status von|wie ist der status von)\s+(.+)$",
            text,
        )
        if status_match:
            device_name = status_match.group(1).strip()
            return RouteResult(
                capability="tapo",
                action="status",
                payload={"device_name": device_name},
            )

        return None