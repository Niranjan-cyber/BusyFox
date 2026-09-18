import { business, feedbackSignals } from '../fixtures/business'
import { claims, opportunities, rejectedIdeas } from '../fixtures/opportunities'
import type { Business, Claim, Opportunity, RetrievalMode, Signal } from '../types/entities'
import type { RejectedIdea, ServedMode } from '../lib/viewModels'

/**
 * API client for the screens Lane B owns.
 *
 * The resilience ladder in §7.2 is a contract with the person reading the screen, not an
 * implementation detail: every response carries the level it was actually served at, and the
 * UI labels it. When `VITE_API_BASE_URL` is unset or a request fails, this client serves the
 * committed fixtures and says so — `demo_fixture`, never `live`.
 *
 * Every path below is a row in `docs/contract.md`'s API table, matched against the deployed
 * stage (README.md). Nothing here calls a route the contract does not define.
 */

/**
 * Read per call rather than captured at module load: a bundled build inlines the value either
 * way, and reading it lazily is what lets the tests exercise both the configured and the
 * unconfigured branch in one process.
 */
function baseUrl(): string | undefined {
  return import.meta.env.VITE_API_BASE_URL as string | undefined
}

/** Every payload the UI renders knows how it was obtained. */
export interface Served<T> {
  data: T
  retrieval_mode: ServedMode
  /** Why this payload is not at the level above — a failed request, or a missing endpoint. */
  fallback_reason?: string
}

const REQUEST_TIMEOUT_MS = 8000

/**
 * The header the API is expected to state its §7.2 level in.
 *
 * A header rather than a response envelope because four of the nine contract endpoints return
 * a bare array (`Signal[]`, `Opportunity[]`, `Claim[]`, `Evidence[]`), which has nowhere to put
 * an envelope field without changing its declared response type in `docs/contract.md`.
 *
 * Sent by every stub Lambda as of Task 21's follow-up (`backend/handlers/_common.py::ok`).
 * `get_execution_pack` and `list_competitors` always send `demo_fixture` — neither is wired to
 * DynamoDB yet, so that is the honest label rather than a guess.
 */
const RETRIEVAL_MODE_HEADER = 'X-Retrieval-Mode'

const RETRIEVAL_MODES: RetrievalMode[] = ['live', 'cached', 'demo_fixture']

/**
 * Levels 1 and 2 of the §7.2 ladder are the backend's to distinguish: only it knows whether it
 * fetched this second or re-served its own cache. So the mode is read off the response, never
 * assumed. A response that declares nothing — or declares something not on the ladder — is
 * reported `undeclared` rather than guessed at: claiming a provenance the data cannot support
 * is the one failure mode §7.2 exists to prevent, and a wrong guess of `cached` is as much a
 * claim as a wrong guess of `live`.
 */
function declaredMode(response: Response): ServedMode {
  const declared = response.headers.get(RETRIEVAL_MODE_HEADER)
  return RETRIEVAL_MODES.find((mode) => mode === declared) ?? 'undeclared'
}

type Fetched<T> = { data: T; mode: ServedMode } | { error: string }

async function get<T>(path: string): Promise<Fetched<T>> {
  const controller = new AbortController()
  let timedOut = false
  const timer = setTimeout(() => {
    timedOut = true
    controller.abort()
  }, REQUEST_TIMEOUT_MS)
  try {
    const response = await fetch(`${baseUrl()}${path}`, { signal: controller.signal })
    if (!response.ok) {
      return { error: `${path} returned HTTP ${response.status}` }
    }
    return { data: (await response.json()) as T, mode: declaredMode(response) }
  } catch (cause) {
    // An abort we caused and a network failure both surface as a thrown error, and they mean
    // different things to whoever is reading the banner, so they are named separately.
    if (timedOut) {
      return { error: `${path} timed out after ${REQUEST_TIMEOUT_MS / 1000}s` }
    }
    const reason = cause instanceof Error ? cause.message : 'request failed'
    return { error: `${path}: ${reason}` }
  } finally {
    clearTimeout(timer)
  }
}

/** Try the live endpoint; fall back to the committed fixture, labelled. */
async function servedOrFixture<T>(path: string, fixture: T): Promise<Served<T>> {
  if (!baseUrl()) {
    return { data: fixture, retrieval_mode: 'demo_fixture' }
  }
  const result = await get<T>(path)
  if ('error' in result) {
    return { data: fixture, retrieval_mode: 'demo_fixture', fallback_reason: result.error }
  }
  return { data: result.data, retrieval_mode: result.mode }
}

/**
 * Strongest claim first. `undeclared` is not a rung on the §7.2 ladder — it is the absence of
 * a rung — so it sits below all three rather than being folded into one: a screen where one
 * payload's provenance is unknown cannot honestly be summarised as live, cached or fixture.
 */
