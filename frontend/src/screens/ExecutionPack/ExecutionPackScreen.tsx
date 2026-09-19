import { fetchExecutionPack, fetchOpportunity } from '../../api/client'
import { Section } from '../../components/common/Card'
import { ExecutionPackBody } from '../../components/execution-pack/ExecutionPackBody'
import { PriorityChip } from '../../components/common/Metrics'
import { ErrorState, LoadingState, ServedBanner } from '../../components/common/ScreenState'
import { opportunityTitle } from '../../lib/viewModels'
import { useServed } from '../../lib/useServed'

/**
 * Screen 5 — Execution pack (PRD §16.1). Reached from an opportunity detail screen's
 * "View execution pack" link (`#/opportunities/{id}/execution-pack`), not a flat nav link —
 * same "no meaningful id-less landing page" reasoning `OpportunityDetailScreen` already
 * documents for screen 4.
 *
 * Fetches the opportunity too (not just the pack) because the outreach drafts' proof points
 * are `strengths_it_builds_on` signal ids, and that list lives on `Opportunity`, not on
 * `ExecutionPack` — see `ExecutionPackBody`.
 */
export function ExecutionPackScreen({ opportunityId }: { opportunityId: string }) {
  const opportunity = useServed(fetchOpportunity, opportunityId)
  const pack = useServed(fetchExecutionPack, opportunityId)

  if (opportunity.status === 'loading' || pack.status === 'loading') {
    return <LoadingState what="the execution pack" />
  }
  if (opportunity.status === 'error') return <ErrorState message={opportunity.message} />
  if (pack.status === 'error') return <ErrorState message={pack.message} />

  const data = opportunity.served.data
  const sources = [
    { label: 'Opportunity', served: opportunity.served },
    { label: 'Execution pack', served: pack.served },
  ]

  return (
    <>
      <header className="screen-head">
        <p className="screen-lede">
          <a href={`#/opportunities/${opportunityId}`}>← Back to the opportunity</a>
        </p>
        <h1>{opportunityTitle(data)}</h1>
        <PriorityChip value={data.priority} />
        <ServedBanner sources={sources} />
      </header>

      <Section
        title="Execution pack"
        description="Offer, proposal, and outreach drafts — the only place outreach_policy (§6.1, §18.1) is shown end-to-end."
      >
        <ExecutionPackBody pack={pack.served.data} opportunity={data} />
      </Section>
    </>
  )
}
