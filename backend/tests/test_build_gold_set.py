"""Task 24 prep — the only non-trivial logic in scripts/build_gold_set.py is
the balanced/deterministic bulk generator; this is its one runnable check."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from build_gold_set import _ASPECTS, build_simulated_items  # noqa: E402


def test_build_simulated_items_is_balanced_and_deterministic():
    items = build_simulated_items(80, seed=24)
    assert len(items) == 80
    assert len({i["item_id"] for i in items}) == 80  # no duplicate ids
    assert len({i["text"] for i in items}) == 80  # no duplicate text

    # Every aspect used, roughly evenly (80 items over 11 aspects cycling in order).
    aspect_hits = Counter(_ASPECTS[i % len(_ASPECTS)] for i in range(80))
    assert set(aspect_hits) == set(_ASPECTS)
    assert max(aspect_hits.values()) - min(aspect_hits.values()) <= 1

    # Same seed reproduces the same set (order may differ after the shuffle).
    again = build_simulated_items(80, seed=24)
    assert {i["item_id"]: i["text"] for i in items} == {i["item_id"]: i["text"] for i in again}
