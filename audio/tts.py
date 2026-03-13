from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path

import edge_tts

from config import Settings


class TextToSpeech:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def speak(self, text: str) -> None:
        cleaned = (text or "").strip()
        if not cleaned:
            return

        asyncio.run(self._speak_async(cleaned))

    async def _speak_async(self, text: str) -> None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            temp_path = Path(tmp_file.name)

        try:
            communicator = edge_tts.Communicate(
                text=text,
                voice=self.settings.voice_name,
            )
            await communicator.save(str(temp_path))
            self._play_file(temp_path)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def _play_file(self, file_path: Path) -> None:
        if os.name == "nt":
            os.system(f'start /min wmplayer "{file_path}" /play /close')
            return

        if os.system("which afplay > /dev/null 2>&1") == 0:
            os.system(f'afplay "{file_path}"')
            return

        if os.system("which ffplay > /dev/null 2>&1") == 0:
            os.system(f'ffplay -nodisp -autoexit -loglevel quiet "{file_path}"')
            return

        raise RuntimeError(
            "Kein Audio-Player gefunden. Installiere ffplay oder nutze macOS mit afplay."
        )