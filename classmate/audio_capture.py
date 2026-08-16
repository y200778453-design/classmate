"""Microphone capture via sounddevice (optional dependency)."""
from __future__ import annotations
import queue
import threading

import numpy as np

SAMPLE_RATE = 16000


class AudioCapture:
    def __init__(self, on_level=None):
        self.on_level = on_level
        self._queue: queue.Queue = queue.Queue(maxsize=400)
        self._stream = None
        self._thread: threading.Thread | None = None
        self.running = False
        self.available = True
        self.last_error = ""

    def start(self):
        try:
            import sounddevice as sd
        except Exception as exc:  # pragma: no cover
            self.available = False
            self.last_error = f"sounddevice 未安裝: {exc}"
            return False
        try:
            self._stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1,
                                          dtype="int16", blocksize=3200,
                                          callback=self._callback)
            self._stream.start()
            self.running = True
            return True
        except Exception as exc:
            self.available = False
            self.last_error = f"無法開啟麥克風: {exc}"
            return False

    def _callback(self, indata, frames, time_info, status):
        if self.on_level:
            rms = float(np.sqrt(np.mean(np.square(indata.astype(np.float32) / 32768.0))))
            self.on_level(min(1.0, rms * 4.0))
        try:
            self._queue.put_nowait(indata.tobytes())
        except queue.Full:
            try:
                self._queue.get_nowait()
                self._queue.put_nowait(indata.tobytes())
            except Exception:
                pass

    def read(self, timeout: float = 0.5) -> bytes | None:
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def stop(self):
        self.running = False
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None
