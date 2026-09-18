import { useEffect, useState } from 'react'
import { contrastLevel, contrastRatio, readTokenColors } from './contrast'
import './TokensScreen.css'

/**
 * Development-only reference page for the design tokens (todo.md Task 8).
 *
 * It resolves every colour from the live custom properties and recomputes each contrast
 * ratio on load, so editing a token in theme.css changes what this page reports. It is not
 * one of the five P0 screens.
 */

const PALETTE = [
  { token: '--bg', role: 'Page background' },
  { token: '--surface', role: 'Cards, panels, rows' },
  { token: '--ink', role: 'Primary text; text on accent fills' },
  { token: '--slate', role: 'Dark surfaces: header, rail, drawer' },
  { token: '--muted', role: 'Borders, icons, secondary text on surface' },
  { token: '--accent', role: 'Fills, active states, focus ring' },
  { token: '--on-slate-muted', role: 'De-emphasised text on dark surfaces' },
  { token: '--warning', role: 'Blocked / fix-first' },
  { token: '--negative', role: 'Complaints, rejected ideas' },
]

/** `need: 0` marks a pairing the system forbids: failing is the correct result for it. */
const PAIRINGS = [
  { fg: '--ink', bg: '--bg', label: 'ink on bg', need: 4.5 },
  { fg: '--ink', bg: '--surface', label: 'ink on surface', need: 4.5 },
  { fg: '--bg', bg: '--slate', label: 'bg text on slate', need: 4.5 },
  { fg: '--accent', bg: '--slate', label: 'accent text on slate', need: 4.5 },
  { fg: '--on-slate-muted', bg: '--slate', label: 'de-emphasised text on slate', need: 4.5 },
  { fg: '--ink', bg: '--accent', label: 'ink on accent fill', need: 4.5 },
  { fg: '--muted', bg: '--surface', label: 'muted on surface', need: 4.5 },
  { fg: '--warning', bg: '--surface', label: 'warning text on surface', need: 4.5 },
  { fg: '--negative', bg: '--surface', label: 'negative text on surface', need: 4.5 },
  { fg: '--slate', bg: '--bg', label: 'secondary-on-bg text on bg', need: 4.5 },
  { fg: '--muted', bg: '--bg', label: 'muted on bg (large text only)', need: 3 },
  { fg: '--accent', bg: '--bg', label: 'accent text on bg — must fail', need: 0 },
  { fg: '--accent', bg: '--surface', label: 'accent text on surface — must fail', need: 0 },
  { fg: '--muted', bg: '--slate', label: 'muted text on slate — must fail', need: 0 },
]

const TYPE_STEPS = [
  { token: '--text-display', label: 'Display 2.25rem / 600', className: 'step-display' },
  { token: '--text-title', label: 'Title 1.5rem / 600', className: 'step-title' },
  { token: '--text-heading', label: 'Heading 1.125rem / 600', className: 'step-heading' },
  { token: '--text-body', label: 'Body 1rem / 400', className: 'step-body' },
  { token: '--text-small', label: 'Small 0.875rem / 400', className: 'step-small' },
  { token: '--text-micro', label: 'Micro 0.75rem / 500', className: 'step-micro' },
]

const SPACE_STEPS = ['1', '2', '3', '4', '6', '8', '12', '16']

const ALL_TOKENS = [...new Set([...PALETTE.map((p) => p.token), ...PAIRINGS.flatMap((p) => [p.fg, p.bg])])]

export function TokensScreen() {
  const [colors, setColors] = useState<Record<string, string> | null>(null)

  useEffect(() => {
    // The CSSOM is exactly the "external system" this rule carves out: resolving a custom
    // property needs a mounted probe element, so it cannot be derived during render without
    // mutating the DOM mid-render, which is the worse of the two.
    // oxlint-disable-next-line react/set-state-in-effect
    setColors(readTokenColors(ALL_TOKENS))
  }, [])

  return (
    <div className="tokens">
      <header className="tokens-header">
        <h1>Design tokens</h1>
        <p>
          Reference for the theme in <code>src/styles/theme.css</code>. Colours are read from the
          live custom properties and the ratios are computed here, so a token edit that breaks a
          pairing shows up below as a regression.
        </p>
      </header>

      <section aria-labelledby="palette-heading">
        <h2 id="palette-heading">Palette</h2>
        <ul className="swatches">
          {PALETTE.map((entry) => (
            <li key={entry.token} className="swatch">
              <div className="swatch-chip" style={{ background: `var(${entry.token})` }} />
              <div>
                <code>{entry.token}</code>
                <span className="swatch-hex tabular">{colors?.[entry.token] ?? '…'}</span>
                <span className="swatch-role">{entry.role}</span>
              </div>
            </li>
          ))}
        </ul>
      </section>

      <section aria-labelledby="contrast-heading">
        <h2 id="contrast-heading">Contrast</h2>
        <table className="contrast-table">
          <thead>
            <tr>
              <th scope="col">Pairing</th>
              <th scope="col">Sample</th>
              <th scope="col">Ratio</th>
              <th scope="col">Level</th>
              <th scope="col">Meets intent</th>
            </tr>
          </thead>
          <tbody>
            {PAIRINGS.map((pair) => {
              const fg = colors?.[pair.fg]
              const bg = colors?.[pair.bg]
              const ratio = fg && bg ? contrastRatio(fg, bg) : null
              const ok = ratio === null ? null : pair.need === 0 ? ratio < 3 : ratio >= pair.need
              return (
                <tr key={pair.label}>
                  <th scope="row">{pair.label}</th>
                  <td>
                    <span
                      className="sample"
                      style={{ color: `var(${pair.fg})`, background: `var(${pair.bg})` }}
                    >
                      Sample text
                    </span>
                  </td>
                  <td className="tabular">{ratio === null ? '…' : `${ratio.toFixed(2)}:1`}</td>
                  <td>{ratio === null ? '…' : contrastLevel(ratio)}</td>
                  <td>{ok === null ? '…' : ok ? 'yes' : 'NO — regression'}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </section>

      <section aria-labelledby="type-heading">
        <h2 id="type-heading">Type scale</h2>
        <ul className="type-list">
          {TYPE_STEPS.map((step) => (
            <li key={step.token}>
              <span className={step.className}>Evidence-backed growth opportunities</span>
              <code>{step.token}</code>
              <span className="swatch-role">{step.label}</span>
            </li>
          ))}
        </ul>
      </section>

      <section aria-labelledby="space-heading">
        <h2 id="space-heading">Spacing scale</h2>
        <ul className="space-list">
          {SPACE_STEPS.map((step) => (
            <li key={step}>
              <span className="space-bar" style={{ width: `var(--space-${step})` }} />
              <code>--space-{step}</code>
            </li>
          ))}
        </ul>
      </section>

      <section aria-labelledby="radius-heading">
        <h2 id="radius-heading">Radii</h2>
        <ul className="radius-list">
          <li>
            <span className="radius-box radius-chip" />
            <code>--radius-chip</code>
          </li>
          <li>
            <span className="radius-box radius-card" />
            <code>--radius-card</code>
          </li>
          <li>
            <span className="radius-box radius-bar" />
            <code>--radius-bar</code>
          </li>
        </ul>
      </section>
    </div>
  )
}
