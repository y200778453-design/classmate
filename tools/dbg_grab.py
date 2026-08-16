import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import sys, tempfile
from pathlib import Path
ROOT = Path("E:/AI/classmate")
sys.path.insert(0, str(ROOT))
from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterSingletonInstance
from PySide6.QtTest import QTest
from classmate.answer_engine import AnswerEngine
from classmate.bridge import ClassMateBridge
from classmate.config import AppConfig
from classmate.courses import CourseCatalog
from classmate.history_store import HistoryStore
import shiboken6

app = QGuiApplication.instance() or QGuiApplication([])
tmp = tempfile.mkdtemp(prefix="cm_dbg_")
cfg = AppConfig(str(Path(tmp) / "config.json"))
catalog = CourseCatalog([ROOT / "data" / "courses_a.json", ROOT / "data" / "courses_b.json"], cfg)
store = HistoryStore(Path(tmp) / "hist.db")
bridge = ClassMateBridge(cfg, catalog, AnswerEngine(catalog, cfg), store, ROOT)
qmlRegisterSingletonInstance(ClassMateBridge, "ClassMate.Core", 1, 0, "Bridge", bridge)
engine = QQmlApplicationEngine()
engine.addImportPath(str(ROOT / "qml"))
engine.load(QUrl.fromLocalFile(str(ROOT / "qml" / "Main.qml")))
win = engine.rootObjects()[0]
QTest.qWait(800)
print("pytype:", type(win))
print("class:", win.metaObject().className())
print("is QQuickWindow:", isinstance(win, __import__("PySide6.QtQuick", fromlist=["QQuickWindow"]).QQuickWindow))
ptr = shiboken6.getCppPointer(win)
print("cpp ptr ok:", bool(ptr and ptr[0]))
# QScreen grab test
scr = win.screen()
print("screen:", scr is not None, scr.name() if scr else None)
if scr:
    pm = scr.grabWindow(0)
    print("screen grab:", pm.isNull(), pm.size())
    pm.save(str(ROOT / "docs" / "shots" / "_probe_screen.png"))
# contentItem via QQuickWindow cast from Qml
try:
    from PySide6.QtQuick import QQuickWindow
    qw = shiboken6.wrapInstance(ptr[0], QQuickWindow)
    print("wrapped type:", type(qw))
    print("has grabWindow:", hasattr(qw, "grabWindow"))
    if hasattr(qw, "grabWindow"):
        img = qw.grabWindow()
        print("grab:", img.isNull(), img.size())
        img.save(str(ROOT / "docs" / "shots" / "_probe_grab.png"))
except Exception as e:
    print("wrap err:", e)
