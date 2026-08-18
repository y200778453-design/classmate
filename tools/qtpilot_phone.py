"""Qtpilot launcher: start ClassMate at phone size (411x914), keep alive, quit."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PySide6.QtCore import QTimer
from run import build_app

app, win, bridge, tray, args = build_app([
    "--scale", "0.98",
    "--config", str(ROOT / "models" / "demo_config.json"),
])
win.setProperty("width", 411)
win.setProperty("height", 914)
QTimer.singleShot(60000, app.quit)
sys.exit(app.exec())
