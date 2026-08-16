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

app = QGuiApplication.instance() or QGuiApplication([])
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
QTest.qWait(500)
bridge.selectSubject("ic")
bridge.injectUtterance("咩係標準預防措施？", "yue")
QTest.qWait(500)
print("model rows:", bridge.historyModel.rowCount(), "store:", store.count())
bridge.demoCommand.emit("page:history")
QTest.qWait(600)
hist = win.findChild(object, "historyList")
print("hist found:", hist is not None, "count:", hist.property("count") if hist else None)
print("stack depth:", win.findChild(object, "pageStack").property("depth"))
