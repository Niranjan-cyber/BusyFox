import type { Claim, Opportunity } from '../../types/entities'
import { Card, CardBody, CardFooter, CardHeader } from '../common/Card'
import { ClaimLabel } from '../common/Labels'
import { ConfidenceMeter, EvidenceDiversityReadout, PriorityChip, ValueRange } from '../common/Metrics'
import { CLAIM_HEADING, CLAIM_ORDER, claimLabel, opportunityTitle } from '../../lib/viewModels'
import './OpportunityCard.css'

/** The card from §1.4. Every line on it is either evidence-backed or labelled as not. */

function ClaimRow({ claim }: { claim: Claim }) {
  return (
    <div className="claim">
      <div className="claim-head">
        <span className="claim-type">{CLAIM_HEADING[claim.type]}</span>
        <ClaimLabel value={claimLabel(claim)} />
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
        <h3>{opportunityTitle(opportunity)}</h3>
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

        {/* An opportunity whose claims did not load is not an opportunity without claims, and
            the two look identical if the block just renders empty. §14.8 requires all four. */}
        {ordered.length === 0 ? (
          <p className="claims-missing">
            This opportunity&apos;s claims could not be loaded, so its why this / why you / why
            now / mechanism lines are missing rather than absent.
          </p>
        ) : (
          <div className="claims">
            {ordered.map((claim) => (
              <ClaimRow key={claim.id} claim={claim} />
            ))}
          </div>
        )}

        {/* "Your fit" and "What to do" sections dropped: no canonical field backs either
            (Opportunity has no capability link and no free-text action recommendation) and
            inventing one isn't this layer's call — see LEARNING.md. */}
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

        <EvidenceDiversityReadout diversity={diversity} />
      </CardBody>

      <CardFooter>
        <a className="card-detail-link" href={`#/opportunities/${opportunity.id}`}>
          View evidence chain and editable assumptions →
        </a>
      </CardFooter>
    </Card>
  )
}
