"""Run the scripted classroom demo headlessly and capture screenshots.

Usage: python tools/run_demo.py
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PySide6.QtCore import QTimer


def main():
    from run import build_app
    out = ROOT / "docs" / "shots_demo"
    app, win, bridge, tray, args = build_app(
        ["--demo", "--autoshot", str(out), "--config", str(ROOT / "models" / "demo_config.json")])
    QTimer.singleShot(41000, app.quit)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
