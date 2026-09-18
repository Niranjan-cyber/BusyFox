import type { ReactNode } from 'react'
import './Card.css'

/** Composable surface used by both screens. Composition over configuration. */

export function Card({ children, tone = 'default' }: { children: ReactNode; tone?: 'default' | 'blocked' }) {
  return <article className={tone === 'blocked' ? 'card card-blocked' : 'card'}>{children}</article>
}

export function CardHeader({ children }: { children: ReactNode }) {
  return <header className="card-header">{children}</header>
}

export function CardBody({ children }: { children: ReactNode }) {
  return <div className="card-body">{children}</div>
}

export function CardFooter({ children }: { children: ReactNode }) {
  return <footer className="card-footer">{children}</footer>
}

/** A titled region of a screen. Headings stay in document order; nothing skips a level. */
export function Section({
  title,
  description,
  children,
}: {
  title: string
  description?: ReactNode
  children: ReactNode
}) {
  const id = title.toLowerCase().replace(/[^a-z0-9]+/g, '-')
  return (
    <section className="section" aria-labelledby={id}>
      <div className="section-head">
        <h2 id={id}>{title}</h2>
        {description ? <p className="section-description">{description}</p> : null}
      </div>
      {children}
    </section>
  )
}
