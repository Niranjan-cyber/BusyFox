"""Feedback pipeline (Task 14) — label/validate/aggregate/balance."""

from __future__ import annotations

from datetime import datetime, timedelta

from backend.pipeline.feedback_labelling import (
    RawLabel,
    aggregate_and_balance,
    is_valid_label,
    label_item,
    run_labelling_pipeline,
)
from backend.pipeline.feedback_pipeline import RawFeedbackItem
from backend.schemas.entities import Polarity, SourceKind

_NOW = datetime(2026, 9, 18)


def _item(id_: str, text: str, days_ago: int = 1) -> RawFeedbackItem:
    return RawFeedbackItem(id=id_, text=text, author=f"author_{id_}", published_at=_NOW - timedelta(days=days_ago), source_kind=SourceKind.SIMULATED)


def _label(**overrides) -> RawLabel:
    defaults = dict(
        aspect="alert_noise",
        polarity="negative",
        intents=("complaint",),
        segment_hint="sre_devops",
        evidence_span="too noisy",
    )
    defaults.update(overrides)
    return RawLabel(**defaults)


def test_is_valid_label_accepts_exact_span():
    assert is_valid_label(_label(), "Alerts are too noisy at night.")


def test_is_valid_label_rejects_unknown_aspect():
    assert not is_valid_label(_label(aspect="not_a_real_aspect"), "Alerts are too noisy at night.")


def test_is_valid_label_rejects_span_not_in_text():
    assert not is_valid_label(_label(evidence_span="completely different words"), "Alerts are too noisy at night.")


def test_is_valid_label_accepts_fuzzy_span():
    # dropped a letter ("nigt" for "night") — clears the 0.92 fuzzy bar.
    assert is_valid_label(_label(evidence_span="Alerts are too noisy at nigt"), "Alerts are too noisy at night.")


def test_label_item_retries_once_then_drops_still_invalid():
    calls = []

    def flaky_labeller(text: str) -> list[RawLabel]:
        calls.append(text)
        if len(calls) == 1:
            return [_label(aspect="bogus_aspect")]
        return [_label()]

    result = label_item(_item("a", "Alerts are too noisy at night."), flaky_labeller)
    assert len(calls) == 2
    assert len(result.labels) == 1
    assert result.labels[0].aspect == "alert_noise"


def test_label_item_drops_label_still_invalid_after_retry():
    def always_bad_labeller(text: str) -> list[RawLabel]:
        return [_label(aspect="bogus_aspect")]

    result = label_item(_item("a", "Alerts are too noisy at night."), always_bad_labeller)
    assert result.labels == ()


def test_theme_below_min_items_produces_no_signal():
    labelled = [
        _labelled(_item("a", "Alerts are too noisy at night."), _label()),
        _labelled(_item("b", "Alerts are too noisy at night."), _label()),
    ]
    result = aggregate_and_balance(labelled, run_id="run1", now=_NOW)
    assert result.signals == []


def test_theme_meeting_threshold_and_skew_produces_signal():
    labelled = [_labelled(_item(f"a{i}", "Alerts are too noisy at night."), _label()) for i in range(4)]
    result = aggregate_and_balance(labelled, run_id="run1", now=_NOW)
    assert len(result.signals) == 1
    signal = result.signals[0]
    assert signal.aspect == "alert_noise"
    assert signal.polarity == Polarity.NEGATIVE
    assert len(signal.evidence_ids) == 4
    assert len(result.evidence) == 4


def test_balanced_sentiment_produces_no_signal():
    negative = [_labelled(_item(f"n{i}", "Alerts are too noisy at night."), _label(polarity="negative")) for i in range(3)]
    positive = [_labelled(_item(f"p{i}", "Alerts are perfectly quiet now."), _label(polarity="positive", evidence_span="perfectly quiet")) for i in range(3)]
    result = aggregate_and_balance(negative + positive, run_id="run1", now=_NOW)
    assert result.signals == []


def test_run_labelling_pipeline_end_to_end():
    items = [_item(f"a{i}", "Alerts are too noisy at night.") for i in range(4)]

    def labeller(text: str) -> list[RawLabel]:
        return [_label()]

    result = run_labelling_pipeline(items, labeller, run_id="run1", now=_NOW)
    assert len(result.signals) == 1
    assert result.signals[0].produced_by == "feedback_pipeline_labeller"


def _labelled(item: RawFeedbackItem, *labels: RawLabel):
    from backend.pipeline.feedback_labelling import LabelledItem

    return LabelledItem(item=item, labels=tuple(labels))
