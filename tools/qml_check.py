"""Load Main.qml and print all QML warnings/errors."""
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from classmate.answer_engine import AnswerEngine
from classmate.bridge import ClassMateBridge
from classmate.config import AppConfig
from classmate.courses import CourseCatalog
from classmate.history_store import HistoryStore

app = QGuiApplication([])
cfg = AppConfig(str(ROOT / "models" / "dbg_cfg.json"))
catalog = CourseCatalog([ROOT / "data" / "courses_a.json", ROOT / "data" / "courses_b.json"], cfg)
store = HistoryStore(ROOT / "models" / "dbg_hist.db")
bridge = ClassMateBridge(cfg, catalog, AnswerEngine(catalog, cfg), store, ROOT)

engine = QQmlApplicationEngine()
errors = []
engine.warnings.connect(lambda ws: errors.extend(str(ws).splitlines()))
engine.addImportPath(str(ROOT / "qml"))
engine.rootContext().setContextProperty("Bridge", bridge)

from PySide6.QtQml import qmlRegisterSingletonInstance
qmlRegisterSingletonInstance(ClassMateBridge, "ClassMate.Core", 1, 0, "Bridge", bridge)

engine.load(QUrl.fromLocalFile(str(ROOT / "qml" / "Main.qml")))
print("objects:", len(engine.rootObjects()))
for e in errors:
    print("WARN:", e)
