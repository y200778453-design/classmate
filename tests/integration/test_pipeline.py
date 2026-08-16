"""Full pipeline: mock recognizer → bridge → detection → answer → history."""
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def qt_app():
    from PySide6.QtCore import QCoreApplication
    return QCoreApplication.instance() or QCoreApplication([])


@pytest.fixture()
def bridge(qt_app, cfg, catalog, tmp_path):
    from classmate.answer_engine import AnswerEngine
    from classmate.bridge import ClassMateBridge
    from classmate.history_store import HistoryStore
    cfg.set("userName", {"zh": "李小明", "en": "Xiao Ming", "yue": "李小明"})
    store = HistoryStore(tmp_path / "hist.db")
    b = ClassMateBridge(cfg, catalog, AnswerEngine(catalog, cfg), store, ROOT)
    yield b
    b.close()


class TestPipeline:
    def test_question_event_flow(self, bridge):
        events = []
        bridge.questionDetected.connect(lambda ev: events.append(ev))
        bridge.selectSubject("ic")
        bridge.injectUtterance("咩係標準預防措施？", "yue")
        assert len(events) == 1
        ev = events[0]
        assert ev["kind"] == "question"
        assert ev["source"] == "kb"
        assert "標準預防措施" in ev["answer"]
        assert ev["hotwords"]
        assert bridge.stats["questions"] >= 1

    def test_english_question_event(self, bridge):
        events = []
        bridge.questionDetected.connect(lambda ev: events.append(ev))
        bridge.selectSubject("ic")
        bridge.injectUtterance("What is the difference between disinfection and sterilization?", "en")
        assert len(events) == 1
        assert events[0]["lang"] == "en"

    def test_mandarin_question_event(self, bridge):
        events = []
        bridge.questionDetected.connect(lambda ev: events.append(ev))
        bridge.selectSubject("ic")
        bridge.injectUtterance("為什麼多重耐藥菌越來越常見？", "zh")
        assert len(events) == 1

    def test_name_call_urgent_concise(self, bridge):
        events = []
        bridge.nameCalled.connect(lambda ev: events.append(ev))
        bridge.selectSubject("ic")
        bridge.injectUtterance("李小明，你嚟答下MRSA要點樣隔離？", "yue")
        assert len(events) == 1
        ev = events[0]
        assert ev["urgent"] is True
        assert ev["mode"] == "concise"
        assert "MRSA" in ev["answer"]

    def test_statement_ignored(self, bridge):
        q_events, n_events = [], []
        bridge.questionDetected.connect(lambda ev: q_events.append(ev))
        bridge.nameCalled.connect(lambda ev: n_events.append(ev))
        bridge.injectUtterance("今日講到呢度，下堂再續", "yue")
        assert not q_events and not n_events

    def test_history_recorded(self, bridge):
        bridge.selectSubject("ic")
        bridge.injectUtterance("點解要洗手先接觸病人？", "yue")
        rows = bridge.store.list()
        assert any("洗手" in (r.question or "") for r in rows)

    def test_deep_mode_and_reamswer(self, bridge):
        events = []
        bridge.questionDetected.connect(lambda ev: events.append(ev))
        bridge.selectSubject("ic")
        bridge.setAnswerMode("deep")
        bridge.injectUtterance("點解要洗手先接觸病人？", "yue")
        assert events[-1]["mode"] == "deep"
        r = bridge.reAnswer(999, "點解要洗手先接觸病人？", "concise")
        assert r["source"] == "kb"
        assert len(r["answer"]) < len(events[-1]["answer"])

    def test_name_call_reuses_last_question(self, bridge):
        bridge.selectSubject("ic")
        bridge.injectUtterance("咩係標準預防措施？", "yue")
        events = []
        bridge.nameCalled.connect(lambda ev: events.append(ev))
        bridge.injectUtterance("李小明！", "yue")
        assert len(events) == 1
        assert events[0]["question"] == "咩係標準預防措施？"

    def test_custom_hotword_flow(self, bridge):
        assert bridge.addHotWord("ic", "濕性敷料") is True
        bridge.selectSubject("ic")
        events = []
        bridge.questionDetected.connect(lambda ev: events.append(ev))
        bridge.injectUtterance("點樣揀濕性敷料？", "yue")
        assert len(events) == 1
        assert "濕性敷料" in events[0]["hotwords"]
        assert bridge.removeHotWord("ic", "濕性敷料") is True

    def test_sensitivity_live_change(self, bridge):
        events = []
        bridge.questionDetected.connect(lambda ev: events.append(ev))
        bridge.selectSubject("ic")
        bridge.setSensitivity(10)
        bridge.injectUtterance("洗手咩？", "yue")
        assert len(events) == 0
        bridge.setSensitivity(90)
        bridge.injectUtterance("洗手咩？", "yue")
        assert len(events) == 1
