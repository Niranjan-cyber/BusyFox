export interface ScreenRoute {
  path: string
  label: string
  /** Screens 2, 4 and 5 land on day 3. The nav lists them so the shape of the product is
      visible, and says plainly that they are not built rather than linking nowhere. */
  available: boolean
}

export const SCREENS: ScreenRoute[] = [
  { path: 'business', label: 'Business & feedback', available: true },
  { path: 'investigation', label: 'Live investigation', available: true },
  { path: 'inbox', label: 'Opportunity inbox', available: true },
  { path: 'opportunity', label: 'Opportunity detail', available: false },
  { path: 'execution', label: 'Execution pack', available: false },
]
