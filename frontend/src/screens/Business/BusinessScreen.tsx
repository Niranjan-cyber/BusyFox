import {
  fetchBusiness,
  fetchFeedbackSignals,
  firstFallbackReason,
  weakestMode,
} from '../../api/client'
import { Card, CardBody, CardHeader, Section } from '../../components/common/Card'
import { ClaimLabel } from '../../components/common/Labels'
import {
  ErrorState,
  LoadingState,
  ServedBanner,
} from '../../components/common/ScreenState'
import { PolaritySplitBar } from '../../components/polarity/PolaritySplitBar'
import { count, exactUsd } from '../../lib/format'
import { useServed } from '../../lib/useServed'
import { summariseFeedback, type FeedbackTheme } from '../../lib/viewModels'
import './BusinessScreen.css'

/** Turns a snake_case key from the scenario file into something a person reads. */
function humanise(key: string): string {
  return key.replace(/_/g, ' ').replace(/^./, (c) => c.toUpperCase())
}

function ThemeList({ themes, emptyText }: { themes: FeedbackTheme[]; emptyText: string }) {
  if (themes.length === 0) {
    return <p className="theme-empty">{emptyText}</p>
  }
  return (
    <ul className="theme-list">
      {themes.map((theme) => (
        <li key={theme.id} className="theme">
          <div className="theme-head">
            <h4>{theme.summary}</h4>
            <span className="theme-count tabular">{count(theme.mention_count)} mentions</span>
          </div>
          <blockquote className="theme-quote">{theme.representative_quote}</blockquote>
          <div className="theme-meta">
            <ClaimLabel value="OBSERVED" />
          </div>
        </li>
      ))}
    </ul>
  )
}

/** Screen 1 — Business & feedback (PRD §16.1). */
export function BusinessScreen({ businessId }: { businessId: string }) {
  const profile = useServed(fetchBusiness, businessId)
  const feedback = useServed(fetchFeedbackSignals, businessId)

  if (profile.status === 'loading' || feedback.status === 'loading') {
    return <LoadingState what="the business profile" />
  }
  if (profile.status === 'error') return <ErrorState message={profile.message} />
  if (feedback.status === 'error') return <ErrorState message={feedback.message} />

  // Both endpoints fall back independently; the banner reports the weaker of the two.
  const payloads = [profile.served, feedback.served]
  const business = profile.served.data
  const summary = summariseFeedback(feedback.served.data)
  const loves = summary.themes.filter((theme) => theme.polarity === 'positive')
  const complains = summary.themes.filter((theme) => theme.polarity === 'negative')
  const goalTarget = business.current_mrr_usd + business.goal.change_usd

  return (
    <>
      <header className="screen-head">
        <h1>{business.name}</h1>
        <p className="screen-lede">
          {humanise(business.industry)} · {humanise(business.playbook_id)} playbook
        </p>
        <ServedBanner
          mode={weakestMode(payloads)}
          fallbackReason={firstFallbackReason(payloads)}
        />
        {business.is_simulated ? (
          <p className="simulated-note">
            {business.name} is a simulated business (scenario <code>{business.scenario_id}</code>),
            so its feedback is generated from a committed seed. Its named competitors are real
            companies, and nothing here asserts a claim about one of them without an attributed
            source.
          </p>
        ) : null}
      </header>

      <Section
        title="Goal"
        description="What this business is trying to move, and by when."
      >
        <Card>
          <CardBody>
            <p className="goal-line">
              <span className="goal-figure tabular">
                {exactUsd(business.goal.change_usd)} additional MRR
              </span>
              <span className="goal-horizon">in {business.goal.horizon_days} days</span>
            </p>
            <p className="goal-detail">
              Currently at <span className="tabular">{exactUsd(business.current_mrr_usd)}</span> MRR,
              so the target is <span className="tabular">{exactUsd(goalTarget)}</span>.
            </p>
          </CardBody>
        </Card>
      </Section>

      <Section
        title="Profile"
        description="What the business can already do, and who it already sells to."
      >
        <div className="profile-grid">
          <Card>
            <CardHeader>
              <h3>Capabilities</h3>
            </CardHeader>
            <CardBody>
              <ul className="chip-list">
                {business.capabilities.map((capability) => (
                  <li
                    key={capability.key}
                    className={capability.confirmed ? 'chip chip-confirmed' : 'chip chip-absent'}
                  >
                    <span aria-hidden="true">{capability.confirmed ? '✓' : '—'}</span>
                    {humanise(capability.key)}
                    <span className="chip-state">
                      {capability.confirmed ? 'confirmed' : 'not built'}
                    </span>
                  </li>
                ))}
              </ul>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h3>Ideal customer</h3>
            </CardHeader>
            <CardBody>
              <ul className="chip-list">
                {business.icp.map((segment) => (
                  <li key={segment} className="chip chip-confirmed">
                    {humanise(segment)}
                  </li>
                ))}
              </ul>
              <dl className="pricing">
                {Object.entries(business.pricing).map(([plan, price]) => (
                  <div key={plan}>
                    <dt>{humanise(plan.replace('_usd_month', ''))}</dt>
                    <dd className="tabular">{exactUsd(price)}/mo</dd>
                  </div>
                ))}
              </dl>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h3>Named competitors</h3>
            </CardHeader>
            <CardBody>
              <ul className="chip-list">
                {business.named_competitors.map((competitor) => (
                  <li key={competitor} className="chip chip-neutral">
                    {competitor}
                  </li>
                ))}
              </ul>
              <p className="competitor-note">
                Real companies. Anything this product says about them comes from an attributed,
                verifiable source.
              </p>
            </CardBody>
          </Card>
        </div>
      </Section>

      <Section
        title="What customers say"
        description={
          <>
            <span className="tabular">{count(summary.total_items)}</span> labelled feedback items
            from this business's own tickets and survey responses.
          </>
        }
      >
        <PolaritySplitBar positive={summary.positive_count} negative={summary.negative_count} />
        <div className="theme-columns">
          <div>
            <h3>What customers love</h3>
            <ThemeList themes={loves} emptyText="No praise themes cleared the mention threshold." />
          </div>
          <div>
            <h3>What customers complain about</h3>
            <ThemeList
              themes={complains}
              emptyText="No complaint themes cleared the mention threshold."
            />
          </div>
        </div>
      </Section>
    </>
  )
}
