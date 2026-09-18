import { useEffect, useState } from 'react'

function currentRoute(fallback: string): string {
  return window.location.hash.replace(/^#\/?/, '') || fallback
}

/**
 * Hash routing for the five P0 screens.
 *
 * Five flat screens, no nested routes, no data loaders, no code splitting — a router
 * dependency would carry a lot of machinery none of these screens use. Hash routing also
 * means Amplify Hosting needs no rewrite rule for deep links to work.
 */
export function useHashRoute(fallback: string): string {
  const [route, setRoute] = useState(() => currentRoute(fallback))

  useEffect(() => {
    const onChange = () => setRoute(currentRoute(fallback))
    window.addEventListener('hashchange', onChange)
    return () => window.removeEventListener('hashchange', onChange)
  }, [fallback])

  return route
}
