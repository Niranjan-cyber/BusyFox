import { afterEach, describe, expect, it, vi } from 'vitest'
import {
  fetchBusiness,
  fetchClaims,
  fetchFeedbackSignals,
  fetchInbox,
  fetchOpportunities,
  fetchRejectedIdeas,
  weakestMode,
} from './client'
import type { Served } from './client'
import { business, feedbackSignals } from '../fixtures/business'
import { claims, opportunities, rejectedIdeas } from '../fixtures/opportunities'

/**
 * The API client's half of the §7.2 ladder.
 *
 * Two things are protected here, and they pull in opposite directions: a fixture must never be
 * dressed up as live data, and live data must never be quietly replaced by a fixture without
 * the screen being told. Both failure modes are cheap to introduce and invisible on screen, so
 * they get tests rather than a convention.
 */

const BASE = 'https://api.test'

function jsonResponse(body: unknown, headers: Record<string, string> = {}) {
  return new Response(JSON.stringify(body), { status: 200, headers })
}

/** Records every URL requested and answers each one from `answer`. */
function stubFetch(answer: (url: string) => Response | Promise<Response>) {
  const calls: string[] = []
  vi.stubGlobal('fetch', async (url: string) => {
    calls.push(url)
    return answer(url)
  })
  return calls
}

afterEach(() => {
  vi.unstubAllGlobals()
  vi.unstubAllEnvs()
})

describe('with no VITE_API_BASE_URL configured', () => {
  it('serves committed fixtures, labelled demo_fixture, without touching the network', async () => {
    const calls = stubFetch(() => {
      throw new Error('the client must not call fetch with no base URL configured')
    })

    const profile = await fetchBusiness('biz_pulsestack')
    expect(profile.data).toEqual(business)
    expect(profile.retrieval_mode).toBe('demo_fixture')

    const feedback = await fetchFeedbackSignals('biz_pulsestack')
    expect(feedback.data).toEqual(feedbackSignals)
    expect(feedback.retrieval_mode).toBe('demo_fixture')

    const inbox = await fetchInbox('biz_pulsestack')
    expect(inbox.data.opportunities).toEqual(opportunities)
    expect(inbox.data.claims).toEqual(claims)
    expect(inbox.retrieval_mode).toBe('demo_fixture')

    const rejected = await fetchRejectedIdeas('biz_pulsestack')
    expect(rejected.data).toEqual(rejectedIdeas)
    expect(rejected.retrieval_mode).toBe('demo_fixture')

    expect(calls).toEqual([])
  })
})

describe('request paths match docs/contract.md', () => {
  it('uses the contract route for every endpoint it calls', async () => {
    vi.stubEnv('VITE_API_BASE_URL', BASE)
    const calls = stubFetch((url) => {
      if (url.endsWith('/opportunities')) return jsonResponse([opportunities[0]])
      if (url.endsWith('/claims')) return jsonResponse(claims.slice(0, 4))
      return jsonResponse(business)
    })

    await fetchBusiness('biz_pulsestack')
    await fetchFeedbackSignals('biz_pulsestack')
    await fetchOpportunities('biz_pulsestack')
    await fetchClaims('opp_07')

    expect(calls).toEqual([
      `${BASE}/businesses/biz_pulsestack`,
      `${BASE}/businesses/biz_pulsestack/feedback-summary`,
      `${BASE}/businesses/biz_pulsestack/opportunities`,
      // docs/contract.md — claims hang off an opportunity, not a business. There is no
      // /businesses/{id}/claims route in the contract or on the deployed API.
      `${BASE}/opportunities/opp_07/claims`,
    ])
  })
})

