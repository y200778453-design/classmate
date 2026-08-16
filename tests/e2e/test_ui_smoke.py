"""Offscreen UI smoke test: load QML, drive pipeline, assert popup and history UI."""
import os
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

ROOT = Path(__file__).resolve().parents[2]
SHOTS = ROOT / "docs" / "shots"


@pytest.fixture(scope="module")
def ui():
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterSingletonInstance

    from classmate.answer_engine import AnswerEngine
    from classmate.bridge import ClassMateBridge
    from classmate.config import AppConfig
    from classmate.courses import CourseCatalog
    from classmate.history_store import HistoryStore

    app = QGuiApplication.instance() or QGuiApplication([])
    import sys as _sys
    from PySide6.QtGui import QFontDatabase
    if _sys.platform.startswith("win"):
        for _n in ("msyh.ttc", "segoeui.ttf", "seguisym.ttf"):
            _p = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / _n
            if _p.exists():
                QFontDatabase.addApplicationFont(str(_p))
    tmp = tempfile.mkdtemp(prefix="cm_ui_")
    cfg = AppConfig(str(Path(tmp) / "config.json"))
    cfg.set("userName", {"zh": "李小明", "en": "Xiao Ming", "yue": "李小明"})
    catalog = CourseCatalog(
        [ROOT / "data" / "courses_a.json", ROOT / "data" / "courses_b.json"], cfg)
    store = HistoryStore(Path(tmp) / "hist.db")
    bridge = ClassMateBridge(cfg, catalog, AnswerEngine(catalog, cfg), store, ROOT)

    qmlRegisterSingletonInstance(ClassMateBridge, "ClassMate.Core", 1, 0, "Bridge", bridge)
    engine = QQmlApplicationEngine()
    engine.addImportPath(str(ROOT / "qml"))
    engine.load(QUrl.fromLocalFile(str(ROOT / "qml" / "Main.qml")))
    assert engine.rootObjects(), "QML failed to load"
    win = engine.rootObjects()[0]
    yield app, win, bridge
    bridge.close()


def _find(root, name):
    return root.findChild(object, name)


def _shot(win, name):
    SHOTS.mkdir(parents=True, exist_ok=True)
    pm = win.screen().grabWindow(0, win.x(), win.y(), win.width(), win.height())
    assert not pm.isNull()
    pm.save(str(SHOTS / name))
    return pm


class TestUiSmoke:
    def test_window_and_pages_loaded(self, ui):
        from PySide6.QtTest import QTest
        app, win, bridge = ui
        QTest.qWait(400)
        assert win.width() > 0 and win.height() > 0
        assert _find(win, "pageStack") is not None
        assert _find(win, "mainStartButton") is not None

    def test_question_popup_with_answer(self, ui):
        from PySide6.QtTest import QTest
        app, win, bridge = ui
        QTest.qWait(400)
        bridge.selectSubject("ic")
        bridge.injectUtterance("咩係標準預防措施？", "yue")
        QTest.qWait(700)
        popup = _find(win, "alertPopup")
        assert popup is not None
        assert popup.property("visible"), "popup should be visible after question"
        badge = _find(win, "alertBadge")
        assert "提問" in badge.property("text")
        QTest.qWait(2600)  # typewriter reveal
        answer = _find(win, "alertAnswerText")
        assert "標準預防措施" in answer.property("text"), f"answer text: {answer.property('text')}"
        _shot(win, "e2e_popup_question.png")

    def test_name_call_urgent_popup(self, ui):
        from PySide6.QtTest import QTest
        app, win, bridge = ui
        bridge.injectUtterance("李小明，你嚟答下MRSA要點樣隔離？", "yue")
        QTest.qWait(800)
        popup = _find(win, "alertPopup")
        assert popup.property("visible")
        badge = _find(win, "alertBadge")
        assert "點名" in badge.property("text")
        QTest.qWait(2600)
        answer = _find(win, "alertAnswerText")
        assert "MRSA" in answer.property("text")
        _shot(win, "e2e_popup_name.png")

    def test_history_and_pages(self, ui):
        from PySide6.QtTest import QTest
        app, win, bridge = ui
        bridge.demoCommand.emit("page:history")
        QTest.qWait(500)
        hist = _find(win, "historyList")
        assert hist is not None
        assert hist.property("count") >= 2, f"history rows: {hist.property('count')}"
        _shot(win, "e2e_history.png")

        bridge.demoCommand.emit("page:subjects")
        QTest.qWait(500)
        _shot(win, "e2e_subjects.png")

        bridge.demoCommand.emit("page:settings")
        QTest.qWait(500)
        _shot(win, "e2e_settings.png")

        bridge.demoCommand.emit("page:listen")
        QTest.qWait(500)
        _shot(win, "e2e_listen.png")
