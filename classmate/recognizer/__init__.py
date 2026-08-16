"""Recognizer factory: auto-select engine per platform and availability."""
from __future__ import annotations
import sys

from .base import BaseRecognizer


def create_recognizer(cfg, on_transcript, on_level=None) -> BaseRecognizer:
    engine = cfg.get("recognitionEngine", "auto")
    primary = (cfg.get("languages") or ["yue"])[0]
    is_android = getattr(sys, "platform", "").startswith("android") or "ANDROID_ARGUMENT" in __import__("os").environ

    if engine == "mock":
        from .mock_recognizer import MockRecognizer
        return MockRecognizer(on_transcript, on_level, primary)

    if is_android:
        from .android_recognizer import AndroidRecognizer
        return AndroidRecognizer(on_transcript, on_level, primary)

    if engine == "vosk":
        from .vosk_recognizer import VoskRecognizer
        return VoskRecognizer(on_transcript, on_level, primary, model_paths=cfg.get("voskModels", {}))

    if engine == "google":
        from .google_recognizer import GoogleRecognizer
        return GoogleRecognizer(on_transcript, on_level, primary)

    # auto: vosk (offline, deterministic) preferred when models exist
    from .vosk_recognizer import VoskRecognizer
    if VoskRecognizer.available():
        paths = cfg.get("voskModels", {}) or {}
        if any(paths.values()):
            return VoskRecognizer(on_transcript, on_level, primary, model_paths=paths)
    from .google_recognizer import GoogleRecognizer
    if GoogleRecognizer.available():
        return GoogleRecognizer(on_transcript, on_level, primary)
    from .mock_recognizer import MockRecognizer
    return MockRecognizer(on_transcript, on_level, primary)


def autodetect_models(model_dir) -> dict:
    """Scan model_dir for vosk-model-* subdirectories → {lang: path}."""
    from pathlib import Path
    out: dict = {}
    d = Path(model_dir)
    if not d.is_dir():
        return out
    for child in sorted(d.iterdir()):
        if child.is_dir() and "vosk-model" in child.name:
            name = child.name.lower()
            if "yue" in name or "cantonese" in name:
                out["yue"] = str(child)
            elif "cn" in name or "zh" in name:
                out["zh"] = str(child)
            elif "en" in name:
                out["en"] = str(child)
    return out


def engine_status() -> dict:
    out = {"vosk": False, "google": False, "mock": True, "android": False}
    from .vosk_recognizer import VoskRecognizer
    from .google_recognizer import GoogleRecognizer
    from .android_recognizer import AndroidRecognizer
    out["vosk"] = VoskRecognizer.available()
    out["google"] = GoogleRecognizer.available()
    out["android"] = AndroidRecognizer.available()
    return out