describe('the retrieval mode a live response is labelled with', () => {
  it('reports the mode the response declares', async () => {
    vi.stubEnv('VITE_API_BASE_URL', BASE)
    stubFetch(() => jsonResponse(business, { 'X-Retrieval-Mode': 'live' }))

    const profile = await fetchBusiness('biz_pulsestack')
    expect(profile.retrieval_mode).toBe('live')
    expect(profile.data).toEqual(business)
  })

  it('reports cached when the response declares cached', async () => {
    vi.stubEnv('VITE_API_BASE_URL', BASE)
    stubFetch(() => jsonResponse(business, { 'X-Retrieval-Mode': 'cached' }))

    expect((await fetchBusiness('biz_pulsestack')).retrieval_mode).toBe('cached')
  })

  it('says so rather than guessing when the response declares nothing', async () => {
    vi.stubEnv('VITE_API_BASE_URL', BASE)
    stubFetch(() => jsonResponse(business))

    const profile = await fetchBusiness('biz_pulsestack')
    // The deployed API sends no provenance header yet, so this is today's real behaviour.
    // Guessing `cached` would print CACHED VERIFIED SOURCE over stub fixture data.
    expect(profile.retrieval_mode).toBe('undeclared')
  })

  it('ignores a mode it does not recognise rather than trusting it', async () => {
    vi.stubEnv('VITE_API_BASE_URL', BASE)
    stubFetch(() => jsonResponse(business, { 'X-Retrieval-Mode': 'definitely_live_honest' }))

    expect((await fetchBusiness('biz_pulsestack')).retrieval_mode).toBe('undeclared')
  })

  it('serves an empty live payload as live rather than substituting a fixture', async () => {
    vi.stubEnv('VITE_API_BASE_URL', BASE)
    stubFetch(() => jsonResponse([], { 'X-Retrieval-Mode': 'live' }))

    const feedback = await fetchFeedbackSignals('biz_pulsestack')
    expect(feedback.data).toEqual([])
    expect(feedback.retrieval_mode).toBe('live')
  })
})

describe('falling back to the demo fixture', () => {
  it('falls back and names the status code on an HTTP error', async () => {
    vi.stubEnv('VITE_API_BASE_URL', BASE)
    stubFetch(() => new Response('{"error":"boom"}', { status: 500 }))

    const profile = await fetchBusiness('biz_pulsestack')
    expect(profile.data).toEqual(business)
    expect(profile.retrieval_mode).toBe('demo_fixture')
    expect(profile.fallback_reason).toContain('500')
  })

  it('falls back and names the endpoint when the network throws', async () => {
    vi.stubEnv('VITE_API_BASE_URL', BASE)
    vi.stubGlobal('fetch', async () => {
      throw new TypeError('Failed to fetch')
    })

    const feedback = await fetchFeedbackSignals('biz_pulsestack')
    expect(feedback.data).toEqual(feedbackSignals)
    expect(feedback.retrieval_mode).toBe('demo_fixture')
    expect(feedback.fallback_reason).toContain('/businesses/biz_pulsestack/feedback-summary')
    expect(feedback.fallback_reason).toContain('Failed to fetch')
  })

  it('reports a timeout as a timeout, not as a generic abort', async () => {
    vi.useFakeTimers()
    vi.stubEnv('VITE_API_BASE_URL', BASE)
    vi.stubGlobal('fetch', (_url: string, init?: RequestInit) =>
      new Promise<Response>((_resolve, reject) => {
        init?.signal?.addEventListener('abort', () =>
          reject(new DOMException('Aborted', 'AbortError')),
        )
      }),
    )

    const pending = fetchBusiness('biz_pulsestack')
    await vi.advanceTimersByTimeAsync(10_000)
    const profile = await pending

    expect(profile.retrieval_mode).toBe('demo_fixture')
    expect(profile.fallback_reason).toMatch(/timed out/i)
    vi.useRealTimers()
  })
})

