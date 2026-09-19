import { useEffect, useState } from 'react'
import { fetchSignals, type Served } from '../../api/client'
import { Section } from '../../components/common/Card'
import { SourceLabel } from '../../components/common/Labels'
import {
  EmptyState,
  ErrorState,
  LoadingState,
  ServedBanner,
} from '../../components/common/ScreenState'
import { LANE_LABEL, RESEARCH_LANES, signalLane } from '../../lib/viewModels'
import type { Signal } from '../../types/entities'
import './InvestigationScreen.css'

const POLL_MS = 4000

type PollState =
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'ready'; served: Served<Signal[]> }

/**
 * Screen 2 — Live investigation (PRD §16.1).
 *
 * Polls `/businesses/{id}/signals` rather than opening a stream — the acceptance criteria
 * (tasks/plan.md Task 30) explicitly allow this for a hackathon-scale demo. Each signal carries
 * its own `SourceLabel`, not just the screen-level banner: with one bare-array endpoint every
 * signal on screen shares the response's retrieval mode, but §7.2 requires the label to sit next
 * to the data it describes, not just once at the top.
 */
export function InvestigationScreen({ businessId }: { businessId: string }) {
  const [state, setState] = useState<PollState>({ status: 'loading' })

  useEffect(() => {
    let active = true
    async function poll() {
      try {
        const served = await fetchSignals(businessId)
        if (active) setState({ status: 'ready', served })
      } catch (cause) {
        if (active) {
          setState({
            status: 'error',
            message: cause instanceof Error ? cause.message : 'Could not load signals.',
          })
        }
      }
    }
    poll()
    const timer = setInterval(poll, POLL_MS)
    return () => {
      active = false
      clearInterval(timer)
    }
  }, [businessId])

  if (state.status === 'loading') return <LoadingState what="the live investigation" />
  if (state.status === 'error') return <ErrorState message={state.message} />

  const signals = state.served.data

  return (
    <>
      <header className="screen-head">
        <h1>Live investigation</h1>
        <p className="screen-lede">
          Signals arriving from the three research lanes, each labelled with where it came from.
        </p>
        <ServedBanner sources={[{ label: 'Signals', served: state.served }]} />
      </header>

      {signals.length === 0 ? (
        <EmptyState>No signals yet. Run an investigation to populate the three lanes.</EmptyState>
      ) : (
        <div className="lanes">
          {RESEARCH_LANES.map((lane) => {
            const laneSignals = signals.filter((signal) => signalLane(signal) === lane)
            return (
              <Section
                key={lane}
                title={LANE_LABEL[lane]}
                description={`${laneSignals.length} signal${laneSignals.length === 1 ? '' : 's'}`}
              >
                {laneSignals.length === 0 ? (
                  <EmptyState>Nothing from this lane yet.</EmptyState>
                ) : (
                  <ul className="lane-signals">
                    {laneSignals.map((signal) => (
                      <li key={signal.id} className={`lane-signal lane-signal-${signal.polarity}`}>
                        <div className="lane-signal-head">
                          <span className="lane-signal-aspect">{signal.aspect.replace(/_/g, ' ')}</span>
                          <SourceLabel mode={state.served.retrieval_mode} />
                        </div>
                        <p className="lane-signal-text">{signal.claim_text}</p>
                      </li>
                    ))}
                  </ul>
                )}
              </Section>
            )
          })}
        </div>
      )}

      <p className="investigation-note">
        Opportunities that clear the quality gate appear in the{' '}
        <a href="#/inbox">opportunity inbox</a>.
      </p>
    </>
  )
}
