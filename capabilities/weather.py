from __future__ import annotations

import python_weather

from config import Settings


class WeatherCapability:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def get_weather_report(self, city: str | None = None) -> str:
        target_city = (city or self.settings.default_city).strip()

        async with python_weather.Client(unit=python_weather.METRIC) as client:
            weather = await client.get(target_city)

        temperature = weather.temperature
        description = weather.description or "unbekannt"
        feels_like = getattr(weather, "feels_like", None)
        humidity = getattr(weather, "humidity", None)

        parts = [
            f"Das aktuelle Wetter in {target_city} ist {description}.",
            f"Die Temperatur liegt bei {temperature} Grad.",
        ]

        if feels_like is not None:
            parts.append(f"Gefühlt sind es {feels_like} Grad.")

        if humidity is not None:
            parts.append(f"Die Luftfeuchtigkeit beträgt {humidity} Prozent.")

        return " ".join(parts)