import { renderToStaticMarkup } from 'react-dom/server'
import { describe, expect, it } from 'vitest'
import { AppShell } from '../components/layout/AppShell'
import { OpportunityCard } from '../components/inbox/OpportunityCard'
import { GoalBar } from '../components/inbox/GoalBar'
import { RejectedIdeas } from '../components/inbox/RejectedIdeas'
import { PolaritySplitBar } from '../components/polarity/PolaritySplitBar'
import { claims, opportunities, rejectedIdeas } from '../fixtures/opportunities'
import { feedbackSummary } from '../fixtures/business'

/**
 * Render smoke tests.
 *
 * These render to static markup rather than driving a browser, so they prove the components
 * render and that the required labels reach the output — not that the layout looks right.
 * Visual and viewport checks are a separate manual pass.
 */

const renderCard = (id: string) => {
  const opportunity = opportunities.find((o) => o.id === id)!
  return renderToStaticMarkup(<OpportunityCard opportunity={opportunity} claims={claims} />)
}

describe('OpportunityCard', () => {
  it('renders all four claims with their labels', () => {
    const html = renderCard('opp_07')
    for (const heading of ['Why this', 'Why you', 'Why now', 'Mechanism']) {
      expect(html).toContain(heading)
    }
    expect(html).toContain('OBSERVED')
    expect(html).toContain('INFERRED')
  })

  it('shows priority, evidence confidence and value as three separate readings', () => {
    const html = renderCard('opp_07')
    expect(html).toContain('High priority')
    expect(html).toContain('Evidence confidence')
    expect(html).toContain('Potential value')
  })

  it('tags the value estimate ASSUMED and shows the assumptions behind it', () => {
    const html = renderCard('opp_07')
    expect(html).toContain('ASSUMED')
    // The §13.2 worked example, so the numbers on screen can be checked against the PRD.
    expect(html).toContain('$5.9k')
    expect(html).toContain('$18k')
    expect(html).toContain('5%')
    expect(html).toContain('$99')
  })

  it('marks a blocked opportunity as blocked and names what to fix first', () => {
    const html = renderCard('opp_04')
    expect(html).toContain('card-blocked')
    expect(html).toContain('Blocked')
    expect(html).toContain('Fix first')
  })

  it('never renders a combined score', () => {
    for (const opportunity of opportunities) {
      const html = renderCard(opportunity.id).toLowerCase()
      expect(html).not.toContain('overall score')
      expect(html).not.toContain('opportunity score')
      expect(html).not.toMatch(/score[:\s]/)
    }
  })
})

describe('PolaritySplitBar', () => {
  it('states both counts in text, not only through colour', () => {
    const html = renderToStaticMarkup(
      <PolaritySplitBar
        positive={feedbackSummary.positive_count}
        negative={feedbackSummary.negative_count}
      />,
    )
    expect(html).toContain('98')
    expect(html).toContain('72')
    expect(html).toContain('aria-label')
  })

  it('handles an empty feedback set without dividing by zero', () => {
    const html = renderToStaticMarkup(<PolaritySplitBar positive={0} negative={0} />)
    expect(html).toContain('No feedback has been labelled')
  })
})

describe('GoalBar', () => {
  it('shows the identified range against the goal', () => {
    const html = renderToStaticMarkup(
      <GoalBar
        goalChangeUsd={15000}
        horizonDays={90}
        low={10148}
        high={23711}
        lowShare={0.68}
        highShare={1.58}
      />,
    )
    expect(html).toContain('$15,000 additional MRR in 90 days')
    expect(html).toContain('ASSUMED')
    // The high end exceeds the goal; the bar must clamp rather than overflow its track.
    expect(html).toContain('width:100%')
  })
})

describe('RejectedIdeas', () => {
  it('shows the reason, not just the count', () => {
    const html = renderToStaticMarkup(<RejectedIdeas ideas={rejectedIdeas} />)
    expect(html).toContain('quote-exists')
    expect(html).toContain('evidence diversity')
  })

  it('has an empty state', () => {
    const html = renderToStaticMarkup(<RejectedIdeas ideas={[]} />)
    expect(html).toContain('Nothing was rejected')
  })
})

describe('AppShell', () => {
  it('marks the current screen and says which screens are not built', () => {
    const html = renderToStaticMarkup(
      <AppShell route="inbox">
        <p>content</p>
      </AppShell>,
    )
    expect(html).toContain('aria-current="page"')
    expect(html).toContain('not built yet')
    expect(html).toContain('Skip to content')
  })
})
