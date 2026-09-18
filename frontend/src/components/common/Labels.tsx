import type { ClaimLabel as ClaimLabelValue, RetrievalMode } from '../../types/entities'
import './Labels.css'

/**
 * The two label systems the PRD requires at every render site.
 *
 * Both are differentiated by border treatment rather than by hue, so they survive the
 * five-colour palette, greyscale and colour-blind viewing (§13.3, §7.2).
 */

const CLAIM_DESCRIPTION: Record<ClaimLabelValue, string> = {
  OBSERVED: 'Directly backed by a verified evidence item',
  INFERRED: 'A conclusion drawn from observed evidence, not itself directly evidenced',
  ASSUMED: 'A modelling input we chose. Editable, and never evidence',
}

/** §13.3 — every claim reaching the UI is tagged. */
export function ClaimLabel({ value }: { value: ClaimLabelValue }) {
  return (
    <span
      className={`label label-${value.toLowerCase()}`}
      title={CLAIM_DESCRIPTION[value]}
    >
      {value}
    </span>
  )
}

const SOURCE_TEXT: Record<RetrievalMode, { short: string; full: string }> = {
  live: {
    short: 'LIVE RESEARCH',
    full: 'Fetched fresh during this run',
  },
  cached: {
    short: 'CACHED VERIFIED SOURCE',
    full: 'Real evidence collected earlier in this run, re-served now',
  },
  demo_fixture: {
    short: 'DEMO FIXTURE',
    full: 'Pre-collected and verified, not this run live search',
  },
}

/** §7.2 — the retrieval level is always stated, never silently substituted. */
export function SourceLabel({ mode }: { mode: RetrievalMode }) {
  const text = SOURCE_TEXT[mode]
  return (
    <span className={`label label-${mode}`} title={text.full}>
      {text.short}
    </span>
  )
}
