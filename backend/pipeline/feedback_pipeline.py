"""Feedback pipeline (Task 13) — normalise -> dedupe -> redact -> spam filter
(PRD §9 diagram, first four stages). Pure code, no LLM call: runs on raw
PulseStack tickets/survey responses or owner uploads before Task 14's Haiku
labeller turns cleaned items into Signal/Evidence (§14.5/§14.7).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from datetime import datetime

from backend.schemas.entities import SourceKind

_WHITESPACE_RE = re.compile(r"\s+")
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE_RE = re.compile(r"\+?\d[\d\-. ]{7,}\d")
_REPEATED_CHAR_RE = re.compile(r"^(.)\1{4,}$")
_BARE_URL_RE = re.compile(r"^https?://\S+$", re.IGNORECASE)
_MIN_LEN = 12


@dataclass(frozen=True)
class RawFeedbackItem:
    """One ticket/survey/upload row, pre-labelling. Not a §14 entity — this
    only exists between ingestion and the Task 14 labeller."""

    id: str
    text: str
    author: str | None
    published_at: datetime
    source_kind: SourceKind


def normalise(items: list[RawFeedbackItem]) -> list[RawFeedbackItem]:
    return [replace(item, text=_WHITESPACE_RE.sub(" ", item.text.strip())) for item in items]


def dedupe(items: list[RawFeedbackItem]) -> list[RawFeedbackItem]:
    seen: set[str] = set()
    deduped = []
    for item in items:
        key = item.text.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def redact(items: list[RawFeedbackItem]) -> list[RawFeedbackItem]:
    def scrub(text: str) -> str:
        text = _EMAIL_RE.sub("[redacted-email]", text)
        return _PHONE_RE.sub("[redacted-phone]", text)

    return [replace(item, text=scrub(item.text)) for item in items]


def filter_spam(items: list[RawFeedbackItem]) -> list[RawFeedbackItem]:
    def is_spam(text: str) -> bool:
        if len(text) < _MIN_LEN:
            return True
        return bool(_REPEATED_CHAR_RE.match(text) or _BARE_URL_RE.match(text))

    return [item for item in items if not is_spam(item.text)]


def run_pipeline(items: list[RawFeedbackItem]) -> list[RawFeedbackItem]:
    return filter_spam(redact(dedupe(normalise(items))))


if __name__ == "__main__":
    _demo_items = [
        RawFeedbackItem("a", "  Alerts   are noisy   ", "founder", datetime(2026, 9, 1), SourceKind.SIMULATED),
        RawFeedbackItem("b", "Alerts are noisy", "founder", datetime(2026, 9, 1), SourceKind.SIMULATED),
        RawFeedbackItem("c", "contact me at a@b.com or 555-123-4567", "sre", datetime(2026, 9, 1), SourceKind.OWNER_UPLOAD),
        RawFeedbackItem("d", "!!!!!!", "sre", datetime(2026, 9, 1), SourceKind.SIMULATED),
    ]
    _result = run_pipeline(_demo_items)
    assert [i.id for i in _result] == ["a", "c"], _result
    assert _result[1].text == "contact me at [redacted-email] or [redacted-phone]"
    print("ok")
