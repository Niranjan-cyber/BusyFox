import type { Claim, Evidence } from '../../types/entities'
import { claimLabel, evidenceCheckResult, type EvidenceCheckOutcome } from '../../lib/viewModels'
import { ClaimLabel, SourceLabel } from '../common/Labels'
import './EvidenceCheckDiagram.css'

/**
 * §16.1's signature moment: the accept/reject Evidence Check diagram, including semantic
 * support (§12.1), walking the real Claim -> Evidence -> Source chain (§14) for every claim —
 * not a static mock. Each row replays `run_evidence_check`'s actual per-evidence outcome
 * (Task 18), read off `claim_support` via `lib/viewModels.ts::evidenceCheckResult`.
 */

const OUTCOME_LABEL: Record<EvidenceCheckOutcome, string> = {
  accepted: 'Accepted',
  rejected_missing_citation: 'Rejected — quote not found',
  rejected_unsupported: 'Rejected — quote exists but does not support the claim',
}

function Step({ label, pass }: { label: string; pass: boolean }) {
  return (
    <span className={pass ? 'check-step check-step-pass' : 'check-step check-step-fail'}>
      <span aria-hidden="true">{pass ? '✓' : '✗'}</span> {label}
    </span>
  )
}

function EvidenceRow({ evidence }: { evidence: Evidence }) {
  const result = evidenceCheckResult(evidence)
  const supportsChecked = result.quoteExists // the model is only ever asked once quote-exists passes
  const supportsPass = result.outcome === 'accepted'

  return (
    <li className={`evidence-check-row evidence-check-${result.outcome}`}>
      <blockquote className="evidence-check-quote">&ldquo;{evidence.quote}&rdquo;</blockquote>
      <div className="evidence-check-source">
        <SourceLabel mode={evidence.retrieval_mode} />
        <a href={evidence.url} target="_blank" rel="noreferrer">
          {evidence.source_kind.replace(/_/g, ' ')} source
        </a>
      </div>
      <div className="evidence-check-steps">
        <Step label="Quote found in source" pass={result.quoteExists} />
        {supportsChecked ? (
          <Step label="Supports the claim" pass={supportsPass} />
        ) : (
          <span className="check-step check-step-skipped">— supports check not run, no quote to check</span>
        )}
        <Step label="Fresh" pass={evidence.freshness.status === 'fresh'} />
      </div>
      <p className="evidence-check-reason">{evidence.claim_support.reason}</p>
      <span className={`evidence-check-verdict evidence-check-verdict-${result.outcome}`}>
        {OUTCOME_LABEL[result.outcome]}
      </span>
    </li>
  )
}

export function EvidenceCheckDiagram({
  claims,
  evidenceByClaimId,
}: {
  claims: Claim[]
  evidenceByClaimId: Record<string, Evidence[]>
}) {
  return (
    <div className="evidence-check-diagram">
      {claims.map((claim) => {
        const evidence = evidenceByClaimId[claim.id] ?? []
        return (
          <div key={claim.id} className="evidence-check-claim">
            <div className="evidence-check-claim-head">
              <span className="claim-type">{claim.type.replace(/_/g, ' ')}</span>
              <ClaimLabel value={claimLabel(claim)} />
              <span className={`claim-status-tag claim-status-${claim.status}`}>{claim.status}</span>
            </div>
            <p className="claim-text">{claim.text}</p>
            {evidence.length === 0 ? (
              <p className="evidence-check-empty">
                No evidence chain loaded for this claim — Evidence Check has nothing to replay.
              </p>
            ) : (
              <ul className="evidence-check-list">
                {evidence.map((item) => (
                  <EvidenceRow key={item.id} evidence={item} />
                ))}
              </ul>
            )}
          </div>
        )
      })}
    </div>
  )
}
