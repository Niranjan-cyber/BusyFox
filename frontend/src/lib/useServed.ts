import { useEffect, useState } from 'react'
import type { Served } from '../api/client'

type State<T> =
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'ready'; served: Served<T> }

const LOADING = { status: 'loading' } as const

/**
 * Runs one API client call and tracks its loading, error and ready states.
 *
 * `fetcher` is a module-level function from the API client, so it is stable across renders
 * and can be a real dependency. The result is stored with the key it belongs to, and the
 * loading state is derived during render rather than assigned inside the effect — which
 * keeps the effect from starting a second render pass just to show a spinner.
 *
 * The client already falls back to fixtures, so `error` here means the call itself threw: a
 * bug rather than an unreachable backend. It is still surfaced rather than swallowed.
 */
export function useServed<T>(
  fetcher: (key: string) => Promise<Served<T>>,
  key: string,
): State<T> {
  const [result, setResult] = useState<{ key: string; state: State<T> } | null>(null)

  useEffect(() => {
    let active = true
    fetcher(key)
      .then((served) => {
        if (active) setResult({ key, state: { status: 'ready', served } })
      })
      .catch((cause: unknown) => {
        if (!active) return
        setResult({
          key,
          state: {
            status: 'error',
            message: cause instanceof Error ? cause.message : 'Could not load this screen.',
          },
        })
      })
    return () => {
      active = false
    }
  }, [fetcher, key])

  return result !== null && result.key === key ? result.state : LOADING
}
