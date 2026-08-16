import os, sys
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from pathlib import Path
ROOT = Path("E:/AI/classmate")
sys.path.insert(0, str(ROOT))
from PySide6.QtCore import QTimer
from run import build_app
out = ROOT / "models" / "_shotdbg"
app, win, bridge, tray, args = build_app(["--autoshot", str(out), "--config", str(ROOT/"models"/"demo_config.json")])
print("screen:", win.screen() is not None, "geo:", win.x(), win.y(), win.width(), win.height())
def grabonce():
    try:
        pm = win.screen().grabWindow(0, win.x(), win.y(), win.width(), win.height())
        print("grab:", pm.isNull(), pm.size())
        if not pm.isNull():
            pm.save(str(out / "manual.png"))
    except Exception as e:
        print("grab err:", e)
QTimer.singleShot(2000, grabonce)
QTimer.singleShot(6500, app.quit)
sys.exit(app.exec())