const MODE_ORDER: ServedMode[] = ['live', 'cached', 'demo_fixture', 'undeclared']

/**
 * The weakest provenance among several payloads rendered on one screen.
 *
 * A screen that pulls several endpoints can have one of them fall back while the rest are
 * live. Reporting only the first would print LIVE RESEARCH over fixture data, so the banner
 * reports the weakest level present and names what fell back.
 */
export function weakestMode(served: Served<unknown>[]): ServedMode {
  let weakest: ServedMode = 'live'
  for (const item of served) {
    if (MODE_ORDER.indexOf(item.retrieval_mode) > MODE_ORDER.indexOf(weakest)) {
      weakest = item.retrieval_mode
    }
  }
  return weakest
}

export function fetchBusiness(businessId: string): Promise<Served<Business>> {
  return servedOrFixture(`/businesses/${businessId}`, business)
}

/** docs/contract.md — this endpoint's response type is `Signal[]`, not a bespoke summary
    shape; grouping into themes happens client-side (see lib/viewModels.ts). */
export function fetchFeedbackSignals(businessId: string): Promise<Served<Signal[]>> {
  return servedOrFixture(`/businesses/${businessId}/feedback-summary`, feedbackSignals)
}

export function fetchOpportunities(businessId: string): Promise<Served<Opportunity[]>> {
  return servedOrFixture(`/businesses/${businessId}/opportunities`, opportunities)
}

/** docs/contract.md — claims hang off an opportunity, not off a business. */
export function fetchClaims(opportunityId: string): Promise<Served<Claim[]>> {
  return servedOrFixture(
    `/opportunities/${opportunityId}/claims`,
    claims.filter((claim) => claim.opportunity_id === opportunityId),
  )
}

export interface InboxPayload {
  opportunities: Opportunity[]
  claims: Claim[]
}

/**
 * Screen 3's data: the opportunity list, plus the claims of the opportunities it returned.
 *
 * The contract has no bulk claims route, so this fans out one `/opportunities/{id}/claims` call
 * per opportunity. It lives here rather than in the screen because of the one rule the screen
 * must not get wrong: fixture claims are only ever served beside fixture opportunities. If the
 * list is live and a claims call fails, that opportunity renders with no claims and the banner
 * says why — substituting the fixture claims would attach evidence to an opportunity nobody
 * ever wrote it about, which is the §7.2 silent-substitution failure in its worst form.
 */
export async function fetchInbox(businessId: string): Promise<Served<InboxPayload>> {
  const list = await fetchOpportunities(businessId)
  if (list.retrieval_mode === 'demo_fixture') {
    // Either no live endpoint is configured or the list fell back. Both mean the fixture
    // world, and the fixture claims are the set written for these exact opportunities.
    return {
      data: { opportunities: list.data, claims },
      retrieval_mode: 'demo_fixture',
      fallback_reason: list.fallback_reason,
    }
  }

  const served = await Promise.all(list.data.map((opportunity) => fetchClaims(opportunity.id)))
  const answered = served.filter((item) => item.fallback_reason === undefined)
  const failed = served.filter((item) => item.fallback_reason !== undefined)

  return {
    data: {
      opportunities: list.data,
      claims: answered.flatMap((item) => item.data),
    },
    // Only what is actually on screen counts towards the label: a claims call that failed
    // contributed nothing to render, so it cannot weaken the provenance of what did.
    retrieval_mode: weakestMode([list, ...answered]),
    fallback_reason:
      failed.length === 0
        ? undefined
        : `${failed.length} of ${served.length} opportunities could not load their claims (${failed[0].fallback_reason})`,
  }
}

/**
 * BLOCKED ON LANE A, TASK 19 (Quality Gate + Ranker).
 *
 * `docs/contract.md`'s API table has no rejected-candidate route and `backend/handlers/` has no
 * handler for one, so there is nothing to call. With no live endpoint configured the committed
 * fixture is the right answer and is labelled as such. With one configured, the honest answer
 * is nothing at all: showing fixture rejections beside a live run's opportunities would present
 * ideas this run never considered as ideas this run rejected.
 */
export function fetchRejectedIdeas(_businessId: string): Promise<Served<RejectedIdea[]>> {
  if (!baseUrl()) {
    return Promise.resolve({ data: rejectedIdeas, retrieval_mode: 'demo_fixture' })
  }
  return Promise.resolve({
    data: [],
    retrieval_mode: 'demo_fixture',
    fallback_reason:
      'The Quality Gate does not store rejected candidates yet (Lane A, Task 19), and the contract has no route for them, so this run has none to show.',
  })
}
