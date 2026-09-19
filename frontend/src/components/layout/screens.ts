export interface ScreenRoute {
  path: string
  label: string
  /** Screens 4 and 5 aren't reachable from a flat nav link — 4 opens from a specific
      opportunity's card, 5 hasn't landed yet. The nav lists them so the shape of the product
      is visible, and says why rather than linking nowhere. */
  available: boolean
  /** Overrides the default "not built yet" note. */
  note?: string
}

export const SCREENS: ScreenRoute[] = [
  { path: 'business', label: 'Business & feedback', available: true },
  { path: 'investigation', label: 'Live investigation', available: true },
  { path: 'inbox', label: 'Opportunity inbox', available: true },
  { path: 'opportunity', label: 'Opportunity detail', available: false, note: 'open one from the inbox' },
  { path: 'execution', label: 'Execution pack', available: false },
]
