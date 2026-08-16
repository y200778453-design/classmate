"""Multilingual classroom utterance understanding: question / name / hotword detection.

Supports Cantonese (粵), Mandarin (普) and English question detection, student
name-call detection, subject hot-word fuzzy matching and a sensitivity model.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher

from .models import Detection, HotWord

STRONG_MARKERS: dict[str, list[str]] = {
    "yue": ["點解", "點樣", "咩係", "咩嚟", "咩意思", "幾多", "幾時", "邊個", "邊度", "點睇",
            "係咪", "有冇", "可唔可以", "點分", "有咩分別", "點處理", "點樣護理", "點樣做",
            "點評估", "點監測", "幾耐", "點解要", "即係", "點定義", "咩情況", "點樣判斷",
            "點算", "點知道", "有幾種", "幾多種", "點預防", "點改善"],
    "zh": ["為什麼", "為什麼會", "什麼是", "什麼叫", "怎麼", "如何", "多少", "哪個", "哪些",
           "何時", "何謂", "為何", "可否", "是否", "為何要", "如何判斷", "如何評估", "怎麼處理",
           "有幾種", "有哪些", "什麼情況", "怎麼做", "如何區分", "有什麼不同", "有何", "幾種",
           "為什麼要", "如何預防"],
    "en": ["what", "why", "how", "when", "where", "which", "who", "explain", "describe",
           "compare", "contrast", "discuss", "define", "identify", "difference", "normal range",
           "indication", "contraindication", "management", "assessment", "intervention",
           "mechanism", "cause", "example", "tell me", "can you", "could you", "do you",
           "does", "is it", "are there", "give", "list", "name"],
}
ENDERS: tuple[str, ...] = ("?", "？", "嗎", "呢", "咩", "呀", "㗎", "啊", "麼")
_CJK = re.compile(r"[\u4e00-\u9fff]")


@dataclass
class NameHit:
    variant: str
    conf: float
    pattern: str = ""


@dataclass
class HotWordHit:
    hotword: HotWord
    conf: float


def normalize(text: str) -> str:
    t = text.strip().lower()
    t = re.sub(r"[！-～]", lambda m: chr(ord(m.group(0)) - 0xFEE0), t)
    t = re.sub(r"[,.!;:，。！；：、\"'「」『』（）()\[\]\s]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


class PhraseEngine:
    def __init__(self, sensitivity: int = 55):
        self._sens = 55
        self._names: list[str] = []
        self.set_sensitivity(sensitivity)

    # ---- sensitivity model -------------------------------------------------
    def set_sensitivity(self, value: int):
        self._sens = max(0, min(100, int(value)))
        self._min_units = max(1.0, 4 - 3.5 * self._sens / 100)
        self._ender_only = self._sens >= 42
        self._hw_ratio = 0.60 + (100 - self._sens) * 0.0016
        self._kw_ratio = 0.62 + (100 - self._sens) * 0.0016
        self._name_ratio = 0.86 + (100 - self._sens) * 0.0010

    @property
    def sensitivity(self) -> int:
        return self._sens

    def set_names(self, variants: list[str]):
        self._names = [normalize(v) for v in variants if v and normalize(v)]

    # ---- question detection --------------------------------------------------
    def detect(self, raw: str) -> Detection:
        text = normalize(raw)
        hits: dict[str, list[str]] = {}
        for lang, markers in STRONG_MARKERS.items():
            found = [m for m in markers if m in text]
            if found:
                hits[lang] = found
        strong: list[str] = [m for ms in hits.values() for m in ms]
        ends = raw.strip().endswith(ENDERS)
        has_cjk = bool(_CJK.search(text))
        if has_cjk:
            lang = "yue" if "yue" in hits else ("zh" if "zh" in hits else "zh")
        else:
            lang = "en"
        cjk_count = len(_CJK.findall(text))
        ascii_words = len(re.sub(r"[^a-z0-9]+", " ", text).split())
        units = ascii_words + cjk_count / 3.0
        is_q = bool(strong) and units >= self._min_units
        if not is_q and ends and self._ender_only and units >= self._min_units:
            is_q = True
        score = 0.0
        if is_q:
            score = min(1.0, 0.5 + 0.12 * len(strong) + (0.15 if ends else 0.0)
                        + (0.2 if any(m in ("點解", "why", "what", "為什麼", "咩係") for m in strong) else 0.0))
        return Detection(is_question=is_q, lang=lang, score=round(score, 2), strong=strong)

    # ---- name-call detection ---------------------------------------------------
    def detect_name(self, raw: str) -> NameHit | None:
        if not self._names:
            return None
        text = normalize(raw)
        best: NameHit | None = None
        for variant in self._names:
            if not variant:
                continue
            conf = 1.0 if variant in text else SequenceMatcher(None, text, variant).ratio()
            pattern = ""
            for pat in ("{n}同學", "{n}你", "{n}嚟答", "{n}來答", "{n}答", "有請{n}", "{n} please",
                        "how about {n}", "{n}，你", "{n} you answer", "叫{n}"):
                if pat.format(n=variant) in text:
                    conf, pattern = 1.0, pat
                    break
            if conf >= self._name_ratio and (best is None or conf > best.conf):
                best = NameHit(variant=variant, conf=round(conf, 2), pattern=pattern)
        return best

    # ---- hot-word matching -------------------------------------------------------
    def match_hotwords(self, raw: str, hotwords: list[HotWord]) -> list[HotWordHit]:
        text = normalize(raw)
        out: list[HotWordHit] = []
        for hw in hotwords:
            best = 0.0
            matched = False
            for cand in [hw.term] + list(hw.aliases):
                c = normalize(cand)
                if not c:
                    continue
                th = self._hw_ratio if len(c) >= 3 else min(0.99, self._hw_ratio + 0.14)
                if c in text:
                    best = max(best, 1.0)
                    matched = True
                    break
                if len(c) >= 2:
                    ln = len(text)
                    step = 1 if ln <= 40 else 2
                    for i in range(0, max(1, ln - len(c) + 1), step):
                        r = SequenceMatcher(None, text[i:i + len(c)], c).ratio()
                        best = max(best, r)
                        if r >= th:
                            matched = True
                        if best >= 0.999:
                            break
                    if len(c) >= 3:
                        best = max(best, SequenceMatcher(None, text, c).ratio())
                if matched:
                    break
            if matched:
                out.append(HotWordHit(hotword=hw, conf=round(best, 2)))
        out.sort(key=lambda h: -h.conf)
        return out

    def extract_keywords(self, raw: str, hotword_pool: list[HotWord], limit: int = 4) -> list[HotWordHit]:
        hits = self.match_hotwords(raw, hotword_pool)
        return [h for h in hits if h.conf >= self._kw_ratio][:limit]