describe('the inbox keeps opportunities and their claims consistent', () => {
  it('fetches the claims of each opportunity the list actually returned', async () => {
    vi.stubEnv('VITE_API_BASE_URL', BASE)
    const live = [
      { ...opportunities[0], id: 'opp_live_a' },
      { ...opportunities[1], id: 'opp_live_b' },
    ]
    const calls = stubFetch((url) => {
      if (url.endsWith('/opportunities')) return jsonResponse(live, { 'X-Retrieval-Mode': 'live' })
      const id = url.slice(`${BASE}/opportunities/`.length, -'/claims'.length)
      return jsonResponse([{ ...claims[0], id: `claim_${id}`, opportunity_id: id }], {
        'X-Retrieval-Mode': 'live',
      })
    })

    const inbox = await fetchInbox('biz_pulsestack')

    expect(calls).toEqual([
      `${BASE}/businesses/biz_pulsestack/opportunities`,
      `${BASE}/opportunities/opp_live_a/claims`,
      `${BASE}/opportunities/opp_live_b/claims`,
    ])
    expect(inbox.retrieval_mode).toBe('live')
    expect(inbox.data.claims.map((claim) => claim.opportunity_id)).toEqual([
      'opp_live_a',
      'opp_live_b',
    ])
  })

  it('never pairs fixture claims with live opportunities', async () => {
    vi.stubEnv('VITE_API_BASE_URL', BASE)
    const live = [{ ...opportunities[0], id: 'opp_live_a' }]
    stubFetch((url) => {
      if (url.endsWith('/opportunities')) return jsonResponse(live, { 'X-Retrieval-Mode': 'live' })
      return new Response('{}', { status: 502 })
    })

    const inbox = await fetchInbox('biz_pulsestack')

    expect(inbox.data.opportunities).toEqual(live)
    // The fixture claims belong to fixture opportunities. Serving them beside live ones would
    // attach evidence to an opportunity it was never written about.
    expect(inbox.data.claims).toEqual([])
    expect(inbox.fallback_reason).toContain('502')
  })

  it('falls back to the whole fixture set when the opportunity list itself fails', async () => {
    vi.stubEnv('VITE_API_BASE_URL', BASE)
    const calls = stubFetch(() => new Response('{}', { status: 500 }))

    const inbox = await fetchInbox('biz_pulsestack')

    expect(inbox.retrieval_mode).toBe('demo_fixture')
    expect(inbox.data.opportunities).toEqual(opportunities)
    expect(inbox.data.claims).toEqual(claims)
    // No point asking for the claims of opportunities that were never served.
    expect(calls).toEqual([`${BASE}/businesses/biz_pulsestack/opportunities`])
  })
})

describe('rejected ideas', () => {
  it('calls the contract route and reports the declared retrieval mode', async () => {
    vi.stubEnv('VITE_API_BASE_URL', BASE)
    const calls = stubFetch(() => jsonResponse([], { 'X-Retrieval-Mode': 'live' }))

    const rejected = await fetchRejectedIdeas('biz_pulsestack')

    expect(calls).toEqual([`${BASE}/businesses/biz_pulsestack/rejected-ideas`])
    expect(rejected.data).toEqual([])
    expect(rejected.retrieval_mode).toBe('live')
  })

  it('falls back to the committed fixture, labelled, when the endpoint fails', async () => {
    vi.stubEnv('VITE_API_BASE_URL', BASE)
    stubFetch(() => new Response('{}', { status: 500 }))

    const rejected = await fetchRejectedIdeas('biz_pulsestack')

    expect(rejected.data).toEqual(rejectedIdeas)
    expect(rejected.retrieval_mode).toBe('demo_fixture')
    expect(rejected.fallback_reason).toContain('500')
  })
})

describe('weakestMode', () => {
  const at = (retrieval_mode: Served<unknown>['retrieval_mode']): Served<unknown> => ({
    data: null,
    retrieval_mode,
  })

  it('reports the weakest level present, not the first', () => {
    expect(weakestMode([at('live'), at('live')])).toBe('live')
    expect(weakestMode([at('live'), at('cached')])).toBe('cached')
    expect(weakestMode([at('live'), at('demo_fixture')])).toBe('demo_fixture')
  })

  it('reports an unstated provenance over any ladder level', () => {
    // "We do not know" is the weakest claim available, so it wins the banner.
    expect(weakestMode([at('live'), at('undeclared')])).toBe('undeclared')
    expect(weakestMode([at('demo_fixture'), at('undeclared')])).toBe('undeclared')
  })

  it('treats an empty set as live rather than inventing a fallback', () => {
    expect(weakestMode([])).toBe('live')
  })
})
