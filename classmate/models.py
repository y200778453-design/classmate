"""Data models for ClassMate."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class HotWord:
    term: str
    aliases: list[str] = field(default_factory=list)
    concise: str = ""
    deep: str = ""
    custom: bool = False


@dataclass
class Subject:
    id: str
    name: str
    nameEn: str = ""
    icon: str = "✦"
    color: str = "#6C8CFF"
    kind: str = "必修"
    year: int = 3
    hotwords: list[HotWord] = field(default_factory=list)


@dataclass
class AnswerResult:
    mode: str
    question: str
    answer: str
    source: str  # kb | api | framework
    hotwords: list[str] = field(default_factory=list)
    elapsedMs: int = 0


@dataclass
class HistoryEntry:
    id: int = 0
    ts: str = ""
    subjectId: str = ""
    subjectName: str = ""
    kind: str = "question"  # question | name
    question: str = ""
    answer: str = ""
    mode: str = "concise"
    hotwords: list[str] = field(default_factory=list)
    urgent: bool = False
    lang: str = ""


@dataclass
class Detection:
    is_question: bool
    lang: str
    score: float
    strong: list[str] = field(default_factory=list)
