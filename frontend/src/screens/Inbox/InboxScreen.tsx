import { fetchBusiness, fetchInbox, fetchRejectedIdeas } from '../../api/client'
import { Section } from '../../components/common/Card'
import {
  EmptyState,
  ErrorState,
  LoadingState,
  ServedBanner,
} from '../../components/common/ScreenState'
import { GoalBar } from '../../components/inbox/GoalBar'
import { OpportunityCard } from '../../components/inbox/OpportunityCard'
import { RejectedIdeas } from '../../components/inbox/RejectedIdeas'
import { useServed } from '../../lib/useServed'
import { goalCoverage, groupOpportunities } from './grouping'
import './InboxScreen.css'

/** Screen 3 — Opportunity Inbox (PRD §1.3, §16.1). */
export function InboxScreen({ businessId }: { businessId: string }) {
  const profile = useServed(fetchBusiness, businessId)
  const inbox = useServed(fetchInbox, businessId)
  const rejected = useServed(fetchRejectedIdeas, businessId)

  if (
    profile.status === 'loading' ||
    inbox.status === 'loading' ||
    rejected.status === 'loading'
  ) {
    return <LoadingState what="the opportunity inbox" />
  }
  if (profile.status === 'error') return <ErrorState message={profile.message} />
  if (inbox.status === 'error') return <ErrorState message={inbox.message} />
  if (rejected.status === 'error') return <ErrorState message={rejected.message} />

  // Each payload falls back independently, so the banner gets all of them and names each.
  const sources = [
    { label: 'Business profile', served: profile.served },
    { label: 'Opportunities and claims', served: inbox.served },
    { label: 'Ideas we rejected', served: rejected.served },
  ]
  const business = profile.served.data
  const { opportunities, claims } = inbox.served.data
  const sections = groupOpportunities(opportunities)
  const coverage = goalCoverage(opportunities, business.goal.change_usd)

  return (
    <>
      <header className="screen-head">
        <h1>Opportunity inbox</h1>
        <p className="screen-lede">
          What {business.name} could do to reach its goal, ranked, with what is blocking the rest.
        </p>
        <ServedBanner sources={sources} />
      </header>

      <GoalBar
        goalChangeUsd={business.goal.change_usd}
        horizonDays={business.goal.horizon_days}
        low={coverage.low}
        high={coverage.high}
        lowShare={coverage.lowShare}
        highShare={coverage.highShare}
      />

      {opportunities.length === 0 ? (
        <EmptyState>
          No opportunities have cleared the quality gate yet. Run an investigation to fill this
          inbox.
        </EmptyState>
      ) : (
        sections.map((section) => (
          <Section key={section.key} title={section.title} description={section.description}>
            {section.opportunities.length === 0 ? (
              <EmptyState>Nothing in this group from the last run.</EmptyState>
            ) : (
              <div className="inbox-cards">
                {section.opportunities.map((opportunity) => (
                  <OpportunityCard
                    key={opportunity.id}
                    opportunity={opportunity}
                    claims={claims}
                  />
                ))}
              </div>
            )}
          </Section>
        ))
      )}

      <Section
        title="Ideas we rejected"
        description="Checked, and did not survive the check. The reason is the point."
      >
        <RejectedIdeas
          ideas={rejected.served.data}
          emptyReason={rejected.served.fallback_reason}
        />
      </Section>
    </>
  )
}
