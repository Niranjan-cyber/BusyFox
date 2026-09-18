# Opportunity Engine — frontend

React + TypeScript + Vite. Lane B owns this directory: the five P0 screens (PRD §16.1), the
evidence drawer, the design system and the Amplify Hosting pipeline.

## Commands

| Command | What it does |
| --- | --- |
| `npm install` | Install dependencies |
| `npm run dev` | Dev server with HMR |
| `npm run lint` | oxlint |
| `npm test` | vitest — rule-table, guardrail and render tests |
| `npm run build` | `tsc -b` then `vite build` — the gate Amplify runs |
| `npm run preview` | Serve the production build locally |

## Layout

```
src/
  api/          API client; fixture fallback when no live endpoint is configured
  components/
    common/     Shared primitives (labels, chips, meters, cards, buttons)
    layout/     App shell and navigation
    inbox/      Screen 3 components
    polarity/   Polarity split bar (screen 1's signature moment)
  fixtures/     Committed fixture payloads, shaped per PRD §14
  screens/      One folder per P0 screen
  styles/       theme.css — the design tokens every screen imports
  types/        Entity + API types mirroring PRD §14
```

## Routes

Hash routing, so Amplify needs no rewrite rule for deep links.

| Route | Screen |
| --- | --- |
| `#/business` | Screen 1 — Business & feedback (default) |
| `#/inbox` | Screen 3 — Opportunity inbox |
| `#/tokens` | Design-token reference. Not a product screen; it computes the palette's contrast ratios at load, so a token change that breaks a pairing shows up as a FAIL |

Screens 2, 4 and 5 are listed in the nav as not built yet rather than linking nowhere.

## Configuration

`VITE_API_BASE_URL` points the client at the deployed API Gateway stage. When it is unset the
client serves committed fixtures instead — and the UI labels them `DEMO FIXTURE`, per the
Live → Cached → Demo Fixture ladder in PRD §7.2. Fixture data is never shown as if it were live.

## Rendering rules that are not optional

These come from `AGENTS.md` and the PRD; a change that breaks one of them is a bug, not a preference.

- No composite opportunity score. Evidence confidence, potential value and priority render as
  three visually separate fields (§13.1).
- Every claim reaching the UI carries an `OBSERVED` / `INFERRED` / `ASSUMED` label (§13.3).
- Every source carries its retrieval level: `LIVE RESEARCH` / `CACHED VERIFIED SOURCE` /
  `DEMO FIXTURE` (§7.2). Never substitute silently.
- Potential value is always a range with its assumptions visible and editable (§13.2).
- The provenance chain SourceDocument → Evidence → Claim → Opportunity stays clickable.
