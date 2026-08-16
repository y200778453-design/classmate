"""Qt bridge between the QML UI and the recognition/answer pipeline."""
from __future__ import annotations
import json
import threading
from collections import deque
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import (Property, QAbstractListModel, QModelIndex, QObject, Qt, QTimer,
                            Signal, Slot)
from PySide6.QtGui import QGuiApplication

from .answer_engine import AnswerEngine
from .audio_capture import AudioCapture
from .config import AppConfig
from .courses import CourseCatalog
from .history_store import HistoryStore
from .models import HistoryEntry
from .phrase_engine import PhraseEngine


def _subject_map(s) -> dict:
    return {"id": s.id, "name": s.name, "nameEn": s.nameEn, "icon": s.icon,
            "color": s.color, "kind": s.kind, "year": s.year,
            "hotwords": [{"term": h.term, "aliases": h.aliases, "concise": h.concise,
                          "deep": h.deep, "custom": h.custom} for h in s.hotwords]}


class HistoryListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows: list[HistoryEntry] = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._rows)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._rows)):
            return None
        e = self._rows[index.row()]
        mapping = {
            Qt.ItemDataRole.DisplayRole: e.question,
            Qt.ItemDataRole.UserRole + 1: e.ts,
            Qt.ItemDataRole.UserRole + 2: e.subjectName,
            Qt.ItemDataRole.UserRole + 3: "⚠ 點名" if e.urgent else "問題",
            Qt.ItemDataRole.UserRole + 4: e.answer,
            Qt.ItemDataRole.UserRole + 5: "深入研討" if e.mode == "deep" else "簡潔",
            Qt.ItemDataRole.UserRole + 6: e.lang,
            Qt.ItemDataRole.UserRole + 7: "、".join(e.hotwords),
            Qt.ItemDataRole.UserRole + 8: e.question,
        }
        return mapping.get(role)

    def roleNames(self):
        return {Qt.ItemDataRole.UserRole + 1: b"tsText",
                Qt.ItemDataRole.UserRole + 2: b"subjectName",
                Qt.ItemDataRole.UserRole + 3: b"kindText",
                Qt.ItemDataRole.UserRole + 4: b"answer",
                Qt.ItemDataRole.UserRole + 5: b"modeText",
                Qt.ItemDataRole.UserRole + 6: b"lang",
                Qt.ItemDataRole.UserRole + 7: b"hotwordsText",
                Qt.ItemDataRole.UserRole + 8: b"questionText"}

    def set_entries(self, rows: list[HistoryEntry]):
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()


