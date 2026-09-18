import type { EvidenceConfidence, Priority, ValueModel } from '../../types/entities'
import { usdRange } from '../../lib/format'
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
