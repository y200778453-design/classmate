"""Online Google STT recognizer (Cantonese zh-HK / Mandarin zh-CN / English en-US).

Uses the free SpeechRecognition endpoint; requires network access.
"""
from __future__ import annotations
import threading
import time

from .base import BaseRecognizer

_LANG_MAP = {"yue": "zh-HK", "zh": "zh-CN", "en": "en-US"}
GAP_SECONDS = 1.1  # silence gap that closes one utterance


class GoogleRecognizer(BaseRecognizer):
    name = "google"

    def __init__(self, on_transcript, on_level=None, primary_lang="yue"):
        super().__init__(on_transcript, on_level, primary_lang)
        self._buf = bytearray()
        self._last_sound = time.monotonic()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

    @staticmethod
    def available() -> bool:
        try:
            import speech_recognition  # noqa: F401
            return True
        except Exception:
            return False

    def start(self):
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        import speech_recognition as sr
        while not self._stop.is_set():
            with self._lock:
                if len(self._buf) > 16000 and time.monotonic() - self._last_sound > GAP_SECONDS:
                    chunk = bytes(self._buf)
                    self._buf = bytearray()
                else:
                    chunk = None
            if chunk is None:
                time.sleep(0.15)
                continue
            audio = sr.AudioData(chunk, 16000, 2)
            for lang in ("yue", "zh", "en"):
                try:
                    text = sr.Recognizer().recognize_google(audio, language=_LANG_MAP[lang],
                                                            show_all=False)
                    if text and text.strip():
                        self.on_transcript(text.strip(), lang, 0.85)
                        break
                except Exception:
                    continue

    def feed(self, audio_bytes: bytes):
        if not audio_bytes:
            return
        with self._lock:
            self._buf.extend(audio_bytes)
        if any(b != 0 for b in audio_bytes[:200]):
            self._last_sound = time.monotonic()

    def stop(self):
        self._stop.set()
