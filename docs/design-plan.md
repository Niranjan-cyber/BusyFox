# Design plan — Opportunity Engine

Produced with the `frontend-design` skill (`.claude/skills/frontend-design/SKILL.md`), two passes:
a plan, then a critique against the brief before any code was written. This file is the record of
that process and the rationale behind `frontend/src/styles/theme.css`.

## The brief

Font: **Outfit** (400/500/600/700). Palette, exactly five values:

| Hex | Name in the brief |
| --- | --- |
| `#081419` | Deepest oceanic night |
| `#0E2A32` | Dark petrol slate |
| `#456C6F` | Storm slate |
| `#7EAEA6` | Electric seafoam mint |
| `#CBD5D4` | Pale misty silver |

Light primary background (`#CBD5D4`), `#081419` primary text, `#0E2A32` for dark surfaces,
`#456C6F` for secondary text/borders, `#7EAEA6` as the accent. Not dark overall. No random
colours, no excessive gradients, no excessive glassmorphism, no excessive pill shapes. Clean,
modern, technical, professional. Responsive.

The skill's own rule settles the tension between its "make distinctive choices" mandate and a
brief this specific: *"Where the brief pins down a visual direction, follow it exactly — the
brief's own words always win."* Type and colour are therefore fixed. The design work is in
structure, hierarchy, and how the product's label systems are encoded.

## Subject matter

The product reads public discussions and simulated customer feedback and returns growth
opportunities that are *traceable back to the quote that caused them*. The audience is a founder
deciding what to do next, and a technical judge checking whether the claims hold up. The primary
job of the interface is therefore **not** persuasion — it is showing its work. Every screen is a
chain of custody: source to evidence to claim to opportunity.

That points at instrument panels and lab notebooks rather than a marketing dashboard. The nearest
honest vernacular is a **survey instrument**: dense, measured, legible at a glance, nothing
decorative, every reading labelled with how it was obtained.

## Color

Seven tokens. Five are the brief's; the other two are steps between them, added for contrast
reasons documented below — not new hues.

| Token | Hex | Role |
| --- | --- | --- |
| `--bg` | `#CBD5D4` | Page background |
| `--surface` | `#E4EAE9` | Cards, panels, rows (a lighter step of `--bg`, same hue family) |
| `--ink` | `#081419` | Primary text; also the text *on* accent fills |
| `--slate` | `#0E2A32` | Dark surfaces: header, nav rail, drawer chrome |
| `--muted` | `#456C6F` | Borders, dividers, icons, secondary text on `--surface` |
| `--accent` | `#7EAEA6` | Fills, active states, focus ring; text only on dark surfaces |
| `--on-slate-muted` | `#899B9B` | De-emphasised text on `--slate` (`--bg` mixed 65% into `--slate`) |

### Measured contrast (WCAG 2.1 AA)

| Pair | Ratio | Verdict |
| --- | --- | --- |
| `--ink` on `--bg` | 12.5:1 | Pass, any size |
| `--ink` on `--surface` | 15.3:1 | Pass, any size |
| `--bg` text on `--slate` | 10.0:1 | Pass, any size |
| `--accent` text on `--slate` | 6.1:1 | Pass — accent is a text colour **only** here |
| `--ink` on `--accent` fill | 7.5:1 | Pass — this is how accent buttons work |
| `--muted` on `--surface` | 4.8:1 | Pass for body text |
| `--muted` on `--bg` | 3.9:1 | **Large text (24px+, or 18.7px+ bold), borders and icons only** |
| `--accent` on `--bg` | 1.65:1 | **Fails. Accent is never text on the light background.** |
| `--accent` on `--surface` | 2.03:1 | **Fails.** Accent chips are a fill with `--ink` text, never coloured text. |
| `--on-slate-muted` on `--slate` | 5.1:1 | Pass — the only de-emphasised text colour for dark surfaces |
| `--muted` on `--slate` | 2.6:1 | **Fails.** `--muted` is a light-surface colour; on the rail it is unreadable. |

Two consequences are wired into the token names so they are hard to get wrong: `--accent` is
paired with `--on-accent` for fills, and `--accent-on-dark` is the only accent-as-text token.
Small secondary text lives on `--surface`, not directly on `--bg`; where it must sit on `--bg`,
it uses `--slate`.

`--surface` and `--on-slate-muted` are the two additions to the five, and both exist for the
same reason: the palette's mid tone, `#456C6F`, is not readable as small text against either the
page background or the dark rail. `--surface` is the more interesting of the two. Without it, `#456C6F` secondary text on
`#CBD5D4` sits at 3.9:1 and fails AA for body copy — and secondary text is unavoidable on screens
built out of metadata. A lighter step of the same colour fixes it at 4.75:1 without introducing a
hue the brief did not ask for.

### Semantic states

Two additions, used as text, borders and bar fills only, and never as the sole carrier of
meaning (every state also carries a word or an icon):

| Token | Hex | Contrast on `--surface` | Used for |
| --- | --- | --- | --- |
| `--positive` | `#7EAEA6` (the accent, reused) | fill only | Verified, "what customers love", passing checks |
| `--warning` | `#8A5A1E` | 4.8:1 | Blocked / fix-first only |
| `--negative` | `#A8473C` | 4.8:1 | "What customers complain about", rejected ideas |

