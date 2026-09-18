"""Feedback pipeline (Task 13) — normalise/dedupe/redact/spam filter,
pure code, no Bedrock call (plan.md Task 13).
"""

from __future__ import annotations

from datetime import datetime

from backend.pipeline.feedback_pipeline import (
    RawFeedbackItem,
    dedupe,
    filter_spam,
    normalise,
    redact,
    run_pipeline,
)
from backend.schemas.entities import SourceKind

_WHEN = datetime(2026, 9, 18)


def _item(id_: str, text: str, source_kind: SourceKind = SourceKind.SIMULATED) -> RawFeedbackItem:
    return RawFeedbackItem(id=id_, text=text, author="founder", published_at=_WHEN, source_kind=source_kind)


def test_normalise_collapses_whitespace_and_trims():
    items = [_item("a", "  Alerts   are\n\nnoisy   ")]
    assert normalise(items)[0].text == "Alerts are noisy"


def test_dedupe_drops_case_insensitive_repeats():
    items = [_item("a", "Alerts are noisy"), _item("b", "alerts are noisy"), _item("c", "Something else")]
    result = dedupe(items)
    assert [i.id for i in result] == ["a", "c"]


def test_redact_scrubs_email_and_phone():
    items = [_item("a", "reach me at jane@example.com or 555-123-4567")]
    result = redact(items)
    assert result[0].text == "reach me at [redacted-email] or [redacted-phone]"


def test_filter_spam_drops_short_and_repeated_char_and_bare_url():
    items = [
        _item("a", "This is a real, substantive complaint about onboarding."),
        _item("b", "short"),
        _item("c", "!!!!!!!!!!"),
        _item("d", "https://example.com/thing"),
    ]
    result = filter_spam(items)
    assert [i.id for i in result] == ["a"]


def test_run_pipeline_composes_all_four_stages_in_order():
    items = [
        _item("a", "  Onboarding is confusing, email jane@example.com  "),
        _item("b", "Onboarding is confusing, email jane@example.com"),
        _item("c", "!!!!!!!!!!"),
    ]
    result = run_pipeline(items)
    assert [i.id for i in result] == ["a"]
    assert result[0].text == "Onboarding is confusing, email [redacted-email]"


def test_owner_upload_source_kind_survives_pipeline():
    items = [_item("a", "A real, substantive piece of feedback here.", SourceKind.OWNER_UPLOAD)]
    assert run_pipeline(items)[0].source_kind == SourceKind.OWNER_UPLOAD
