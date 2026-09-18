import { ClaimLabel } from '../common/Labels'
import { exactUsd, usdRange } from '../../lib/format'
import './GoalBar.css'

/**
 * Screen 3's signature element: what has been identified, against what the business needs.
 *
 * The bar shows a range, not a point, and the range is capped visually at the goal so the
 * fill can never read as "we found more than you need" when the high end merely exceeds it —
 * the figure above states the real number either way.
 */
export function GoalBar({
  goalChangeUsd,
  horizonDays,
  low,
  high,
  lowShare,
  highShare,
}: {
  goalChangeUsd: number
  horizonDays: number
  low: number
  high: number
  lowShare: number
  highShare: number
}) {
  const lowPercent = Math.min(lowShare, 1) * 100
  const highPercent = Math.min(highShare, 1) * 100

  return (
    <section className="goal-bar" aria-labelledby="goal-bar-heading">
      <div className="goal-bar-head">
        <h2 id="goal-bar-heading">
          {exactUsd(goalChangeUsd)} additional MRR in {horizonDays} days
        </h2>
        <p className="goal-bar-identified">
          <span className="tabular">{usdRange(low, high)} MRR</span> identified so far
          <ClaimLabel value="ASSUMED" />
        </p>
      </div>

      <div
        className="goal-track"
        role="img"
        aria-label={`Identified potential ranges from ${exactUsd(low)} to ${exactUsd(high)} against a goal of ${exactUsd(goalChangeUsd)} additional MRR`}
      >
        <div className="goal-fill-high" style={{ width: `${highPercent}%` }} />
        <div className="goal-fill-low" style={{ width: `${lowPercent}%` }} />
      </div>

      <p className="goal-bar-note">
        Blocked opportunities are not counted towards this range — their value sits behind a
        product fix, so counting it here would overstate what is reachable today.
      </p>
    </section>
  )
}
