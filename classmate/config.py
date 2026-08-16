"""Persistent user configuration (JSON, thread-safe)."""
from __future__ import annotations
import json
import threading
from pathlib import Path

DEFAULTS: dict = {
    "userName": {"zh": "", "en": "", "yue": ""},
    "currentSubjectId": "ic",
    "sensitivity": 55,
    "answerMode": "concise",       # concise | deep
    "languages": ["yue", "zh", "en"],
    "recognitionEngine": "auto",   # auto | vosk | google | mock
    "modelDir": "",
    "voskModels": {"zh": "", "en": "", "yue": ""},
    "apiEnabled": False,
    "apiBase": "https://api.openai.com/v1",
    "apiKey": "",
    "apiModel": "gpt-4o-mini",
    "historyLimit": 500,
    "backgroundTray": True,
}


class AppConfig:
    def __init__(self, path: str | None = None):
        self.path = Path(path) if path else Path.home() / ".classmate" / "config.json"
        self._lock = threading.RLock()
        self.data: dict = {}
        self.reload()

    def reload(self):
        with self._lock:
            data = dict(DEFAULTS)
            try:
                if self.path.exists():
                    loaded = json.loads(self.path.read_text(encoding="utf-8"))
                    if isinstance(loaded, dict):
                        data.update(loaded)
            except Exception:
                pass
            self.data = data

    def get(self, key: str, default=None):
        with self._lock:
            return self.data.get(key, default)

    def set(self, key: str, value) -> None:
        with self._lock:
            self.data[key] = value
            try:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                tmp = self.path.with_suffix(".tmp")
                tmp.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
                tmp.replace(self.path)
            except Exception:
                pass

    def update(self, values: dict) -> None:
        with self._lock:
            self.data.update(values)
            self.set("_noop", None)  # reuse persistence path
