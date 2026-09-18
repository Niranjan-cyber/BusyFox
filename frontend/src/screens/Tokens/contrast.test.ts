import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'
import { contrastLevel, contrastRatio, toRgb } from './contrast'

/**
 * The contrast guarantees, checked against theme.css itself.
 *
 * The token page proves this in a browser, but only when somebody opens it. Parsing the
 * stylesheet here means a palette edit that breaks a pairing fails `npm test` instead.
 *
 * The stylesheet is read from disk rather than imported with `?raw`, because vitest's CSS
 * handling resolves that to an empty string.
 */

const theme = readFileSync(new URL('../../styles/theme.css', import.meta.url), 'utf8')

function token(name: string): string {
  const match = theme.match(new RegExp(`${name}:\\s*(#[0-9a-fA-F]{3,8})\\s*;`))
  if (match === null) throw new Error(`${name} is not a literal colour in theme.css`)
  return match[1]
}

describe('toRgb', () => {
  it('reads the forms getComputedStyle and CSS produce', () => {
    expect(toRgb('#cbd5d4')).toEqual([203, 213, 212])
    expect(toRgb('#abc')).toEqual([170, 187, 204])
    expect(toRgb('rgb(203, 213, 212)')).toEqual([203, 213, 212])
    expect(toRgb('rgb(203 213 212 / 0.5)')).toEqual([203, 213, 212])
    expect(toRgb('not a colour')).toBeNull()
  })
})

describe('contrastLevel', () => {
  it('uses the WCAG 2.1 thresholds', () => {
    expect(contrastLevel(7)).toBe('AAA')
    expect(contrastLevel(4.5)).toBe('AA')
    expect(contrastLevel(3)).toBe('AA Large')
    expect(contrastLevel(2.99)).toBe('Fail')
  })
})

describe('theme.css pairings', () => {
  const required: [string, string, number, string][] = [
    ['--ink', '--bg', 4.5, 'primary text on the page'],
    ['--ink', '--surface', 4.5, 'primary text on a card'],
    ['--bg', '--slate', 4.5, 'text on the nav rail'],
    ['--accent', '--slate', 4.5, 'accent as text on a dark surface'],
    ['--on-slate-muted', '--slate', 4.5, 'de-emphasised text on the nav rail'],
    ['--ink', '--accent', 4.5, 'text on an accent fill'],
    ['--muted', '--surface', 4.5, 'secondary text on a card'],
    ['--warning', '--surface', 4.5, 'warning text on a card'],
    ['--negative', '--surface', 4.5, 'negative text on a card'],
    ['--slate', '--bg', 4.5, 'secondary text on the page'],
    ['--muted', '--bg', 3, 'borders and large text on the page'],
  ]

  it.each(required)('%s on %s clears %s:1 — %s', (fg, bg, threshold) => {
    expect(contrastRatio(token(fg), token(bg))).toBeGreaterThanOrEqual(threshold)
  })

  /**
   * These must fail. They are the pairings the design system forbids, and a palette change
   * that quietly made one of them pass would mean the palette is no longer the brief's.
   */
  const forbidden: [string, string, string][] = [
    ['--accent', '--bg', 'accent as text on the page background'],
    ['--accent', '--surface', 'accent as text on a card'],
    ['--muted', '--slate', 'muted as text on the nav rail'],
  ]

  it.each(forbidden)('%s on %s stays unusable as text — %s', (fg, bg) => {
    expect(contrastRatio(token(fg), token(bg))).toBeLessThan(3)
  })
})
