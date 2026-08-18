"""Render app at OPPO phone logical size (411x914) and capture pages (QScreen.grabWindow)."""
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QGuiApplication, QFontDatabase
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterSingletonInstance
from PySide6.QtTest import QTest

from classmate.answer_engine import AnswerEngine
from classmate.bridge import ClassMateBridge
from classmate.config import AppConfig
from classmate.courses import CourseCatalog
from classmate.history_store import HistoryStore

OUT = ROOT / "docs" / "shots_phone"
OUT.mkdir(parents=True, exist_ok=True)

app = QGuiApplication.instance() or QGuiApplication([])
for n in ("msyh.ttc", "segoeui.ttf", "seguisym.ttf"):
    p = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / n
    if p.exists():
        QFontDatabase.addApplicationFont(str(p))

tmp = tempfile.mkdtemp(prefix="cm_phone_")
cfg = AppConfig(str(Path(tmp) / "config.json"))
cfg.set("userName", {"zh": "李小明", "en": "Xiao Ming", "yue": "李小明"})
catalog = CourseCatalog([ROOT / "data" / "courses_a.json", ROOT / "data" / "courses_b.json"], cfg)
store = HistoryStore(Path(tmp) / "hist.db")
bridge = ClassMateBridge(cfg, catalog, AnswerEngine(catalog, cfg), store, ROOT)
qmlRegisterSingletonInstance(ClassMateBridge, "ClassMate.Core", 1, 0, "Bridge", bridge)
engine = QQmlApplicationEngine()
engine.addImportPath(str(ROOT / "qml"))
engine.load(QUrl.fromLocalFile(str(ROOT / "qml" / "Main.qml")))
assert engine.rootObjects(), "QML load failed"
win = engine.rootObjects()[0]
win.setProperty("width", 411)
win.setProperty("height", 914)
QTest.qWait(500)
print("win:", win.property("width"), "x", win.property("height"))


def shot(name):
    pm = win.screen().grabWindow(0, win.x(), win.y(), win.width(), win.height())
    ok = not pm.isNull()
    pm.save(str(OUT / name))
    print("saved", name, "size", pm.size(), "ok", ok)


bridge.selectSubject("ic")
shot("01_listen.png")
bridge.injectUtterance("咩係標準預防措施？", "yue")
QTest.qWait(2500)
shot("02_popup.png")
bridge.demoCommand.emit("page:subjects")
QTest.qWait(600)
shot("03_subjects.png")
bridge.demoCommand.emit("page:history")
QTest.qWait(600)
shot("04_history.png")
bridge.demoCommand.emit("page:settings")
QTest.qWait(600)
shot("05_settings.png")
print("DONE")
