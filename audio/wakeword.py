from __future__ import annotations
import time
import wave
from pathlib import Path
import numpy as np
import pyaudio
from openwakeword.model import Model
from config import Settings

class WakeWordListener:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.model = Model(inference_framework="tflite")
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.last_detection_time = 0.0
        self.cooldown_seconds = 2.0

    def start(self) -> None:
        if self.stream is not None:
            return

        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.settings.sample_rate,
            input=True,
            frames_per_buffer=self.settings.chunk_size,
        )

    def wait_for_wakeword(self) -> bool:
        if self.stream is None:
            self.start()

        print(f"Listening for wakeword '{self.settings.wakeword_name}' ...")

        while True:
            audio_bytes = self.stream.read(
                self.settings.chunk_size,
                exception_on_overflow=False,
            )
            audio_data = np.frombuffer(audio_bytes, dtype=np.int16)
            prediction = self.model.predict(audio_data)

            score = prediction.get(self.settings.wakeword_name, 0.0)
            if score >= self.settings.wakeword_threshold:
                now = time.time()
                if now - self.last_detection_time >= self.cooldown_seconds:
                    self.last_detection_time = now
                    print(
                        f"Wakeword detected: {self.settings.wakeword_name} "
                        f"(score={score:.2f})"
                    )
                    self._flush_buffer()
                    self._play_activation_sound()
                    return True

    def _flush_buffer(self) -> None:
        if self.stream is None:
            return

        while self.stream.get_read_available() > 0:
            self.stream.read(
                self.settings.chunk_size,
                exception_on_overflow=False,
            )

    def _play_activation_sound(self) -> None:
        if not self.settings.activation_sound_path:
            return

        file_path = Path(self.settings.activation_sound_path)
        if not file_path.exists():
            print(f"Activation sound not found: {file_path}")
            return

        try:
            with wave.open(str(file_path), "rb") as wav_file:
                output = self.audio.open(
                    format=self.audio.get_format_from_width(wav_file.getsampwidth()),
                    channels=wav_file.getnchannels(),
                    rate=wav_file.getframerate(),
                    output=True,
                )

                chunk = 1024
                data = wav_file.readframes(chunk)
                while data:
                    output.write(data)
                    data = wav_file.readframes(chunk)

                output.stop_stream()
                output.close()
        except Exception as exc:
            print(f"Could not play activation sound: {exc}")

    def close(self) -> None:
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        self.audio.terminate()