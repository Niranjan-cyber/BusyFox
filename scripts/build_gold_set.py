"""Task 24 prep — builds the raw, unlabelled corpus for gold-set labelling:
80 simulated feedback items (balanced positive/negative/mixed across the
§9.1 aspect taxonomy) + 20 real competitor snippets (live App Store +
Product Hunt fetches). Writes two identical blank labelling sheets so
Niranjan and Swarali can label independently before comparing, per Task 24's
own requirement ("before either sees the other's labels").

This script does NOT label anything — that's the point of a gold set. It
only assembles the text to be labelled.

ponytail: PulseStack's own generator (backend/simulator/pulsestack.py)
deliberately never grew bulk-volume generation ("add bulk noise generation
once that pipeline needs volume to filter against") — Task 24 is that need,
so the 80-item bulk generator lives here rather than in the core simulator,
since eval-corpus volume isn't part of the production pipeline's job.
"""

from __future__ import annotations

import csv
import json
import os
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

_ASPECTS = [
    "onboarding", "pricing_value", "reliability", "integrations", "support",
    "documentation", "performance", "alert_noise", "ease_of_use",
    "feature_completeness", "migration_friction",
]
_PERSONAS = ["founder", "backend_engineer", "sre_devops", "on_call_lead"]

_TEMPLATES = {
    "onboarding": {
        "positive": "Got the whole team set up on PulseStack in under an hour — {persona} said the {n}-step onboarding flow was the smoothest of any monitoring tool we've tried.",
        "negative": "{persona} gave up halfway through PulseStack's onboarding wizard after it asked for {n} separate API keys with no explanation of what each one does.",
        "mixed": "PulseStack's onboarding got us to a working dashboard fast, but {persona} still had to read the docs for {n} minutes to figure out the alerting setup.",
    },
    "pricing_value": {
        "positive": "{persona} says PulseStack's flat ${n}/month team plan is a no-brainer compared to what we were paying per-seat elsewhere.",
        "negative": "Our bill jumped by ${n} last month with no warning — {persona} is now shopping around for something with predictable pricing.",
        "mixed": "The base plan is fair, but {persona} was surprised the extra ${n}/month add-on for longer retention wasn't mentioned upfront.",
    },
    "reliability": {
        "positive": "{n} days of uptime and zero missed incidents — {persona} trusts PulseStack more than the tool we migrated from.",
        "negative": "PulseStack's own dashboard went down for {n} minutes last week, right when {persona} needed it most during an incident.",
        "mixed": "Reliability has been solid for {n} weeks straight, though {persona} noticed one brief blip during a deploy that wasn't explained.",
    },
    "integrations": {
        "positive": "{persona} wired up Slack, PagerDuty and our CI in under {n} minutes — the integration list covers everything we use.",
        "negative": "{persona} needed a integration with our internal ticketing system and PulseStack has {n} pre-built connectors, none of which fit.",
        "mixed": "Most integrations just worked, but {persona} had to write a small script to bridge the {n}th tool we use that isn't supported.",
    },
    "support": {
        "positive": "{persona} got a real answer from support in under {n} minutes on a Sunday — that responsiveness alone would keep us as customers.",
        "negative": "Opened a ticket {n} days ago and {persona} still hasn't heard back from PulseStack support.",
        "mixed": "Support resolved {persona}'s issue but it took {n} back-and-forth emails to get there.",
    },
    "documentation": {
        "positive": "{persona} says the API docs are the best-written of any observability vendor we've evaluated — found what we needed in {n} minutes.",
        "negative": "The docs page for the alerting API hasn't been updated in {n} months and still references a deprecated endpoint, which cost {persona} an afternoon.",
        "mixed": "The getting-started docs are great, but {persona} couldn't find anything on the {n} advanced config options in the dashboard.",
    },
    "performance": {
        "positive": "Query latency on our {n}-node cluster's dashboard is consistently under a second — {persona} never has to wait.",
        "negative": "{persona} says the dashboard takes {n} seconds to load once we crossed our current node count, which is unacceptable during an incident.",
        "mixed": "Performance is fine most days, but {persona} noticed it slows down noticeably around the {n}th concurrent dashboard viewer.",
    },
    "alert_noise": {
        "positive": "{persona} says alert volume dropped by {n}% after switching, with zero false positives so far this month.",
        "negative": "{persona} is drowning in {n} duplicate alerts a night from the same underlying issue and is close to muting the channel entirely.",
        "mixed": "The low-noise alerting is a real improvement, but {persona} still gets {n} redundant pages for planned maintenance windows.",
    },
    "ease_of_use": {
        "positive": "{persona} taught a new hire the whole dashboard in {n} minutes — nothing needed explaining twice.",
        "negative": "It took {persona} {n} clicks just to filter the dashboard by service, which feels like it should be one step.",
        "mixed": "The dashboard is intuitive for the basics, but {persona} needed {n} tries to find where custom views are saved.",
    },
    "feature_completeness": {
        "positive": "{persona} says PulseStack covers everything our old {n}-tool stack did, in one place.",
        "negative": "We're still missing {n} features we relied on with our previous vendor, and {persona} has had to keep a second tool running just for those.",
        "mixed": "Core monitoring is complete, but {persona} counted {n} smaller features (custom SLOs, saved filters) that are still on the roadmap.",
    },
    "migration_friction": {
        "positive": "{persona} migrated {n} services over a weekend with the provided import tool — barely any manual work.",
        "negative": "{persona} is {n} weeks into migrating off our old vendor and PulseStack's import tool still can't handle our alert-rule format.",
        "mixed": "Most of the migration was painless, but {persona} had to hand-rewrite {n} legacy alert rules that the importer choked on.",
    },
}

