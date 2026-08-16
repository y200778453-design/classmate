"""Course catalog data integrity (KWNC BSN Year-3 preset)."""
import pytest

COMPULSORY = ["an3", "an4", "mh", "ic", "an5", "chn", "ger", "ce", "cl3", "cl4"]


class TestCatalog:
    def test_all_subjects_present(self, catalog):
        ids = {s.id for s in catalog.subjects}
        for c in COMPULSORY:
            assert c in ids, f"missing {c}"

    def test_unique_ids_and_year3(self, catalog):
        ids = [s.id for s in catalog.subjects]
        assert len(ids) == len(set(ids))
        assert all(s.year == 3 for s in catalog.subjects)

    def test_every_hotword_has_notes(self, catalog):
        for s in catalog.subjects:
            for h in s.hotwords:
                assert h.term.strip(), f"{s.id} empty term"
                assert h.concise.strip(), f"{s.id}/{h.term} missing concise"
                assert h.deep.strip(), f"{s.id}/{h.term} missing deep"

    def test_compulsory_subjects_have_rich_hotwords(self, catalog):
        for c in COMPULSORY:
            s = catalog.get(c)
            assert len(s.hotwords) >= 8, f"{c} has only {len(s.hotwords)}"

    def test_integrity_report_empty(self, catalog):
        assert catalog.integrity() == []

    def test_custom_hotword_roundtrip(self, catalog, cfg):
        before = len(catalog.get("ic").hotwords)
        hw = catalog.add_custom_hotword("ic", "濕性敷料")
        assert hw is not None
        assert len(catalog.get("ic").hotwords) == before + 1
        assert catalog.get("ic").hotwords[-1].custom is True
        assert catalog.remove_custom_hotword("ic", "濕性敷料") is True
        assert len(catalog.get("ic").hotwords) == before

    def test_custom_hotword_persists(self, catalog, cfg):
        catalog.add_custom_hotword("ger", "防跌評估")
        from classmate.courses import CourseCatalog
        c2 = CourseCatalog(
            [str(p) for p in [__import__("pathlib").Path(__file__).resolve().parents[2]
                              / "data" / "courses_a.json",
                              __import__("pathlib").Path(__file__).resolve().parents[2]
                              / "data" / "courses_b.json"]], cfg)
        assert any(h.term == "防跌評估" for h in c2.get("ger").hotwords)
