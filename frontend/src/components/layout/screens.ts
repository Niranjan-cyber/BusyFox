export interface ScreenRoute {
  path: string
  label: string
  /** Screens 4 and 5 aren't reachable from a flat nav link — both only make sense for a
      specific opportunity, so they open from a card/screen that already has one. The nav
      lists them so the shape of the product is visible, and says why rather than linking
      nowhere. */
  available: boolean
  /** Overrides the default "not built yet" note. */
  note?: string
}

export const SCREENS: ScreenRoute[] = [
  { path: 'business', label: 'Business & feedback', available: true },
  { path: 'investigation', label: 'Live investigation', available: true },
  { path: 'inbox', label: 'Opportunity inbox', available: true },
  { path: 'opportunity', label: 'Opportunity detail', available: false, note: 'open one from the inbox' },
  {
    path: 'execution',
    label: 'Execution pack',
    available: false,
    note: 'open one from an opportunity detail screen',
  },
]