`--warning` and `--negative` are deep and desaturated so they sit inside the palette's muted
register rather than reading as generic alert colours — and so they clear 4.5:1 as *text* on
`--surface`. They are text, border and bar-fill colours only; neither is ever a background behind
small text, because at that size neither passes against `--ink` or `--bg`.

This produces a second, useful shape distinction: a positive chip is an accent **fill** with
`--ink` text (7.5:1), while warning and negative chips are **outlined** — `--surface` background,
1px border and text in the state colour. Filled versus outlined carries the meaning even in
greyscale, so colour is never the sole signal.

## Type

One family: **Outfit**, loaded from Google Fonts with a `system-ui` fallback, `display=swap`.
No second family — the skill allows one or two, and a second would compete with the density.

| Step | Size / line-height | Weight | Use |
| --- | --- | --- | --- |
| `--text-display` | 2.25rem / 1.15 | 600 | Screen title |
| `--text-title` | 1.5rem / 1.25 | 600 | Section heading |
| `--text-heading` | 1.125rem / 1.35 | 600 | Card heading |
| `--text-body` | 1rem / 1.55 | 400 | Body |
| `--text-small` | 0.875rem / 1.45 | 400 | Secondary |
| `--text-micro` | 0.75rem / 1.3 | 500 | Labels and chips |

Numbers use `font-variant-numeric: tabular-nums` everywhere a figure appears, because this product
puts money ranges in vertical lists and they have to align. Body measure caps at 68ch.

## Layout

Left rail on `--slate` above 768px, collapsing to a bottom bar below it. Content on `--bg`, with
cards on `--surface` separated by 1px `--muted` borders at 30% alpha.

```
>= 1024px                                 < 768px
+------+--------------------------------+ +------------------------+
| RAIL | Screen title                   | | Screen title           |
|      | ------------------------------ | | ---------------------- |
| [1]* | +----------------------------+ | | +--------------------+ |
| [2]  | | card                       | | | | card               | |
| [3]  | +----------------------------+ | | +--------------------+ |
| [4]  | +----------------------------+ | | +--------------------+ |
| [5]  | | card                       | | | | card               | |
|      | +----------------------------+ | | +--------------------+ |
+------+--------------------------------+ | [1] [2] [3] [4] [5]    |
                                          +------------------------+
```

Content is left-aligned throughout — these are scannable records, and centred text would fight
the eye down a list of ranges and labels. Spacing is a 4px scale (4/8/12/16/24/32/48/64); nothing
off-scale. Radius is deliberately stratified rather than uniform: 2px on chips and labels, 4px on
cards and buttons, 0 on bars and meters. Nothing is pill-shaped. One shadow exists, for the
evidence drawer only, because it is the one element that genuinely floats.

## Principles

1. **The label is part of the data.** Every claim, every source, every estimate renders with its
   provenance tag. There is no "clean" view that strips them.
2. **Three numbers, three shapes.** Priority, evidence confidence and potential value are
   deliberately given different visual forms — a tier chip, a stepped 3-dot meter, a range bar —
   so they cannot be misread as one score. This is PRD §13.1 enforced by the design system rather
   than by convention.
3. **Structure over decoration.** Borders, rules and alignment carry the information hierarchy.
   No gradient washes, no glass, no drop shadows except the drawer.
4. **Quiet surface, one loud element per screen.** Screen 1's is the polarity split bar; screen
   3's is the goal bar. Everything else stays in the muted register.
5. **Ranges, never point numbers.** Any modelled figure renders as a range with its assumptions
   reachable in one click.

## Pass 2 — critique against the brief

Checked the pass-1 plan against the skill's list of AI-design tells, and against what a generic
"analytics dashboard" prompt would have produced. Four things changed:

1. **Differentiate the three numbers by *shape*, not colour.** Pass 1 had priority High/Medium/Low
   as a red/amber/green chip set — the generic default, and it would have needed three colours the
   brief does not have. Encoding the three metrics as three different *forms* (chip / dot meter /
   range bar) is both more honest to §13.1 and keeps the palette at five. This is the single
   biggest change from the first pass.
2. **Dropped the all-caps eyebrow labels.** Pass 1 had tracked-out caps above each section — named
   explicitly in the skill as a tell, and the PRD's own label vocabulary (`OBSERVED`, `LIVE
   RESEARCH`) already uses caps. Reserving caps for the label systems makes them mean something.
3. **Stratified the radii.** Pass 1 used one 8px radius on everything, which the skill calls the
   SaaS-card kit. Chips, cards and bars now have different radii, matching their weight.
4. **Cut the numbered markers.** Pass 1 numbered the inbox sections 01/02/03. The four sections
   are categories, not a sequence, so the numbering encoded nothing. The section headers carry
   their own meaning (high-confidence / blocked / hypotheses / rejected) without it.

What survived the critique unchanged: the survey-instrument direction, the left rail, the
left-aligned dense layout, and the one-loud-element-per-screen rule. Those come from the subject
matter — a product whose whole thesis is traceability — rather than from a default.
