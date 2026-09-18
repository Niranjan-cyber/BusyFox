import { business, feedbackSignals } from '../fixtures/business'
import { claims, opportunities } from '../fixtures/opportunities'
import type { Business, Claim, Opportunity, RetrievalMode, Signal } from '../types/entities'
import type { RejectedIdea } from '../lib/viewModels'

/**
 * API client for the screens Lane B owns.
 *
 * The resilience ladder in §7.2 is a contract with the person reading the screen, not an
 * implementation detail: every response carries the `retrieval_mode` it was actually served
 * at, and the UI labels it. When `VITE_API_BASE_URL` is unset or the request fails, this
 * client serves the committed fixtures and says so — `demo_fixture`, never `live`.
 *
 * Endpoints here cover screens 1 and 3 only. §15 names four endpoints; the GET endpoints the
 * screens need are not all spelled out there, so the gap is made explicit in the paths below
 * and needs confirming against Task 2's stubs when they land.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL as string | undefined

/** Every payload the UI renders knows how it was obtained. */
export interface Served<T> {
  data: T
  retrieval_mode: RetrievalMode
  /** Present only when a live request was attempted and did not succeed. */
  fallback_reason?: string
}

const REQUEST_TIMEOUT_MS = 8000

async function get<T>(path: string): Promise<{ data: T } | { error: string }> {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)
  try {
    const response = await fetch(`${BASE_URL}${path}`, { signal: controller.signal })
    if (!response.ok) {
      return { error: `${path} returned ${response.status}` }
    }
    return { data: (await response.json()) as T }
  } catch (cause) {
    const reason = cause instanceof Error ? cause.message : 'request failed'
    return { error: `${path}: ${reason}` }
  } finally {
    clearTimeout(timer)
  }
}

const RETRIEVAL_MODES: RetrievalMode[] = ['live', 'cached', 'demo_fixture']

/**
 * Levels 1 and 2 of the §7.2 ladder are the backend's to distinguish: only it knows whether
 * it fetched this second or re-served its own cache. So the mode is read off the payload,
 * never assumed. A response that does not declare one is treated as `cached` rather than
 * `live` — claiming a fresher provenance than the data can support is the one failure mode
 * §7.2 exists to prevent.
 */
function declaredMode(payload: unknown): RetrievalMode {
  if (payload && typeof payload === 'object' && 'retrieval_mode' in payload) {
    const mode = (payload as { retrieval_mode: unknown }).retrieval_mode
    if (RETRIEVAL_MODES.includes(mode as RetrievalMode)) return mode as RetrievalMode
  }
  return 'cached'
}

/** Try the live endpoint; fall back to the committed fixture, labelled. */
async function servedOrFixture<T>(path: string, fixture: T): Promise<Served<T>> {
  if (!BASE_URL) {
    return { data: fixture, retrieval_mode: 'demo_fixture' }
  }
  const result = await get<T>(path)
  if ('error' in result) {
    return { data: fixture, retrieval_mode: 'demo_fixture', fallback_reason: result.error }
  }
  return { data: result.data, retrieval_mode: declaredMode(result.data) }
}

/**
 * The weakest provenance among several payloads rendered on one screen.
 *
 * A screen that pulls four endpoints can have one of them fall back while the rest are live.
 * Reporting only the first would print LIVE RESEARCH over fixture data, so the banner
 * reports the weakest level present and names what fell back.
 */
export function weakestMode(served: Served<unknown>[]): Served<unknown>['retrieval_mode'] {
  let weakest: RetrievalMode = 'live'
  for (const item of served) {
    if (RETRIEVAL_MODES.indexOf(item.retrieval_mode) > RETRIEVAL_MODES.indexOf(weakest)) {
      weakest = item.retrieval_mode
    }
  }
  return weakest
}

/** The first stated fallback reason among several payloads, if any fell back. */
export function firstFallbackReason(served: Served<unknown>[]): string | undefined {
  return served.find((item) => item.fallback_reason !== undefined)?.fallback_reason
}

export function fetchBusiness(businessId: string): Promise<Served<Business>> {
  return servedOrFixture(`/businesses/${businessId}`, business)
}

/** docs/contract.md:61 — this endpoint's response type is `Signal[]`, not a bespoke summary
    shape; grouping into themes happens client-side (see lib/viewModels.ts). */
export function fetchFeedbackSignals(businessId: string): Promise<Served<Signal[]>> {
  return servedOrFixture(`/businesses/${businessId}/feedback-summary`, feedbackSignals)
}

export function fetchOpportunities(businessId: string): Promise<Served<Opportunity[]>> {
  return servedOrFixture(`/businesses/${businessId}/opportunities`, opportunities)
}

export function fetchClaims(businessId: string): Promise<Served<Claim[]>> {
  return servedOrFixture(`/businesses/${businessId}/claims`, claims)
}

/** No canonical entity or endpoint exists for gate-rejected candidates yet (Quality Gate,
    Day 2, Lane A) — see lib/viewModels.ts. Stubbed empty rather than calling a made-up path. */
export function fetchRejectedIdeas(_businessId: string): Promise<Served<RejectedIdea[]>> {
  return Promise.resolve({ data: [], retrieval_mode: 'demo_fixture' })
}
