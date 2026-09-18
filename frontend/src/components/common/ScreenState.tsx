import type { ReactNode } from 'react'
import { weakestMode, type Served } from '../../api/client'
import type { ServedMode } from '../../lib/viewModels'
import { SourceLabel } from './Labels'
import './ScreenState.css'

/** Loading, error and empty states. An empty screen is an invitation to act, not a shrug. */

export function LoadingState({ what }: { what: string }) {
  return (
    <p className="screen-state" role="status">
      Loading {what}…
    </p>
  )
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="screen-state screen-state-error" role="alert">
      <p>This screen could not load.</p>
      <p className="screen-state-detail">{message}</p>
    </div>
  )
}

export function EmptyState({ children }: { children: ReactNode }) {
  return <p className="screen-state">{children}</p>
}

/** One named payload on the screen, and how it was served. */
export interface BannerSource {
  label: string
  served: Served<unknown>
}

const SUMMARY: Record<ServedMode, string> = {
  live: 'Fetched fresh during this run.',
  cached: 'Real evidence collected earlier in this run, re-served now.',
  demo_fixture: 'Pre-collected and verified. No live endpoint is configured for this build.',
  undeclared:
    'The API answered, but did not state whether it fetched this live, re-served it from cache, or served a fixture. It is not labelled as any of them.',
}

/** Falling back to level 3 and never having left it are different facts about the same data. */
const FELL_BACK_TO_FIXTURE =
  'Live research was unavailable, so part of this screen falls back to pre-collected verified data.'

/**
 * The provenance banner every screen carries (§7.2).
 *
 * It takes every payload the screen renders rather than one mode, because a screen that pulls
 * four endpoints can have one fall back while the rest are live. Two rules follow from that:
 * the headline states the *weakest* level present, so no part of the screen is covered by a
 * stronger claim than it has earned; and as soon as the sources disagree, or any one of them
 * fell back, each is named with its own level and its own reason. A judge reading this gets
 * the partial answer, not an average.
 */
export function ServedBanner({ sources }: { sources: BannerSource[] }) {
  const mode = weakestMode(sources.map((source) => source.served))
  const fellBack = sources.some((source) => source.served.fallback_reason !== undefined)
  const mixed = new Set(sources.map((source) => source.served.retrieval_mode)).size > 1

  return (
    <section className="served-banner" aria-label="Where this screen's data came from">
      <p className="served-banner-head">
        <SourceLabel mode={mode} />
        <span className="served-banner-text">
          {mode === 'demo_fixture' && fellBack ? FELL_BACK_TO_FIXTURE : SUMMARY[mode]}
        </span>
      </p>
      {mixed || fellBack ? (
        <ul className="served-sources">
          {sources.map((source) => (
            <li key={source.label}>
              <span className="served-source-name">{source.label}</span>
              <SourceLabel mode={source.served.retrieval_mode} />
              {source.served.fallback_reason ? (
                <span className="served-source-reason">{source.served.fallback_reason}</span>
              ) : null}
            </li>
          ))}
        </ul>
      ) : null}
    </section>
  )
}
