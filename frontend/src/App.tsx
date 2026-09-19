import { AppShell } from './components/layout/AppShell'
import { SCREENS } from './components/layout/screens'
import { useHashRoute } from './lib/useHashRoute'
import { BusinessScreen } from './screens/Business/BusinessScreen'
import { InboxScreen } from './screens/Inbox/InboxScreen'
import { InvestigationScreen } from './screens/Investigation/InvestigationScreen'
import { OpportunityDetailScreen } from './screens/OpportunityDetail/OpportunityDetailScreen'
import { TokensScreen } from './screens/Tokens/TokensScreen'

const OPPORTUNITY_ROUTE_PREFIX = 'opportunities/'

/**
 * The business is fixed for the hackathon scope: PulseStack is the only business in the
 * system (§3.2). When a second one exists it becomes part of the route, not a constant.
 */
const BUSINESS_ID = 'biz_pulsestack'

/**
 * A route the nav advertises but has not built yet, and an unrecognised one, get their own
 * answers. Falling through to the business screen would leave someone following a deep link
 * on a page they did not ask for, with nothing marked current in the nav.
 */
function UnavailableScreen({ route }: { route: string }) {
  const known = SCREENS.find((screen) => screen.path === route)
  return (
    <>
      <h1>{known ? known.label : 'No such screen'}</h1>
      <p>
        {known
          ? 'This screen lands later on day 3. Screens 1, 2 and 3 are built.'
          : `There is no screen at #/${route}.`}
      </p>
      <p>
        <a href="#/business">Business & feedback</a> ·{' '}
        <a href="#/investigation">Live investigation</a> ·{' '}
        <a href="#/inbox">Opportunity inbox</a>
      </p>
    </>
  )
}

function App() {
  const route = useHashRoute('business')
  const opportunityId = route.startsWith(OPPORTUNITY_ROUTE_PREFIX)
    ? route.slice(OPPORTUNITY_ROUTE_PREFIX.length)
    : null

  if (route === 'tokens') return <TokensScreen />

  const known =
    route === 'business' || route === 'investigation' || route === 'inbox' || opportunityId !== null

  return (
    <AppShell route={opportunityId !== null ? 'opportunity' : route}>
      {route === 'business' ? <BusinessScreen businessId={BUSINESS_ID} /> : null}
      {route === 'investigation' ? <InvestigationScreen businessId={BUSINESS_ID} /> : null}
      {route === 'inbox' ? <InboxScreen businessId={BUSINESS_ID} /> : null}
      {opportunityId !== null ? <OpportunityDetailScreen opportunityId={opportunityId} /> : null}
      {!known ? <UnavailableScreen route={route} /> : null}
    </AppShell>
  )
}

export default App
