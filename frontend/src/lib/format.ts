/** Formatting helpers shared across screens. Money is always rendered as a range (§13.2). */

/** Compact money for card headlines: 5940 -> "$5.9k", 850 -> "$850". */
export function compactUsd(value: number): string {
  if (value < 1000) return `$${Math.round(value)}`
  const thousands = value / 1000
  const rounded = thousands >= 10 ? Math.round(thousands) : Math.round(thousands * 10) / 10
  return `$${rounded}k`
}

/** Exact money for the assumptions breakdown, where the arithmetic has to be checkable. */
export function exactUsd(value: number): string {
  return `$${Math.round(value).toLocaleString('en-US')}`
}

export function usdRange(low: number, high: number): string {
  return `${compactUsd(low)}–${compactUsd(high)}`
}

export function percent(fraction: number): string {
  return `${Math.round(fraction * 1000) / 10}%`
}

export function count(value: number): string {
  return value.toLocaleString('en-US')
}
