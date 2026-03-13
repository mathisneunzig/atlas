from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(slots=True)
class Settings:
    assistant_name: str
    language: str
    voice_name: str
    wakeword_name: str
    wakeword_threshold: float
    sample_rate: int
    chunk_size: int
    activation_sound_path: str | None
    default_city: str
    spotify_client_id: str | None
    spotify_client_secret: str | None
    spotify_redirect_uri: str | None
    spotify_device_name: str | None

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            assistant_name=os.getenv("ASSISTANT_NAME", "Homelab"),
            language=os.getenv("ASSISTANT_LANGUAGE", "de-DE"),
            voice_name=os.getenv("VOICE_NAME", "de-DE-KatjaNeural"),
            wakeword_name=os.getenv("WAKEWORD_NAME", "hey_jarvis"),
            wakeword_threshold=float(os.getenv("WAKEWORD_THRESHOLD", "0.6")),
            sample_rate=int(os.getenv("AUDIO_SAMPLE_RATE", "16000")),
            chunk_size=int(os.getenv("AUDIO_CHUNK_SIZE", "1280")),
            activation_sound_path=os.getenv("ACTIVATION_SOUND_PATH"),
            default_city=os.getenv("CITY_NAME", "Heidelberg"),
            spotify_client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            spotify_client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            spotify_redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
            spotify_device_name=os.getenv("SPOTIFY_DEVICE_NAME"),
        )

    def validate_base_config(self) -> None:
        if not self.wakeword_name.strip():
            raise ValueError("WAKEWORD_NAME darf nicht leer sein.")

        if self.wakeword_threshold <= 0 or self.wakeword_threshold > 1:
            raise ValueError("WAKEWORD_THRESHOLD muss zwischen 0 und 1 liegen.")

        if self.sample_rate <= 0:
            raise ValueError("AUDIO_SAMPLE_RATE muss größer als 0 sein.")

        if self.chunk_size <= 0:
            raise ValueError("AUDIO_CHUNK_SIZE muss größer als 0 sein.")

    def validate_spotify_config(self) -> None:
        missing = []
        if not self.spotify_client_id:
            missing.append("SPOTIFY_CLIENT_ID")
        if not self.spotify_client_secret:
            missing.append("SPOTIFY_CLIENT_SECRET")
        if not self.spotify_redirect_uri:
            missing.append("SPOTIFY_REDIRECT_URI")

        if missing:
            raise ValueError(
                "Spotify ist nicht vollständig konfiguriert. "
                f"Fehlende Variablen: {', '.join(missing)}"
            )