# Learning Log — Opportunity Engine

Kept from Day 1 per the event rules (learning is a scored judging criterion). One entry per day, added as it happens — not reconstructed from memory on Day 4.

## Day 1 — Sept 17, 2026

**Eligibility & registration**
- Confirmed both teammates meet the eligibility bar (university students in India, 18+) before any other work started.
- Registered and verified student status on WeMakeDevs and AWS Builder Center.
- *(Fill in: any friction hit during verification — e.g. delay between account creation and verification clearing, which step took longest. Whoever did this step knows the specifics; worth a line here since "learning demonstrated" is explicitly judged.)*

**AWS/Bedrock access**
- Confirmed Bedrock model access for both Claude Haiku 4.5 and Sonnet 4.6.
- *(Fill in: which region/inference profile ended up working, and whether the default one was blocked — this is exactly the kind of concrete technical learning judges want to see, and it's only known to whoever ran the check.)*

**Planning & tooling**
- Locked the two-person workflow before writing any product code: split by architectural layer (backend/agents vs. frontend/screens) rather than by day, with a third floating lane for the extra AI subscription — the PRD's own Part B already argues for a contracts-first split, so this wasn't a novel idea, just a deliberate decision to follow it rather than default to a day-based split.
- Writing `tasks/plan.md` before touching code surfaced a gap the PRD doesn't spell out: §15 names four API endpoints, but the five P0 screens need more than that (business profile, opportunity list, opportunity detail, execution pack aren't explicitly listed). Better to find that gap during planning than mid-Day-2 when the frontend is already blocked on it.
- Running `/graphify` on the whole repo (rather than scoping it) pulled in the vendored engineering-skill library twice over (`.agents/skills/` and `.claude/skills/`, same content) — 62 of 73 detected files were generic skill docs, not product content. Scoping the run to the 7 project-specific files was the actual lesson: a knowledge-graph tool is only as useful as the corpus you point it at.
- The `ponytail` plugin was enabled in project settings but didn't resolve through the Skill tool mid-session — a reminder that enabling a plugin and having it actually usable in the current session aren't the same event; worth checking early rather than assuming.

## Day 2 — Sept 18, 2026

**Lane B — design tokens and screens 1 & 3**
- The brief's palette and WCAG AA disagree in one specific place, and it only showed up once
  the ratios were computed rather than eyeballed: `#456C6F` secondary text on the `#CBD5D4`
  page background is 3.9:1, under the 4.5:1 body-text bar. Fixed by adding one lighter tint of
  the same colour (`#E4EAE9`) as the card surface, which puts the same text at 4.75:1 without
  introducing a hue the brief didn't ask for. `#7EAEA6` as text on the light background is
  1.65:1 — unusable — so the accent is a fill colour on light and a text colour only on dark.
  The token names encode that (`--on-accent`, `--accent-on-dark`) so the failing pairing is
  hard to reach by accident, and the `#/tokens` page recomputes every pairing at load instead
  of trusting the numbers in the design doc.
- The PRD contradicts itself on goal coverage. §13.2 defines it as monthly value × 3 for the
  90-day horizon ÷ goal gap, but §1.3's inbox mock-up compares the monthly sums to the $15k
  MRR goal directly ($6.5k + $4.1k against $15k, no ×3). ×3 is also dimensionally odd, since
  the goal is itself a monthly rate. Built §1.3's version because that's the screen being
  rendered, and left the conflict named in `grouping.ts` rather than quietly picking a side —
  needs a ruling at stand-up.
- §13.1's priority rule table covers HIGH and LOW explicitly but never says which §1.3 section
  MEDIUM belongs to. Grouped it with LOW under "additional hypotheses (lower confidence)",
  since the alternative puts medium-confidence items under a heading that says
  "high-confidence". Also flagged in code rather than settled silently.
- Writing the "no composite score" guardrail as an actual test — asserting no rendered card
  carries a score-shaped field, and that every fixture priority matches the rule table — was
  cheap and caught nothing today, which is the point: it will catch it on Day 3 when someone
  is adding the detail screen at speed. The `signals[]`-only guarantee is enforced the same
  way, as a `@ts-expect-error` that fails the typecheck if the field ever becomes assignable.
- Checking the palette's contrast once, for the light background, was not enough. A review pass
  caught `#456C6F` used as text on the dark nav rail at 2.6:1 — the same colour that is fine on a
  card. The lesson was less "check contrast" than "check it per surface": a token that passes
  somewhere gets reused everywhere. The fix was a second derived step (`--on-slate-muted`) and,
  more usefully, moving the whole contrast table out of a doc and into `npm test`, where it
  parses `theme.css` and fails the build. The page that checks it in a browser only helps when
  somebody opens it.

## Day 3 — Sept 19, 2026

*(Not yet written.)*

## Day 4 — Sept 20, 2026

*(Not yet written.)*
