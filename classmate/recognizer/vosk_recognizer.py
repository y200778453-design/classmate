"""Offline vosk streaming recognizer (zh / en models)."""
from __future__ import annotations
import json

from .base import BaseRecognizer

_LANG_HINT = {"zh": "zh", "cn": "zh", "en": "en", "yue": "zh"}


class VoskRecognizer(BaseRecognizer):
    name = "vosk"

    def __init__(self, on_transcript, on_level=None, primary_lang="zh", model_paths=None):
        super().__init__(on_transcript, on_level, primary_lang)
        self.model_paths = model_paths or {}
        self._models = {}
        self._recs = {}

    @staticmethod
    def available() -> bool:
        try:
            import vosk  # noqa: F401
            return True
        except Exception:
            return False

    def start(self):
        import vosk
        loaded = 0
        for lang, path in self.model_paths.items():
            if not path:
                continue
            try:
                model = vosk.Model(str(path))
                self._models[lang] = model
                self._recs[lang] = vosk.KaldiRecognizer(model, 16000)
                loaded += 1
            except Exception:
                continue
        return loaded > 0

    def feed(self, audio_bytes: bytes):
        for lang, rec in list(self._recs.items()):
            if rec.AcceptWaveform(audio_bytes):
                res = json.loads(rec.Result())
                text = (res.get("text") or "").strip()
                if text:
                    self.on_transcript(text, lang, 0.9)
            else:
                partial = json.loads(rec.PartialResult()).get("partial", "").strip()
                if partial and self.on_level is not None:
                    pass  # partial results only update level; keep transcript final-only

    def stop(self):
        for rec in self._recs.values():
            try:
                final = json.loads(rec.FinalResult()).get("text", "").strip()
                if final:
                    lang = [k for k, v in self._recs.items() if v is rec][0]
                    self.on_transcript(final, lang, 0.9)
            except Exception:
                pass
        self._recs.clear()
        self._models.clear()
