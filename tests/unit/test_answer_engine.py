"""Answer engine: KB / fallback / API paths."""
import pytest

from classmate.answer_engine import AnswerEngine
from classmate.phrase_engine import PhraseEngine


@pytest.fixture
def engine(catalog, cfg):
    return AnswerEngine(catalog, cfg)


def hits_for(question, subject, catalog, sens=55):
    pe = PhraseEngine(sensitivity=sens)
    return pe.match_hotwords(question, catalog.get(subject).hotwords)


class TestKnowledgeBase:
    def test_concise_kb_answer(self, engine, catalog):
        r = engine.answer("咩係標準預防措施？", "ic", "concise",
                          hits_for("咩係標準預防措施？", "ic", catalog))
        assert r.source == "kb"
        assert "標準預防措施" in r.answer
        assert r.mode == "concise"

    def test_deep_answer_longer_and_structured(self, engine, catalog):
        q = "咩係標準預防措施？"
        c = engine.answer(q, "ic", "concise", hits_for(q, "ic", catalog))
        d = engine.answer(q, "ic", "deep", hits_for(q, "ic", catalog))
        assert d.source == "kb"
        assert len(d.answer) > len(c.answer)
        assert "◆" in d.answer

    def test_english_kb_answer(self, engine, catalog):
        q = "What is the difference between disinfection and sterilization?"
        r = engine.answer(q, "ic", "concise", hits_for(q, "ic", catalog))
        assert "消毒與滅菌" in r.answer or "滅菌" in r.answer

    def test_fallback_framework(self, engine, catalog):
        r = engine.answer("點解呢個病咁難醫？", "ic", "deep", [])
        assert r.source == "framework"
        assert "答題框架" in r.answer

    def test_fallback_concise_mentions_keywords(self, engine, catalog):
        r = engine.answer("點樣處理低血糖呀？", "an3", "concise", [])
        assert r.source == "framework"
        assert "低血糖" in r.answer


class TestApi:
    def test_api_concise_prompt_and_parse(self, engine, monkeypatch):
        import classmate.answer_engine as ae
        import types

        captured = {}

        class FakeResp:
            def raise_for_status(self):
                return None

            def json(self):
                return {"choices": [{"message": {"content": "血壓正常值為 120/80 mmHg。"}}]}

        def fake_post(url, json=None, headers=None, timeout=None):
            captured["url"] = url
            captured["json"] = json
            captured["headers"] = headers
            return FakeResp()

        monkeypatch.setattr(ae.requests, "post", fake_post)
        cfg = engine.cfg
        cfg.set("apiEnabled", True)
        cfg.set("apiBase", "https://example.com/v1")
        cfg.set("apiKey", "sk-test")
        r = engine.answer_via_api("What is normal blood pressure?", "an3", "concise")
        assert r.source == "api"
        assert "血壓" in r.answer
        assert captured["url"] == "https://example.com/v1/chat/completions"
        assert captured["json"]["messages"][0]["content"].find("簡潔") >= 0
        assert captured["headers"]["Authorization"] == "Bearer sk-test"
