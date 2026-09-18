import type { RejectedIdea } from '../../types/entities'
import './RejectedIdeas.css'

/**
 * Screen 3's signature moment (§16.1): a rejected idea, with the reason it was rejected.
 *
 * This is a feature, not an error log. It is what separates "the AI found six things" from
 * "the AI checked nine things and can tell you why three did not survive", so the reason is
 * always shown in full rather than summarised behind a count.
 */
export function RejectedIdeas({ ideas }: { ideas: RejectedIdea[] }) {
  if (ideas.length === 0) {
    return <p className="rejected-empty">Nothing was rejected in this run.</p>
  }

  return (
    <ul className="rejected-list">
      {ideas.map((idea) => (
        <li key={idea.id} className="rejected">
          <h3>{idea.title}</h3>
          <p className="rejected-gate">{idea.failed_gate}</p>
          <p className="rejected-reason">{idea.rejected_because}</p>
        </li>
      ))}
    </ul>
  )
}
