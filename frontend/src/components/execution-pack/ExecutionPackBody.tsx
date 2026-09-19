import type { ExecutionPack, Opportunity } from '../../types/entities'
import './ExecutionPackBody.css'

/**
 * Screen 5's content (§16.1): offer, proposal, and outreach drafts. Pure/presentational so it
 * can be render-tested against fixture data without wiring up the screen's fetches — same split
 * as `OpportunityCard`/`EvidenceCheckDiagram` from the screens that fetch them.
 *
 * `outreach_policy_checked` is rendered per draft rather than assumed: §16.1 names this screen
 * as "the only place outreach_policy (§18.1) ... is shown end-to-end", so the check itself has
 * to be visible, not just its effect.
 */

const STATUS_LABEL: Record<ExecutionPack['status'], string> = {
  draft: 'Draft — not sent',
  sent: 'Sent',
}

function OutreachDraftItem({
  draft,
  opportunityId,
  strengths,
}: {
  draft: ExecutionPack['outreach_drafts'][number]
  opportunityId: string
  strengths: Opportunity['strengths_it_builds_on']
}) {
  // The proof point is a `strengths_it_builds_on` signal id (§18.1's policy only lets outreach
  // cite a verified strength), so this is a lookup into data the screen already has, not a
  // second fetch — the same "traceable, not a second source of truth" choice screen 4 makes for
  // its own strengths/pains lists.
  const proofPoint = strengths.find((strength) => strength.signal_id === draft.proof_point_signal_id)

  return (
    <li className="outreach-draft">
      <div className="outreach-draft-head">
        <span className="outreach-channel">{draft.channel}</span>
        <span
          className={
            draft.outreach_policy_checked ? 'outreach-check outreach-check-pass' : 'outreach-check outreach-check-fail'
          }
        >
          <span aria-hidden="true">{draft.outreach_policy_checked ? '✓' : '✗'}</span> outreach policy checked
          (§18.1)
        </span>
      </div>
      <p className="outreach-draft-text">{draft.draft}</p>
      <a className="outreach-proof-point" href={`#/opportunities/${opportunityId}`}>
        Proof point: {proofPoint ? proofPoint.reason : `source signal ${draft.proof_point_signal_id}`} →
      </a>
    </li>
  )
}

export function ExecutionPackBody({ pack, opportunity }: { pack: ExecutionPack; opportunity: Opportunity }) {
  return (
    <div className="execution-pack-body">
      <div className="execution-pack-block">
        <h3>Offer</h3>
        <p>{pack.offer}</p>
      </div>

      <div className="execution-pack-block">
        <h3>Proposal</h3>
        <p>{pack.proposal}</p>
      </div>

      <div className="execution-pack-block">
        <h3>Outreach drafts</h3>
        <p className="execution-pack-status">{STATUS_LABEL[pack.status]}</p>
        {pack.outreach_drafts.length === 0 ? (
          <p className="execution-pack-empty">
            No outreach draft yet — this opportunity has no verified strength to cite (§18.1).
          </p>
        ) : (
          <ul className="outreach-drafts">
            {pack.outreach_drafts.map((draft, index) => (
              <OutreachDraftItem
                key={`${draft.channel}-${index}`}
                draft={draft}
                opportunityId={opportunity.id}
                strengths={opportunity.strengths_it_builds_on}
              />
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
