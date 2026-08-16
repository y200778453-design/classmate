"""Answer engine: offline KB → optional OpenAI-compatible API → framework fallback."""
from __future__ import annotations
import time

import requests

from .config import AppConfig
from .courses import CourseCatalog
from .models import AnswerResult, Subject

_SYSTEM_PROMPT = (
    "你是護理學院學士學位大三學生的課堂助教，協助即時回答老師在課堂上的提問。"
    "回答必須準確、以護理專業知識為本，語言跟隨問題的語言（粵語問題可用繁體中文口語作答）。"
)
_MODE_RULES = {
    "concise": "簡潔模式：用不超過 3 句直接回答重點，最後附 2-4 個關鍵詞。不要展開。",
    "deep": "深入研討模式：分點作答，依次為 定義 → 機制/病理 → 臨床表現 → 護理要點/處置，每點 1-2 句。",
}


class AnswerEngine:
    def __init__(self, catalog: CourseCatalog, cfg: AppConfig):
        self.catalog = catalog
        self.cfg = cfg

    def answer(self, question: str, subject_id: str, mode: str,
               hotword_hits: list = None) -> AnswerResult:
        """hotword_hits: list of HotWordHit from PhraseEngine."""
        start = time.time()
        hits = [h for h in (hotword_hits or [])]
        result = self._kb_answer(question, subject_id, mode, hits) if hits else None
        if result is None:
            result = self._framework_answer(question, subject_id, mode)
        result.elapsedMs = int((time.time() - start) * 1000)
        return result

    def answer_via_api(self, question: str, subject_id: str, mode: str) -> AnswerResult:
        """Call the configured OpenAI-compatible endpoint (blocking; run in a worker)."""
        subject = self.catalog.get(subject_id)
        ctx = f"科目：{subject.name}（{subject.nameEn}）" if subject else "科目：未指定"
        payload = {
            "model": self.cfg.get("apiModel", "gpt-4o-mini"),
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT + "\n" + _MODE_RULES.get(mode, _MODE_RULES["concise"])},
                {"role": "user", "content": f"{ctx}\n老師提問：{question}"},
            ],
            "temperature": 0.4,
            "max_tokens": 220 if mode == "concise" else 900,
        }
        resp = requests.post(
            self.cfg.get("apiBase", "https://api.openai.com/v1").rstrip("/") + "/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {self.cfg.get('apiKey', '')}"},
            timeout=25,
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"].strip()
        return AnswerResult(mode=mode, question=question, answer=text, source="api",
                            hotwords=[], elapsedMs=0)

    # ---- offline knowledge base ------------------------------------------------
    def _kb_answer(self, question, subject_id, mode, hits) -> AnswerResult | None:
        top = hits[:3]
        if mode == "concise":
            parts = [f"{h.hotword.term}：{h.hotword.concise}" for h in top]
            answer = f"「{question}」\n" + "\n".join(parts)
        else:
            blocks = []
            for h in top:
                blocks.append(f"◆ {h.hotword.term}（命中 {int(h.conf*100)}%）\n{h.hotword.deep}")
            answer = f"「{question}」\n" + "\n\n".join(blocks)
        return AnswerResult(mode=mode, question=question, answer=answer, source="kb",
                            hotwords=[h.hotword.term for h in top])

    # ---- offline framework fallback -------------------------------------------------
    def _framework_answer(self, question: str, subject_id: str, mode: str) -> AnswerResult:
        from .phrase_engine import PhraseEngine  # local import avoids cycle at module load
        pool = [hw for s in self.catalog.subjects for hw in s.hotwords]
        engine = PhraseEngine(sensitivity=70)
        kws = [h.hotword.term for h in engine.extract_keywords(question, pool, limit=4)]
        if mode == "concise":
            if kws:
                answer = f"「{question}」快速要點：題目核心為 {'、'.join(kws)}，可先一句定義，再答臨床意義與護理重點。"
            else:
                answer = f"「{question}」快速要點：先直接答結論，再補 1 個關鍵原因或數值；答案以課本為準。"
        else:
            kws_txt = ("\n相關概念：" + "、".join(kws)) if kws else ""
            answer = (f"「{question}」答題框架：\n"
                      "1. 定義：先界定題中核心概念。\n"
                      "2. 機制/病理：說明發生原因與過程。\n"
                      "3. 臨床表現：列出典型症狀、體徵或數值。\n"
                      "4. 護理要點：評估 → 措施 → 評值，加入安全注意事項。" + kws_txt +
                      "\n\n（提示：在「設定」啟用 AI 接駁可取得完整答案。）")
        return AnswerResult(mode=mode, question=question, answer=answer, source="framework",
                            hotwords=kws)
