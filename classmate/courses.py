"""Course catalog: KWNC BSN Year-3 subjects with hot words + custom hot words."""
from __future__ import annotations
import json
from pathlib import Path
from .config import AppConfig
from .models import HotWord, Subject

_CUSTOM_CONCISE = "（自訂熱詞：命中時會以答題框架協助作答。）"
_CUSTOM_DEEP = "（自訂熱詞：尚未有資料庫筆記。建議課後補充：定義 → 機制 → 臨床表現 → 護理要點。）"


class CourseCatalog:
    def __init__(self, data_paths, cfg: AppConfig | None = None):
        if isinstance(data_paths, (str, Path)):
            data_paths = [data_paths]
        self.cfg = cfg
        self.subjects: list[Subject] = []
        for dp in data_paths:
            raw = json.loads(Path(dp).read_text(encoding="utf-8"))
            for s in raw.get("subjects", []):
                hws = [HotWord(term=h["term"], aliases=h.get("aliases", []),
                               concise=h.get("concise", ""), deep=h.get("deep", ""))
                       for h in s.get("hotwords", [])]
                self.subjects.append(Subject(
                    id=s["id"], name=s["name"], nameEn=s.get("nameEn", ""),
                    icon=s.get("icon", "✦"), color=s.get("color", "#6C8CFF"),
                    kind=s.get("kind", "必修"), year=s.get("year", 3), hotwords=hws))
        self._apply_custom()

    def _custom_key(self) -> dict:
        return self.cfg.get("customHotwords", {}) if self.cfg else {}

    def _apply_custom(self):
        for subj_id, terms in self._custom_key().items():
            subj = self.get(subj_id)
            if not subj:
                continue
            for t in terms:
                if any(h.term == t for h in subj.hotwords):
                    continue
                subj.hotwords.append(HotWord(term=t, concise=_CUSTOM_CONCISE, deep=_CUSTOM_DEEP, custom=True))

    def get(self, subject_id: str) -> Subject | None:
        return next((s for s in self.subjects if s.id == subject_id), None)

    def add_custom_hotword(self, subject_id: str, term: str) -> HotWord | None:
        subj = self.get(subject_id)
        if not subj or not term.strip():
            return None
        term = term.strip()
        if any(h.term == term for h in subj.hotwords):
            return None
        hw = HotWord(term=term, concise=_CUSTOM_CONCISE, deep=_CUSTOM_DEEP, custom=True)
        subj.hotwords.append(hw)
        if self.cfg:
            custom = self.cfg.get("customHotwords", {})
            custom.setdefault(subject_id, []).append(term)
            self.cfg.set("customHotwords", custom)
        return hw

    def remove_custom_hotword(self, subject_id: str, term: str) -> bool:
        subj = self.get(subject_id)
        if not subj:
            return False
        for h in list(subj.hotwords):
            if h.custom and h.term == term:
                subj.hotwords.remove(h)
                if self.cfg:
                    custom = self.cfg.get("customHotwords", {})
                    lst = [t for t in custom.get(subject_id, []) if t != term]
                    custom[subject_id] = lst
                    self.cfg.set("customHotwords", custom)
                return True
        return False

    def all_hotwords(self, subject_id: str) -> list[HotWord]:
        subj = self.get(subject_id)
        return subj.hotwords if subj else []

    def integrity(self) -> list[str]:
        errors: list[str] = []
        ids = [s.id for s in self.subjects]
        if len(ids) != len(set(ids)):
            errors.append("duplicate subject ids")
        for s in self.subjects:
            if not s.hotwords:
                errors.append(f"{s.id}: no hotwords")
            for h in s.hotwords:
                if not h.term.strip():
                    errors.append(f"{s.id}: empty hotword term")
                if not h.concise.strip() or not h.deep.strip():
                    errors.append(f"{s.id}/{h.term}: missing concise or deep note")
        return errors