_POLARITIES = ("positive", "negative", "mixed")


def build_simulated_items(count: int, seed: int) -> list[dict]:
    """`count` deterministic, template-based feedback items, balanced across
    the three polarity buckets and cycling through every §9.1 aspect."""

    rng = random.Random(seed)
    items = []
    for i in range(count):
        aspect = _ASPECTS[i % len(_ASPECTS)]
        polarity = _POLARITIES[i % len(_POLARITIES)]
        template = _TEMPLATES[aspect][polarity]
        text = template.format(persona=rng.choice(_PERSONAS), n=rng.randint(2, 45))
        items.append({"item_id": f"sim_{i + 1:03d}", "text": text, "source": "simulated"})
    rng.shuffle(items)
    return items


def build_real_items() -> list[dict]:
    """Live App Store + Product Hunt fetches for named competitors —
    real customer text, not simulated. Requires PRODUCT_HUNT_TOKEN in the
    environment; App Store RSS needs no key."""

    from backend.collectors.app_store import fetch_app_store_signals
    from backend.collectors.producthunt import fetch_producthunt_signals

    items = []
    app_store_signals = fetch_app_store_signals("1391380318", "Datadog", "run_gold_prep")
    for s in app_store_signals:
        items.append({"item_id": f"real_appstore_{s.id}", "text": s.claim_text, "source": "real:app_store"})

    token = os.environ.get("PRODUCT_HUNT_TOKEN")
    if token:
        ph_signals = fetch_producthunt_signals("sentry", "Sentry", "run_gold_prep", token)
        for s in ph_signals:
            items.append({"item_id": f"real_ph_{s.id}", "text": s.claim_text, "source": "real:product_hunt"})
    else:
        print("PRODUCT_HUNT_TOKEN not set — skipping Product Hunt, App Store alone may fall short of 20.")

    return items[:20]


def write_blank_sheet(path: Path, items: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["item_id", "source", "text", "aspect", "polarity", "intents", "segment_hints", "evidence_span"])
        for item in items:
            writer.writerow([item["item_id"], item["source"], item["text"], "", "", "", "", ""])


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "tasks" / "gold_set"
    out_dir.mkdir(parents=True, exist_ok=True)

    simulated = build_simulated_items(80, seed=24)
    real = build_real_items()
    print(f"simulated: {len(simulated)}, real: {len(real)}")

    all_items = simulated + real
    (out_dir / "items.json").write_text(json.dumps(all_items, indent=2), encoding="utf-8")

    write_blank_sheet(out_dir / "labels_niranjan.csv", all_items)
    write_blank_sheet(out_dir / "labels_swarali.csv", all_items)
    print(f"Wrote {out_dir / 'items.json'}, labels_niranjan.csv, labels_swarali.csv")
    print("Label independently — don't open the other person's CSV until both are done.")


if __name__ == "__main__":
    main()
