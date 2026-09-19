import type { ReactNode } from 'react'
import { SCREENS } from './screens'
import './AppShell.css'

export function AppShell({ route, children }: { route: string; children: ReactNode }) {
  return (
    <div className="shell">
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <nav className="rail" aria-label="Screens">
        <span className="rail-mark">
          Opportunity
          <br />
          Engine
        </span>
        <ul>
          {SCREENS.map((screen) => {
            const current = screen.path === route
            return (
              <li key={screen.path}>
                {screen.available ? (
                  <a
                    href={`#/${screen.path}`}
                    className={current ? 'rail-link rail-link-current' : 'rail-link'}
                    aria-current={current ? 'page' : undefined}
                  >
                    {screen.label}
                  </a>
                ) : (
                  <span className="rail-link rail-link-pending" title={screen.note ?? 'Lands on day 3'}>
                    {screen.label}
                    <span className="rail-pending-note">{screen.note ?? 'not built yet'}</span>
                  </span>
                )}
              </li>
            )
          })}
        </ul>
      </nav>
      <main id="main" className="content">
        {children}
      </main>
    </div>
  )
}
