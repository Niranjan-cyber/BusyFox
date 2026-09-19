import { useState } from 'react'
import type { EvidenceConfidence, EvidenceDiversity, Priority, ValueModel } from '../../types/entities'
import { count, usdRange } from '../../lib/format'
import { ClaimLabel } from './Labels'
import './Metrics.css'

/**
 * Priority, evidence confidence and potential value — §13.1's three separate numbers.
 *
 * They are deliberately given three different forms: a tier chip, a stepped meter and a
 * range bar. There is no composite score in this product, and giving the three readings the
 * same visual treatment is how a composite one gets invented by accident. Keep them distinct.
 */

const PRIORITY_EXPLANATION: Record<Priority, string> = {
  High: 'Evidence confidence HIGH, no fix-first blocker',
  Medium: 'Evidence confidence MEDIUM, no fix-first blocker',
  Low: 'Evidence confidence LOW, no fix-first blocker',
  Blocked: 'A product issue has to be fixed before this can be sold',
}

export function PriorityChip({ value }: { value: Priority }) {
  return (
    <span className={`priority priority-${value.toLowerCase()}`} title={PRIORITY_EXPLANATION[value]}>
      {value === 'Blocked' ? 'Blocked' : `${value} priority`}
    </span>
  )
}

const CONFIDENCE_STEPS: Record<EvidenceConfidence, number> = { LOW: 1, MEDIUM: 2, HIGH: 3 }

/** A stepped meter, not a percentage — the underlying value is a tier, and pretending
    otherwise would imply a precision the Evidence Check does not produce (§12). */
export function ConfidenceMeter({ value }: { value: EvidenceConfidence }) {
  const filled = CONFIDENCE_STEPS[value]
  return (
    <span className="confidence">
      <span className="confidence-label">Evidence confidence</span>
      <span className="confidence-value">{value}</span>
      {/* The tier is already stated in text beside this, so the steps are decoration. */}
      <span className="confidence-steps" aria-hidden="true">
        {[1, 2, 3].map((step) => (
          <span key={step} className={step <= filled ? 'step step-on' : 'step'} />
        ))}
      </span>
    </span>
  )
}

/**
 * The value range with its inputs visible (§13.2). Never a bare point number, and the
 * headline figure carries the ASSUMED tag because it is a model output, not an observation.
 *
 * Canonical `ValueAssumption` (§13.2) carries a qualitative `description` + its own
 * OBSERVED/ASSUMED/INFERRED `label`, not the numeric accounts/conversion/ARPA breakdown a
 * calculator would need — that structured data doesn't exist in the contract, so this renders
 * what the contract actually has rather than reconstructing arithmetic from nothing.
 */
export function ValueRange({ value }: { value: ValueModel }) {
  return (
    <div className="value">
      <div className="value-headline">
        <span className="value-amount tabular">
          {usdRange(value.monthly_usd.low, value.monthly_usd.high)} MRR
        </span>
        <ClaimLabel value="ASSUMED" />
      </div>
      <details className="value-details">
        <summary>Based on</summary>
        <ul>
          {value.assumptions.map((assumption) => (
            <li key={assumption.key}>
              {assumption.description} <ClaimLabel value={assumption.label} />
            </li>
          ))}
        </ul>
      </details>
    </div>
  )
}

/**
 * §11.2's source-diversity readout. Shared between the inbox card and screen 4's detail view —
 * same three counts and risk flag, no separate summary invented for the detail screen.
 */
export function EvidenceDiversityReadout({ diversity }: { diversity: EvidenceDiversity }) {
  return (
    <p className="diversity">
      Source diversity: <span className="tabular">{count(diversity.source_kind_count)}</span>{' '}
      kinds, <span className="tabular">{count(diversity.domain_count)}</span> domains,{' '}
      <span className="tabular">{count(diversity.author_count)}</span> authors · underlying-event
      risk {diversity.underlying_event_risk}
    </p>
  )
}

/**
 * Screen 4's editable value range (Task 31). The canonical `ValueAssumption` (§13.2) has no
 * numeric fields to recompute from — see Task 27's note — so this edits the headline range
 * directly, client-side only. Nothing here is sent anywhere: there is no route to save an
 * edited value model, so the edit is scoped to this browser tab for as long as the screen stays
 * open, and says so rather than implying it persisted.
 */
export function EditableValueRange({ value }: { value: ValueModel }) {
  const [low, setLow] = useState(value.monthly_usd.low)
  const [high, setHigh] = useState(value.monthly_usd.high)
  const edited = low !== value.monthly_usd.low || high !== value.monthly_usd.high

  return (
    <div className="value value-editable">
      <div className="value-headline">
        <span className="value-amount tabular value-input-group">
          $
          <input
            className="value-input"
            type="number"
            min={0}
            inputMode="numeric"
            aria-label="Adjust the low end of the monthly value range"
            value={low}
            onChange={(event) => setLow(Number(event.target.value))}
          />
          –$
          <input
            className="value-input"
            type="number"
            min={0}
            inputMode="numeric"
            aria-label="Adjust the high end of the monthly value range"
            value={high}
            onChange={(event) => setHigh(Number(event.target.value))}
          />{' '}
          MRR
        </span>
        <ClaimLabel value="ASSUMED" />
      </div>
      {edited ? (
        <p className="value-edited-note">
          Adjusted from the model&apos;s {usdRange(value.monthly_usd.low, value.monthly_usd.high)}{' '}
          range for this browser tab only — not saved anywhere.
        </p>
      ) : null}
      <details className="value-details" open>
        <summary>Based on</summary>
        <ul>
          {value.assumptions.map((assumption) => (
            <li key={assumption.key}>
              {assumption.description} <ClaimLabel value={assumption.label} />
            </li>
          ))}
        </ul>
      </details>
    </div>
  )
}
