import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import sys, tempfile
from pathlib import Path
ROOT = Path("E:/AI/classmate")
sys.path.insert(0, str(ROOT))
from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication, QFontDatabase
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterSingletonInstance
from PySide6.QtTest import QTest
import shiboken6

app = QGuiApplication.instance() or QGuiApplication([])
for n in ("msyh.ttc", "segoeui.ttf", "seguisym.ttf"):
    p = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / n
    if p.exists():
        QFontDatabase.addApplicationFont(str(p))
from classmate.answer_engine import AnswerEngine
from classmate.bridge import ClassMateBridge
from classmate.config import AppConfig
from classmate.courses import CourseCatalog
from classmate.history_store import HistoryStore

tmp = tempfile.mkdtemp(prefix="cm_dbg_")
cfg = AppConfig(str(Path(tmp) / "config.json"))
cfg.set("userName", {"zh": "李小明", "en": "Xiao Ming", "yue": "李小明"})
catalog = CourseCatalog([ROOT / "data" / "courses_a.json", ROOT / "data" / "courses_b.json"], cfg)
store = HistoryStore(Path(tmp) / "hist.db")
bridge = ClassMateBridge(cfg, catalog, AnswerEngine(catalog, cfg), store, ROOT)
qmlRegisterSingletonInstance(ClassMateBridge, "ClassMate.Core", 1, 0, "Bridge", bridge)
engine = QQmlApplicationEngine()
engine.addImportPath(str(ROOT / "qml"))
engine.load(QUrl.fromLocalFile(str(ROOT / "qml" / "Main.qml")))
win = engine.rootObjects()[0]
QTest.qWait(600)
bridge.selectSubject("ic")
bridge.injectUtterance("李小明，你嚟答下MRSA要點樣隔離？", "yue")
QTest.qWait(3000)
popup = win.findChild(object, "alertPopup")
card = win.findChild(object, "alertCard")
answer = win.findChild(object, "alertAnswerText")
badge = win.findChild(object, "alertBadge")
print("popup visible:", popup.property("visible") if popup else None)
print("card geo:", card.property("x"), card.property("y"), card.property("width"), card.property("height") if card else None)
if answer:
    print("answer text len:", len(answer.property("text") or ""))
    print("answer geo:", answer.property("x"), answer.property("y"), answer.property("width"), answer.property("height"))
    print("answer visible:", answer.property("visible"), "opacity:", answer.property("opacity"))
    print("answer clip-parent-visible:", answer.parent() is not None, answer.parent().property("width") if answer.parent() else None)
print("badge text:", badge.property("text") if badge else None)
