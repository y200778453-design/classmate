"""History store CRUD."""
from classmate.history_store import HistoryStore
from classmate.models import HistoryEntry


def make_entry(subject_name="感染控制", kind="question", urgent=False):
    return HistoryEntry(ts="2025-06-01T10:00:00", subjectId="ic", subjectName=subject_name,
                        kind=kind, question="咩係標準預防措施？", answer="答案", mode="concise",
                        hotwords=["標準預防措施"], urgent=urgent, lang="yue")


class TestStore:
    def test_add_and_list(self, tmp_path):
        s = HistoryStore(tmp_path / "h.db")
        s.add(make_entry())
        rows = s.list()
        assert len(rows) == 1
        assert rows[0].question.startswith("咩係")
        s.close()

    def test_search(self, tmp_path):
        s = HistoryStore(tmp_path / "h.db")
        s.add(make_entry())
        s.add(HistoryEntry(ts="2025-06-01T10:05:00", subjectId="ce", subjectName="重急症護理",
                           kind="question", question="GCS有幾多分？", answer="15", mode="deep",
                           hotwords=[], urgent=False, lang="zh"))
        assert len(s.list(query="GCS")) == 1
        assert len(s.list(query="標準預防")) == 1
        assert len(s.list(query="不存在xyz")) == 0
        s.close()

    def test_urgent_flag_and_count_today(self, tmp_path):
        s = HistoryStore(tmp_path / "h.db")
        from datetime import datetime
        today = datetime.now().isoformat(timespec="seconds")
        s.add(HistoryEntry(ts=today, subjectId="ic", subjectName="感染控制", kind="name",
                           question="你嚟答", answer="a", mode="concise", hotwords=[],
                           urgent=True, lang="yue"))
        assert s.list()[0].urgent is True
        assert s.count_today() >= 1
        s.close()

    def test_clear_and_export(self, tmp_path):
        s = HistoryStore(tmp_path / "h.db")
        s.add(make_entry())
        out = tmp_path / "export.json"
        n = s.export(out)
        assert n == 1
        assert out.exists()
        s.clear()
        assert s.count() == 0
        s.close()
