"""PulseStack simulator (Task 10) — scenario + seeded generator, output
must already match Task 1's Signal/Evidence shape (plan.md Task 10).
"""

from __future__ import annotations

from backend.schemas.entities import Evidence, FreshnessStatus, Signal
from backend.simulator.pulsestack import generate_pulsestack_feedback, load_scenario

SCENARIO = load_scenario()
RUN_ID = "run_001"


def test_output_validates_as_task1_signal_and_evidence():
    result = generate_pulsestack_feedback(SCENARIO, RUN_ID, seed=SCENARIO["seed"])
    assert result.evidence and result.signals
    for evidence in result.evidence:
        Evidence.model_validate(evidence.model_dump())
    for signal in result.signals:
        Signal.model_validate(signal.model_dump())
        assert signal.run_id == RUN_ID
        assert signal.source_kind == "simulated"


def test_same_seed_is_deterministic():
    first = generate_pulsestack_feedback(SCENARIO, RUN_ID, seed=SCENARIO["seed"])
    second = generate_pulsestack_feedback(SCENARIO, RUN_ID, seed=SCENARIO["seed"])
    assert [e.model_dump() for e in first.evidence] == [e.model_dump() for e in second.evidence]
    assert [s.model_dump() for s in first.signals] == [s.model_dump() for s in second.signals]


def test_different_seed_reshuffles_personas():
    first = generate_pulsestack_feedback(SCENARIO, RUN_ID, seed=1)
    second = generate_pulsestack_feedback(SCENARIO, RUN_ID, seed=2)
    assert [e.author for e in first.evidence] != [e.author for e in second.evidence]


def test_real_tagged_effects_are_not_generated():
    result = generate_pulsestack_feedback(SCENARIO, RUN_ID, seed=SCENARIO["seed"])
    assert all(not s.claim_text.startswith("(real)") for s in result.signals)


def test_red_herring_with_no_effects_produces_nothing():
    result = generate_pulsestack_feedback(SCENARIO, RUN_ID, seed=SCENARIO["seed"])
    assert not any("APM suite" in s.claim_text for s in result.signals)


def test_stale_red_herring_is_flagged_stale():
    result = generate_pulsestack_feedback(SCENARIO, RUN_ID, seed=SCENARIO["seed"])
    stale_evidence = next(e for e in result.evidence if "9 months stale" in e.quote)
    assert stale_evidence.freshness.status == FreshnessStatus.STALE


def test_planted_truth_effects_appear_as_signals():
    result = generate_pulsestack_feedback(SCENARIO, RUN_ID, seed=SCENARIO["seed"])
    texts = [s.claim_text for s in result.signals]
    assert any("few false alarms" in t for t in texts)
    assert any("evaluating alternatives" in t for t in texts)
    assert any("multi-service setup confusion" in t for t in texts)


def test_spam_items_are_low_confidence_and_unsupported():
    result = generate_pulsestack_feedback(SCENARIO, RUN_ID, seed=SCENARIO["seed"])
    spam = [e for e in result.evidence if e.claim_support.status == "unsupported"]
    assert len(spam) == SCENARIO["noise"]["spam_or_low_signal"]
    assert all(e.claim_support.confidence < 0.5 for e in spam)


def test_every_signal_evidence_id_resolves():
    result = generate_pulsestack_feedback(SCENARIO, RUN_ID, seed=SCENARIO["seed"])
    evidence_ids = {e.id for e in result.evidence}
    for signal in result.signals:
        assert set(signal.evidence_ids) <= evidence_ids
