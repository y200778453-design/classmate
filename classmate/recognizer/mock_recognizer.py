"""Deterministic mock recognizer for tests / demos / offline rehearsal."""
from __future__ import annotations
import threading
import time

from .base import BaseRecognizer


class MockRecognizer(BaseRecognizer):
    name = "mock"

    def __init__(self, on_transcript, on_level=None, primary_lang="zh", script=None):
        super().__init__(on_transcript, on_level, primary_lang)
        self.script = list(script or [])
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self.pending = 0

    def schedule(self, utterances: list):
        """utterances: list of (text, lang) or (text, lang, delay_seconds)."""
        for u in utterances:
            item = list(u) + [2.0] if len(u) == 2 else list(u)
            self.script.append(tuple(item))

    def start(self):
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        for text, lang, delay in self.script:
            if self._stop.is_set():
                return
            time.sleep(delay)
            if self._stop.is_set():
                return
            self.pending += 1
            try:
                self.on_transcript(text, lang, 0.99)
            except Exception:
                pass

    def stop(self):
        self._stop.set()

    def needs_audio(self) -> bool:
        return False
