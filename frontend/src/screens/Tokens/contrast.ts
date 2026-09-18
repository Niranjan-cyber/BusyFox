/**
 * WCAG 2.1 relative luminance and contrast ratio.
 *
 * The token page resolves colours from the live custom properties and computes the table
 * with these, rather than restating figures from docs/design-plan.md — a token edit that
 * breaks a pairing has to show up as a failure on the page, not as a stale number.
 */

function channel(srgb: number): number {
  const c = srgb / 255
  return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4
}

/** Accepts `#rgb`, `#rrggbb` or the `rgb(r, g, b)` form `getComputedStyle` returns. */
export function toRgb(color: string): [number, number, number] | null {
  const value = color.trim()

  const hex = value.replace('#', '')
  if (/^[0-9a-f]{3}$/i.test(hex)) {
    const [r, g, b] = [...hex].map((c) => parseInt(c + c, 16))
    return [r, g, b]
  }
  if (/^[0-9a-f]{6}$/i.test(hex)) {
    return [
      parseInt(hex.slice(0, 2), 16),
      parseInt(hex.slice(2, 4), 16),
      parseInt(hex.slice(4, 6), 16),
    ]
  }

  const numbers = value.match(/-?[\d.]+/g)
  if (value.startsWith('rgb') && numbers && numbers.length >= 3) {
    return [Number(numbers[0]), Number(numbers[1]), Number(numbers[2])]
  }
  return null
}

export function luminance(color: string): number | null {
  const rgb = toRgb(color)
  if (rgb === null) return null
  const [r, g, b] = rgb
  return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)
}

export function contrastRatio(foreground: string, background: string): number {
  const a = luminance(foreground)
  const b = luminance(background)
  if (a === null || b === null) return 0
  const [light, dark] = a > b ? [a, b] : [b, a]
  return (light + 0.05) / (dark + 0.05)
}

export type ContrastLevel = 'AAA' | 'AA' | 'AA Large' | 'Fail'

/** Thresholds per WCAG 2.1: 4.5 normal text, 3.0 large text and UI components, 7.0 AAA. */
export function contrastLevel(ratio: number): ContrastLevel {
  if (ratio >= 7) return 'AAA'
  if (ratio >= 4.5) return 'AA'
  if (ratio >= 3) return 'AA Large'
  return 'Fail'
}

/**
 * Resolves custom properties to concrete colours.
 *
 * A probe element is used rather than reading the custom property directly, so a token whose
 * value is itself a `var()` reference or a computed colour resolves to real channel values.
 */
export function readTokenColors(tokens: string[]): Record<string, string> {
  const probe = document.createElement('span')
  probe.style.position = 'absolute'
  probe.style.visibility = 'hidden'
  document.body.appendChild(probe)

  const resolved: Record<string, string> = {}
  try {
    for (const token of tokens) {
      probe.style.color = `var(${token})`
      resolved[token] = getComputedStyle(probe).color
    }
  } finally {
    probe.remove()
  }
  return resolved
}
