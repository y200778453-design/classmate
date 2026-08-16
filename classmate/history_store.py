"""SQLite history store (thread-safe)."""
from __future__ import annotations
import json
import sqlite3
import threading
from datetime import datetime
from pathlib import Path

from .models import HistoryEntry

_SCHEMA = """
CREATE TABLE IF NOT EXISTS history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL,
  subject_id TEXT,
  subject_name TEXT,
  kind TEXT,
  question TEXT,
  answer TEXT,
  mode TEXT,
  hotwords TEXT,
  urgent INTEGER DEFAULT 0,
  lang TEXT
);
CREATE INDEX IF NOT EXISTS idx_history_ts ON history(ts);
"""


class HistoryStore:
    def __init__(self, db_path: str | Path):
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        with self._lock:
            self._conn.executescript(_SCHEMA)
            self._conn.commit()

    def add(self, e: HistoryEntry) -> int:
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO history(ts,subject_id,subject_name,kind,question,answer,mode,hotwords,urgent,lang) "
                "VALUES(?,?,?,?,?,?,?,?,?,?)",
                (e.ts or datetime.now().isoformat(timespec="seconds"), e.subjectId, e.subjectName,
                 e.kind, e.question, e.answer, e.mode, json.dumps(e.hotwords, ensure_ascii=False),
                 1 if e.urgent else 0, e.lang))
            self._conn.commit()
            return cur.lastrowid

    def list(self, limit: int = 100, query: str = "") -> list[HistoryEntry]:
        with self._lock:
            if query.strip():
                like = f"%{query.strip()}%"
                rows = self._conn.execute(
                    "SELECT * FROM history WHERE question LIKE ? OR answer LIKE ? OR subject_name LIKE ? "
                    "ORDER BY id DESC LIMIT ?", (like, like, like, limit)).fetchall()
            else:
                rows = self._conn.execute(
                    "SELECT * FROM history ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [self._row_to_entry(r) for r in rows]

    @staticmethod
    def _row_to_entry(r) -> HistoryEntry:
        try:
            hw = json.loads(r[8]) if r[8] else []
        except Exception:
            hw = []
        return HistoryEntry(id=r[0], ts=r[1], subjectId=r[2] or "", subjectName=r[3] or "",
                            kind=r[4] or "", question=r[5] or "", answer=r[6] or "",
                            mode=r[7] or "", hotwords=hw, urgent=bool(r[9]), lang=r[10] or "")

    def count(self) -> int:
        with self._lock:
            return self._conn.execute("SELECT COUNT(*) FROM history").fetchone()[0]

    def count_today(self) -> int:
        today = datetime.now().strftime("%Y-%m-%d")
        with self._lock:
            return self._conn.execute(
                "SELECT COUNT(*) FROM history WHERE ts LIKE ?", (today + "%",)).fetchone()[0]

    def clear(self) -> None:
        with self._lock:
            self._conn.execute("DELETE FROM history")
            self._conn.commit()

    def export(self, path: str | Path) -> int:
        entries = self.list(limit=100000)
        data = [{"id": e.id, "ts": e.ts, "subject": e.subjectName, "kind": e.kind,
                 "question": e.question, "answer": e.answer, "mode": e.mode,
                 "hotwords": e.hotwords, "urgent": e.urgent, "lang": e.lang} for e in entries]
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return len(data)

    def close(self):
        with self._lock:
            self._conn.close()
