import type { Claim, Opportunity } from '../../types/entities'
import { Card, CardBody, CardFooter, CardHeader } from '../common/Card'
import { ClaimLabel } from '../common/Labels'
import { ConfidenceMeter, PriorityChip, ValueRange } from '../common/Metrics'
import { count } from '../../lib/format'
import './OpportunityCard.css'

/** The card from §1.4. Every line on it is either evidence-backed or labelled as not. */

const CLAIM_HEADING: Record<Claim['type'], string> = {
  why_this: 'Why this',
  why_you: 'Why you',
  why_now: 'Why now',
  mechanism: 'Mechanism',
}

const CLAIM_ORDER: Claim['type'][] = ['why_this', 'why_you', 'why_now', 'mechanism']

function ClaimRow({ claim }: { claim: Claim }) {
  return (
    <div className="claim">
      <div className="claim-head">
        <span className="claim-type">{CLAIM_HEADING[claim.type]}</span>
        <ClaimLabel value={claim.label} />
        {claim.status === 'hypothesis' ? (
          <span className="claim-status" title="Passed with capped confidence (§11.2)">
            hypothesis
          </span>
        ) : null}
      </div>
      <p className="claim-text">{claim.text}</p>
    </div>
  )
}

export function OpportunityCard({
  opportunity,
  claims,
}: {
  opportunity: Opportunity
  claims: Claim[]
}) {
  const ordered = CLAIM_ORDER.map((type) =>
    claims.find((claim) => claim.opportunity_id === opportunity.id && claim.type === type),
  ).filter((claim): claim is Claim => claim !== undefined)

  const diversity = opportunity.evidence_diversity
  const blocked = opportunity.priority === 'Blocked'

  return (
    <Card tone={blocked ? 'blocked' : 'default'}>
      <CardHeader>
        <h3>{opportunity.title}</h3>
        <PriorityChip value={opportunity.priority} />
      </CardHeader>

      <CardBody>
        {/* The three readings of §13.1, laid out so they read as three separate things. */}
        <div className="readings">
          <ConfidenceMeter value={opportunity.evidence_confidence} />
          <div className="reading-value">
            <span className="reading-label">Potential value</span>
            <ValueRange value={opportunity.value} />
          </div>
        </div>

        <div className="claims">{ordered.map((claim) => <ClaimRow key={claim.id} claim={claim} />)}</div>

        {opportunity.fit.length > 0 ? (
          <div className="fit">
            <h4>Your fit</h4>
            <ul>
              {opportunity.fit.map((item) => (
                <li key={item.key}>
                  <span aria-hidden="true">✓</span> {item.label}
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        {opportunity.pains_to_fix_first.length > 0 ? (
          <div className="fix-first">
            <h4>Fix first</h4>
            <ul>
              {opportunity.pains_to_fix_first.map((pain) => (
                <li key={pain.signal_id}>{pain.reason}</li>
              ))}
            </ul>
          </div>
        ) : null}

        <div className="what-to-do">
          <h4>What to do</h4>
          <p>{opportunity.what_to_do}</p>
        </div>

        <p className="diversity">
          Source diversity: <span className="tabular">{count(diversity.source_kind_count)}</span>{' '}
          kinds, <span className="tabular">{count(diversity.domain_count)}</span> domains,{' '}
          <span className="tabular">{count(diversity.author_count)}</span> authors · underlying-event
          risk {diversity.underlying_event_risk}
        </p>
      </CardBody>

      <CardFooter>
        <p className="pending-controls">
          The evidence chain (Claim → Evidence → Source) and editable assumptions open on the
          opportunity detail screen, which lands on day 3.
        </p>
      </CardFooter>
    </Card>
  )
}
