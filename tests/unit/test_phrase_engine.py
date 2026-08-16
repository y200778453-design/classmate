"""Phrase engine: multilingual question / name / hotword detection."""
from classmate.phrase_engine import PhraseEngine


class TestQuestionDetection:
    def test_cantonese_why_question(self, phrase):
        d = phrase.detect("點解糖尿病人容易有傷口感染？")
        assert d.is_question
        assert d.lang == "yue"
        assert d.score > 0.6

    def test_cantonese_what_question(self, phrase):
        d = phrase.detect("咩係標準預防措施？")
        assert d.is_question

    def test_mandarin_question(self, phrase):
        d = phrase.detect("為什麼多重耐藥菌越來越常見？")
        assert d.is_question
        assert d.lang == "zh"

    def test_english_question(self, phrase):
        d = phrase.detect("What is the difference between disinfection and sterilization?")
        assert d.is_question
        assert d.lang == "en"

    def test_english_how_question(self, phrase):
        assert phrase.detect("How do you assess the Glasgow Coma Scale?").is_question

    def test_statement_not_question(self, phrase):
        d = phrase.detect("今日我哋繼續講醫院感染嘅控制")
        assert not d.is_question

    def test_ender_only_at_high_sensitivity(self):
        pe = PhraseEngine(sensitivity=90)
        assert pe.detect("血壓高咩？").is_question

    def test_ender_only_rejected_at_low_sensitivity(self):
        pe = PhraseEngine(sensitivity=10)
        assert not pe.detect("血壓高咩？").is_question


class TestNameDetection:
    def test_cantonese_name_call(self, phrase):
        hit = phrase.detect_name("李小明，你嚟答下MRSA要點樣隔離？")
        assert hit is not None
        assert hit.conf >= 0.9

    def test_english_name_call(self, phrase):
        hit = phrase.detect_name("How about Xiao Ming?")
        assert hit is not None

    def test_nickname_call(self, phrase):
        assert phrase.detect_name("小明，你答") is not None

    def test_no_name(self, phrase):
        assert phrase.detect_name("今日講感染控制") is None


class TestHotwords:
    def test_exact_hotword(self, phrase, catalog):
        hits = phrase.match_hotwords("咩係標準預防措施？", catalog.get("ic").hotwords)
        assert any(h.hotword.term == "標準預防措施" and h.conf >= 0.99 for h in hits)

    def test_english_alias_hotword(self, phrase, catalog):
        hits = phrase.match_hotwords("what is MRSA isolation", catalog.get("ic").hotwords)
        assert any(h.hotword.term == "MRSA" for h in hits)

    def test_fuzzy_match_at_high_sensitivity(self, catalog):
        pe = PhraseEngine(sensitivity=90)
        hits = pe.match_hotwords("講下醣尿病點護理", catalog.get("an3").hotwords)
        assert any(h.hotword.term == "糖尿病" for h in hits)

    def test_fuzzy_match_rejected_at_low_sensitivity(self, catalog):
        pe = PhraseEngine(sensitivity=10)
        hits = pe.match_hotwords("講下醣尿病點護理", catalog.get("an3").hotwords)
        assert not any(h.hotword.term == "糖尿病" for h in hits)

    def test_keyword_extraction_cross_subject(self, phrase, catalog):
        pool = [hw for s in catalog.subjects for hw in s.hotwords]
        kws = phrase.extract_keywords("什麼是GCS昏迷指數", pool)
        assert any(k.hotword.term == "格拉斯哥昏迷指數" for k in kws)
