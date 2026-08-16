"""Qtpilot launcher: start ClassMate demo, keep alive ~45s, then quit."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PySide6.QtCore import QTimer
from run import build_app

app, win, bridge, tray, args = build_app([
    "--demo",
    "--config", str(ROOT / "models" / "demo_config.json"),
])
QTimer.singleShot(46000, app.quit)
sys.exit(app.exec())
