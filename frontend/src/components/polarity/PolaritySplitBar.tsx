import { count } from '../../lib/format'
import './PolaritySplitBar.css'

/**
 * Screen 1's signature moment (§16.1): one bar showing how the business's own feedback
 * splits between praise and complaint.
 *
 * This is the one loud element on the screen, so everything around it stays quiet. The
 * counts are printed on the bar itself rather than only in a legend — the split has to be
 * readable without relying on the colour difference.
 */
export function PolaritySplitBar({
  positive,
  negative,
}: {
  positive: number
  negative: number
}) {
  const total = positive + negative
  if (total === 0) {
    return <p className="polarity-empty">No feedback has been labelled for this business yet.</p>
  }

  const positiveShare = Math.round((positive / total) * 100)

  return (
    <figure className="polarity">
      <div
        className="polarity-bar"
        role="img"
        aria-label={`${positive} of ${total} labelled feedback items are positive, ${negative} are negative`}
      >
        <div className="polarity-positive" style={{ width: `${positiveShare}%` }}>
          <span className="polarity-figure tabular">{count(positive)}</span>
        </div>
        <div className="polarity-negative" style={{ width: `${100 - positiveShare}%` }}>
          <span className="polarity-figure tabular">{count(negative)}</span>
        </div>
      </div>
      <figcaption className="polarity-caption">
        {/* The counts repeat here because a lopsided split leaves one segment too narrow to
            carry its own figure — the number must stay readable at any ratio. */}
        <span>
          <span className="polarity-key polarity-key-positive" aria-hidden="true" /> Loves it
          <span className="tabular">{count(positive)}</span>
        </span>
        <span>
          <span className="polarity-key polarity-key-negative" aria-hidden="true" /> Complains
          <span className="tabular">{count(negative)}</span>
        </span>
        <span className="polarity-total tabular">{count(total)} labelled items</span>
      </figcaption>
    </figure>
  )
}
