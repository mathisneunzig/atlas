from __future__ import annotations

from typing import Any

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from config import Settings


class SpotifyCapability:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.spotify: spotipy.Spotify | None = None

    def _get_client(self) -> spotipy.Spotify:
        if self.spotify is not None:
            return self.spotify

        self.settings.validate_spotify_config()

        auth_manager = SpotifyOAuth(
            client_id=self.settings.spotify_client_id,
            client_secret=self.settings.spotify_client_secret,
            redirect_uri=self.settings.spotify_redirect_uri,
            scope=(
                "user-read-playback-state "
                "user-modify-playback-state "
                "user-read-currently-playing"
            ),
            open_browser=True,
        )

        self.spotify = spotipy.Spotify(auth_manager=auth_manager)
        return self.spotify

    def _find_device_id(self, spotify: spotipy.Spotify) -> str | None:
        devices_response = spotify.devices()
        devices: list[dict[str, Any]] = devices_response.get("devices", [])

        if not devices:
            return None

        preferred_name = (self.settings.spotify_device_name or "").strip().lower()
        if preferred_name:
            for device in devices:
                if device.get("name", "").strip().lower() == preferred_name:
                    return device.get("id")

        active_device = next((d for d in devices if d.get("is_active")), None)
        if active_device:
            return active_device.get("id")

        return devices[0].get("id")

    def search_track(self, query: str) -> dict[str, str] | None:
        spotify = self._get_client()
        result = spotify.search(q=query, type="track", limit=1)

        items = result.get("tracks", {}).get("items", [])
        if not items:
            return None

        track = items[0]
        artists = ", ".join(artist["name"] for artist in track.get("artists", []))

        return {
            "name": track.get("name", "Unbekannt"),
            "artists": artists or "Unbekannt",
            "uri": track.get("uri", ""),
        }

    def play_track(self, query: str) -> str:
        spotify = self._get_client()
        track = self.search_track(query)

        if not track:
            return f"Ich konnte bei Spotify nichts zu {query} finden."

        device_id = self._find_device_id(spotify)
        if not device_id:
            return (
                "Ich habe kein aktives Spotify-Gerät gefunden. "
                "Öffne Spotify auf einem Gerät und versuche es erneut."
            )

        spotify.start_playback(device_id=device_id, uris=[track["uri"]])
        return f"Ich spiele jetzt {track['name']} von {track['artists']}."

    def pause(self) -> str:
        spotify = self._get_client()
        device_id = self._find_device_id(spotify)

        if not device_id:
            return "Ich habe kein Spotify-Gerät zum Pausieren gefunden."

        spotify.pause_playback(device_id=device_id)
        return "Spotify wurde pausiert."

    def resume(self) -> str:
        spotify = self._get_client()
        device_id = self._find_device_id(spotify)

        if not device_id:
            return "Ich habe kein Spotify-Gerät zum Fortsetzen gefunden."

        spotify.start_playback(device_id=device_id)
        return "Spotify läuft weiter."

    def next_track(self) -> str:
        spotify = self._get_client()
        device_id = self._find_device_id(spotify)

        if not device_id:
            return "Ich habe kein Spotify-Gerät gefunden."

        spotify.next_track(device_id=device_id)
        return "Ich habe zum nächsten Titel gewechselt."

    def current_playback(self) -> str:
        spotify = self._get_client()
        playback = spotify.current_playback()

        if not playback or not playback.get("item"):
            return "Aktuell läuft nichts auf Spotify."

        item = playback["item"]
        track_name = item.get("name", "Unbekannt")
        artists = ", ".join(a["name"] for a in item.get("artists", []))
        is_playing = playback.get("is_playing", False)

        if is_playing:
            return f"Gerade läuft {track_name} von {artists}."
        return f"Spotify ist pausiert. Zuletzt lief {track_name} von {artists}."