class ClassMateBridge(QObject):
    transcriptChanged = Signal(str)
    audioLevelChanged = Signal(float)
    listeningChanged = Signal(bool)
    statusChanged = Signal(str)
    subjectsChanged = Signal()
    statsChanged = Signal(dict)
    questionDetected = Signal(dict)
    nameCalled = Signal(dict)
    answerReady = Signal(dict)
    historyUpdated = Signal()
    demoCommand = Signal(str)
    toast = Signal(dict)
    _historyDirty = Signal()

    def __init__(self, cfg: AppConfig, catalog: CourseCatalog,
                 answer: AnswerEngine, store: HistoryStore, root: Path, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.catalog = catalog
        self.answer = answer
        self.store = store
        self.root = Path(root)
        self.phrase = PhraseEngine(cfg.get("sensitivity", 55))
        self.phrase.set_names(self._name_variants())
        self._history_model = HistoryListModel(self)
        self._capture = AudioCapture(on_level=self._on_level)
        self._engine = None
        self._feeder: threading.Thread | None = None
        self._listening = False
        self._transcript = ""
        self._audio_level = 0.0
        self._status = "未開始"
        self._current_subject_id = cfg.get("currentSubjectId") or self.catalog.subjects[0].id
        self._sensitivity = cfg.get("sensitivity", 55)
        self._answer_mode = cfg.get("answerMode", "concise")
        self._last_questions: deque[str] = deque(maxlen=6)
        self._event_seq = 0
        self._stat_total = store.count()
        self._stat_today = store.count_today()
        self._stat_questions = 0
        self._stat_names = 0
        self._historyDirty.connect(self._refresh_history_model)
        self._refresh_history_model()
        self._emit_stats()

    # ------------------------------------------------------------------ props
    def _get_listening(self): return self._listening
    def _get_transcript(self): return self._transcript
    def _get_level(self): return self._audio_level
    def _get_status(self): return self._status
    def _get_sensitivity(self): return self._sensitivity
    def _get_answer_mode(self): return self._answer_mode
    def _get_current_subject_id(self): return self._current_subject_id
    def _get_subjects(self): return [_subject_map(s) for s in self.catalog.subjects]

    def _get_current_subject_name(self):
        s = self.catalog.get(self._current_subject_id)
        return s.name if s else ""

    def _get_stats(self):
        return {"total": self._stat_total, "today": self._stat_today,
                "questions": self._stat_questions, "nameCalls": self._stat_names,
                "listening": self._listening, "engine": self._engine.name if self._engine else "—"}

    def _get_engines(self):
        from .recognizer import engine_status
        return engine_status()

    def _get_api_state(self):
        return {"enabled": bool(self.cfg.get("apiEnabled")), "base": self.cfg.get("apiBase", ""),
                "key": self.cfg.get("apiKey", ""), "model": self.cfg.get("apiModel", ""),
                "mode": self.cfg.get("answerMode", "concise")}

    def _get_user_name(self):
        return dict(self.cfg.get("userName", {"zh": "", "en": "", "yue": ""}))

    def _get_history_model(self):
        return self._history_model

    listening = Property(bool, _get_listening, notify=listeningChanged)
    transcript = Property(str, _get_transcript, notify=transcriptChanged)
    audioLevel = Property(float, _get_level, notify=audioLevelChanged)
    statusText = Property(str, _get_status, notify=statusChanged)
    sensitivity = Property(int, _get_sensitivity, notify=statsChanged)
    answerMode = Property(str, _get_answer_mode, notify=statsChanged)
    currentSubjectId = Property(str, _get_current_subject_id, notify=subjectsChanged)
    currentSubjectName = Property(str, _get_current_subject_name, notify=subjectsChanged)
    subjects = Property(list, _get_subjects, notify=subjectsChanged)
    stats = Property(dict, _get_stats, notify=statsChanged)
    engines = Property(dict, _get_engines, notify=statusChanged)
    apiState = Property(dict, _get_api_state, notify=statsChanged)
    userName = Property(dict, _get_user_name, notify=statsChanged)
    historyModel = Property("QVariant", _get_history_model, constant=True)

    # ------------------------------------------------------------------ slots
    def _name_variants(self) -> list[str]:
        u = self.cfg.get("userName", {})
        return [u.get("zh", ""), u.get("en", ""), u.get("yue", "")]

    @Slot()
    def startListening(self):
        self._start_engine(None)

    def _start_engine(self, engine_override):
        if self._listening:
            return
        from . import recognizer as R
        eng = engine_override or R.create_recognizer(self.cfg, self._on_transcript, self._on_level)
        self._engine = eng
        ok = eng.start()
        if eng.needs_audio():
            if self._capture.start():
                self._feeder = threading.Thread(target=self._feed_loop, daemon=True)
                self._feeder.start()
            elif engine_override is None:
                self._set_status("⚠ " + self.capture_last_error())
        self._listening = True
        self.listeningChanged.emit(True)
        self._set_status(f"聆聽中 · {eng.name}" + ("" if eng.needs_audio() else "（演示）"))
        self._emit_stats()

    def capture_last_error(self):
        return self._capture.last_error

    def _feed_loop(self):
        while self._listening and self._engine:
            chunk = self._capture.read(0.4)
            if chunk:
                try:
                    self._engine.feed(chunk)
                except Exception:
                    pass

    @Slot()
    def stopListening(self):
        self._listening = False
        if self._engine:
            try:
                self._engine.stop()
            except Exception:
                pass
        self._capture.stop()
        self._set_status("已暫停")
        self.listeningChanged.emit(False)
        self._emit_stats()

    @Slot()
    def toggleListening(self):
        if self._listening:
            self.stopListening()
        else:
            self.startListening()

    def _on_level(self, level: float):
        self._audio_level = level
        self.audioLevelChanged.emit(level)

    def _on_transcript(self, text: str, lang: str, conf: float):
        self._handle_utterance(text, lang, conf)

    def _handle_utterance(self, text: str, lang: str, conf: float):
        text = (text or "").strip()
        if len(text) < 2:
            return
        self._transcript = text
        self.transcriptChanged.emit(text)
        det = self.phrase.detect(text)
        name_hit = self.phrase.detect_name(text)
        subj = self.catalog.get(self._current_subject_id)
        subj_name = subj.name if subj else ""
        hits = self.phrase.match_hotwords(text, subj.hotwords) if subj else []
        self._event_seq += 1
        ev = {"id": self._event_seq, "ts": datetime.now().isoformat(timespec="seconds"),
              "subjectId": self._current_subject_id, "subjectName": subj_name,
              "spoken": text, "lang": lang, "urgent": False, "hotwords": [h.hotword.term for h in hits]}

        if name_hit:
            question = text if det.is_question else (self._last_questions[-1] if self._last_questions else text)
            qhits = self.phrase.match_hotwords(question, subj.hotwords) if subj else []
            result = self.answer.answer(question, self._current_subject_id, "concise", qhits)
            ev.update({"kind": "name", "urgent": True, "question": question,
                       "answer": result.answer, "mode": result.mode, "source": result.source,
                       "hotwords": [h.hotword.term for h in qhits]})
            self.store.add(self._entry_from_event(ev))
            self._stat_names += 1
            self._stat_total += 1
            self._stat_today += 1
            self.nameCalled.emit(ev)
        elif det.is_question:
            self._last_questions.append(text)
            mode = self._answer_mode
            result = self.answer.answer(text, self._current_subject_id, mode, hits)
            ev.update({"kind": "question", "urgent": False, "question": text,
                       "answer": result.answer, "mode": result.mode, "source": result.source,
                       "hotwords": [h.hotword.term for h in hits]})
            self.store.add(self._entry_from_event(ev))
            self._stat_questions += 1
            self._stat_total += 1
            self._stat_today += 1
            self.questionDetected.emit(ev)
            if result.source != "kb" and self.cfg.get("apiEnabled"):
                threading.Thread(target=self._api_fill, args=(ev["id"], text, mode), daemon=True).start()
        self._historyDirty.emit()
        self._emit_stats()

    def _api_fill(self, event_id: int, question: str, mode: str):
        try:
            result = self.answer.answer_via_api(question, self._current_subject_id, mode)
            self.answerReady.emit({"id": event_id, "answer": result.answer,
                                   "mode": result.mode, "source": "api"})
        except Exception as exc:
            self.answerReady.emit({"id": event_id, "answer": "", "mode": mode,
                                   "source": "api-error", "error": str(exc)[:200]})

    def _entry_from_event(self, ev: dict) -> HistoryEntry:
        return HistoryEntry(ts=ev["ts"], subjectId=ev.get("subjectId", ""),
                            subjectName=ev.get("subjectName", ""), kind=ev.get("kind", "question"),
                            question=ev.get("question", ""), answer=ev.get("answer", ""),
                            mode=ev.get("mode", ""), hotwords=ev.get("hotwords", []),
                            urgent=bool(ev.get("urgent")), lang=ev.get("lang", ""))

    @Slot(str, str)
    def injectUtterance(self, text: str, lang: str = "auto"):
        self._handle_utterance(text, lang, 1.0)

    @Slot(int, str, str, result=dict)
    def reAnswer(self, event_id: int, question: str, mode: str) -> dict:
        hits = []
        subj = self.catalog.get(self._current_subject_id)
        if subj:
            hits = self.phrase.match_hotwords(question, subj.hotwords)
        result = self.answer.answer(question, self._current_subject_id, mode, hits)
        out = {"id": event_id, "answer": result.answer, "mode": result.mode, "source": result.source}
        if result.source != "kb" and self.cfg.get("apiEnabled"):
            threading.Thread(target=self._api_fill, args=(event_id, question, mode), daemon=True).start()
        return out

    @Slot()
    def _refresh_history_model(self):
        self._history_model.set_entries(self.store.list(limit=200))
        self.historyUpdated.emit()

    @Slot(str)
    def searchHistory(self, query: str):
        self._history_model.set_entries(self.store.list(limit=200, query=query))
        self.historyUpdated.emit()

    @Slot()
    def clearHistory(self):
        self.store.clear()
        self._stat_total = self._stat_today = self._stat_questions = self._stat_names = 0
        self._historyDirty.emit()
        self._emit_stats()
        self.toast.emit({"kind": "info", "text": "歷史紀錄已清空"})

    @Slot(str, result=int)
    def exportHistory(self, path: str) -> int:
        if not (path or "").strip():
            from PySide6.QtCore import QStandardPaths
            docs = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
            path = str(Path(docs) / f"classmate_history_{datetime.now():%Y%m%d_%H%M}.json")
        try:
            n = self.store.export(path)
            self.toast.emit({"kind": "ok", "text": f"已匯出 {n} 條紀錄"})
            return n
        except Exception as exc:
            self.toast.emit({"kind": "error", "text": f"匯出失敗：{exc}"})
            return 0

    @Slot(bool, bool, bool)
    def setLanguages(self, yue: bool, zh: bool, en: bool):
        langs = []
        if yue:
            langs.append("yue")
        if zh:
            langs.append("zh")
        if en:
            langs.append("en")
        if not langs:
            langs = ["yue"]
        self.cfg.set("languages", langs)
        self._emit_stats()
        self.toast.emit({"kind": "ok", "text": "聆聽語言已更新（重新開始聆聽生效）"})

    def _get_language_state(self):
        langs = self.cfg.get("languages", ["yue", "zh", "en"])
        return {"yue": "yue" in langs, "zh": "zh" in langs, "en": "en" in langs}

    languageState = Property(dict, _get_language_state, notify=statsChanged)

    @Slot(str, str, str)
    def setUserName(self, zh: str, en: str, yue: str):
        self.cfg.set("userName", {"zh": zh, "en": en, "yue": yue})
        self.phrase.set_names([zh, en, yue])
        self._emit_stats()
        self.toast.emit({"kind": "ok", "text": "已儲存你的名字，點名即時提醒已啟用"})

    @Slot(int)
    def setSensitivity(self, value: int):
        self._sensitivity = max(0, min(100, int(value)))
        self.phrase.set_sensitivity(self._sensitivity)
        self.cfg.set("sensitivity", self._sensitivity)
        self._emit_stats()

    @Slot(str)
    def setAnswerMode(self, mode: str):
        self._answer_mode = mode if mode in ("concise", "deep") else "concise"
        self.cfg.set("answerMode", self._answer_mode)
        self._emit_stats()

    @Slot(str)
    def selectSubject(self, subject_id: str):
        if not self.catalog.get(subject_id):
            return
        self._current_subject_id = subject_id
        self.cfg.set("currentSubjectId", subject_id)
        self.subjectsChanged.emit()
        self._emit_stats()

    @Slot(str, str, result=bool)
    def addHotWord(self, subject_id: str, term: str) -> bool:
        hw = self.catalog.add_custom_hotword(subject_id, term)
        if hw:
            self.subjectsChanged.emit()
            self.toast.emit({"kind": "ok", "text": f"熱詞「{term}」已加到 {self.catalog.get(subject_id).name}"})
        return bool(hw)

    @Slot(str, str, result=bool)
    def removeHotWord(self, subject_id: str, term: str) -> bool:
        ok = self.catalog.remove_custom_hotword(subject_id, term)
        if ok:
            self.subjectsChanged.emit()
        return ok

    @Slot(str)
    def copyText(self, text: str):
        QGuiApplication.clipboard().setText(text)

    @Slot(bool, str, str, str)
    def saveApi(self, enabled: bool, base: str, key: str, model: str):
        self.cfg.set("apiEnabled", bool(enabled))
        self.cfg.set("apiBase", base.strip())
        self.cfg.set("apiKey", key.strip())
        self.cfg.set("apiModel", model.strip() or "gpt-4o-mini")
        self._emit_stats()
        self.toast.emit({"kind": "ok", "text": "AI 接駁設定已儲存" if enabled else "已切換為離線模式（內建知識庫）"})

    def _set_status(self, text: str):
        self._status = text
        self.statusChanged.emit(text)

    def _emit_stats(self):
        self.statsChanged.emit(self._get_stats())

    # ------------------------------------------------------------------ demo
    @Slot()
    def start_demo(self):
        self.cfg.set("userName", {"zh": "李小明", "en": "Xiao Ming", "yue": "李小明"})
        self.phrase.set_names(["李小明", "Xiao Ming", "小明"])
        self.selectSubject("ic")
        self.setSensitivity(55)
        script_path = self.root / "data" / "demo_script.json"
        data = json.loads(script_path.read_text(encoding="utf-8"))
        utterances = []
        for step in data["steps"]:
            if "utter" in step:
                utterances.append((step["utter"]["text"], step["utter"].get("lang", "auto"), 0.0))
            if "cmd" in step:
                cmd = step["cmd"]
                delay = step["at"]
                if cmd == "start":
                    QTimer.singleShot(int(delay * 1000), self.startListening)
                else:
                    QTimer.singleShot(int(delay * 1000), lambda c=cmd: self.demoCommand.emit(c))
        from .recognizer.mock_recognizer import MockRecognizer
        mock = MockRecognizer(self._on_transcript, None, "yue", script=utterances)
        self.cfg.set("recognitionEngine", "mock")
        self._start_engine(mock)

    def close(self):
        self.stopListening()
        self.store.close()
