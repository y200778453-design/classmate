"""Recognizer base class."""
from __future__ import annotations


class BaseRecognizer:
    name = "base"

    def __init__(self, on_transcript, on_level=None, primary_lang="zh"):
        self.on_transcript = on_transcript
        self.on_level = on_level
        self.primary_lang = primary_lang

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def feed(self, audio_bytes: bytes):
        """Push raw 16kHz mono int16 PCM for streaming recognizers."""

    def needs_audio(self) -> bool:
        return True

    def close(self):
        pass
