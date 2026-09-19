import { useEffect, useState } from 'react'
import {
  fetchClaimEvidence,
  fetchClaims,
  fetchOpportunity,
  type Served,
} from '../../api/client'
import { Section } from '../../components/common/Card'
import { EvidenceCheckDiagram } from '../../components/evidence-check/EvidenceCheckDiagram'
import { ClaimLabel } from '../../components/common/Labels'
import { ConfidenceMeter, EditableValueRange, EvidenceDiversityReadout, PriorityChip } from '../../components/common/Metrics'
import { EmptyState, ErrorState, LoadingState, ServedBanner } from '../../components/common/ScreenState'
import { claimLabel, opportunityTitle } from '../../lib/viewModels'
import type { Claim, Evidence } from '../../types/entities'
import { useServed } from '../../lib/useServed'
import './OpportunityDetailScreen.css'

const CLAIM_HEADING: Record<Claim['type'], string> = {
  why_this: 'Why this',
  why_you: 'Why you',
  why_now: 'Why now',
  mechanism: 'Mechanism',
}

const CLAIM_ORDER: Claim['type'][] = ['why_this', 'why_you', 'why_now', 'mechanism']

type EvidenceState =
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'ready'; byClaimId: Record<string, Served<Evidence[]>> }

const LOADING: EvidenceState = { status: 'loading' }

/** Fetches each of an opportunity's claims' evidence chains once the claim list is known.
    One-off wiring for this screen, not a general hook — nothing else in the app needs to fan
    a list of ids out into parallel per-id fetches this way. Mirrors `useServed`'s key/result
    split rather than setting a loading state from inside the effect. */
function useClaimEvidence(claims: Claim[] | null): EvidenceState {
  const key = claims === null ? null : claims.map((claim) => claim.id).join(',')
  const [result, setResult] = useState<{ key: string; state: EvidenceState } | null>(null)

  useEffect(() => {
    if (claims === null || key === null) return
    let active = true
    Promise.all(claims.map((claim) => fetchClaimEvidence(claim.id).then((served) => [claim.id, served] as const)))
      .then((pairs) => {
        if (active) setResult({ key, state: { status: 'ready', byClaimId: Object.fromEntries(pairs) } })
      })
      .catch((cause: unknown) => {
        if (active) {
          setResult({
            key,
            state: {
              status: 'error',
              message: cause instanceof Error ? cause.message : 'Could not load the evidence chain.',
            },
          })
        }
      })
    return () => {
      active = false
    }
  }, [claims, key])

  return result !== null && result.key === key ? result.state : LOADING
}

/** Screen 4 — Opportunity detail (PRD §16.1). Reached from an opportunity card's evidence-chain
    link (`#/opportunities/{id}`), not from a top-level nav entry — there is no meaningful
    id-less "opportunity detail" page to land on. */
export function OpportunityDetailScreen({ opportunityId }: { opportunityId: string }) {
  const opportunity = useServed(fetchOpportunity, opportunityId)
  const claims = useServed(fetchClaims, opportunityId)
  const evidence = useClaimEvidence(claims.status === 'ready' ? claims.served.data : null)

  if (opportunity.status === 'loading' || claims.status === 'loading' || evidence.status === 'loading') {
    return <LoadingState what="the opportunity" />
  }
  if (opportunity.status === 'error') return <ErrorState message={opportunity.message} />
  if (claims.status === 'error') return <ErrorState message={claims.message} />
  if (evidence.status === 'error') return <ErrorState message={evidence.message} />

  const data = opportunity.served.data
  const orderedClaims = CLAIM_ORDER.map((type) =>
    claims.served.data.find((claim) => claim.type === type),
  ).filter((claim): claim is Claim => claim !== undefined)

  const sources = [
    { label: 'Opportunity', served: opportunity.served },
    { label: 'Claims', served: claims.served },
  ]

  return (
    <>
      <header className="screen-head">
        <p className="screen-lede">
          <a href="#/inbox">← Back to the opportunity inbox</a>
        </p>
        <h1>{opportunityTitle(data)}</h1>
        <PriorityChip value={data.priority} />
        <ServedBanner sources={sources} />
      </header>

      <Section title="The three readings" description="Never combined into one score (§13.1).">
        <div className="detail-readings">
          <ConfidenceMeter value={data.evidence_confidence} />
          <EditableValueRange value={data.value} />
        </div>
      </Section>

      <Section title="Claims" description="Why this / why you / why now / mechanism (§14.6).">
        {orderedClaims.length === 0 ? (
          <EmptyState>This opportunity&apos;s claims could not be loaded.</EmptyState>
        ) : (
          <div className="detail-claims">
            {orderedClaims.map((claim) => (
              <div key={claim.id} className="detail-claim">
                <div className="claim-head">
                  <span className="claim-type">{CLAIM_HEADING[claim.type]}</span>
                  <ClaimLabel value={claimLabel(claim)} />
                </div>
                <p className="claim-text">{claim.text}</p>
              </div>
            ))}
          </div>
        )}
      </Section>

      <Section title="Strengths this builds on">
        {data.strengths_it_builds_on.length === 0 ? (
          <EmptyState>No strengths on record for this opportunity.</EmptyState>
        ) : (
          <ul className="detail-signal-list detail-signal-list-positive">
            {data.strengths_it_builds_on.map((item) => (
              <li key={item.signal_id}>{item.reason}</li>
            ))}
          </ul>
        )}
      </Section>

      <Section title="Pains to fix first">
        {data.pains_to_fix_first.length === 0 ? (
          <EmptyState>Nothing is blocking this opportunity.</EmptyState>
        ) : (
          <ul className="detail-signal-list detail-signal-list-negative">
            {data.pains_to_fix_first.map((item) => (
              <li key={item.signal_id}>{item.reason}</li>
            ))}
          </ul>
        )}
      </Section>

      <Section title="Competitive context">
        {data.competitive_context.length === 0 ? (
          <EmptyState>No named competitor pattern on record.</EmptyState>
        ) : (
          <ul className="detail-signal-list">
            {data.competitive_context.map((item) => (
              <li key={`${item.signal_id}-${item.competitor}`}>
                <strong>{item.competitor}</strong> — {item.pattern.replace(/_/g, ' ')}
              </li>
            ))}
          </ul>
        )}
        <EvidenceDiversityReadout diversity={data.evidence_diversity} />
      </Section>

      <Section
        title="Evidence Check, live"
        description="The accept/reject decision Task 18's run_evidence_check actually produced for this opportunity's claims, including the semantic-support check (§12.1)."
      >
        <EvidenceCheckDiagram
          claims={orderedClaims}
          evidenceByClaimId={Object.fromEntries(
            Object.entries(evidence.byClaimId).map(([claimId, served]) => [claimId, served.data]),
          )}
        />
      </Section>
    </>
  )
}
