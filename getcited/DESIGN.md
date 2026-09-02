# Design System — GetCited

## Aesthetic stance
Clinical calm with a sharp edge — the trustworthy, slightly premium feel a med-spa
owner expects from a vendor, not a Silicon Valley dashboard. Lots of whitespace,
one confident accent, zero hype gradients.

## Type
- Heading: system humanist sans (`-apple-system, "Segoe UI", Inter, sans-serif`),
  weight 700. h1 clamp(2rem, 5vw, 3.25rem); h2 1.6rem; h3 1.15rem.
- Body: same family, weight 400, line-height 1.65, max-width 65ch.
- Mono: `ui-monospace, "SF Mono", Menlo, monospace` — only for code/keys in docs.

## Color
- Surface: `#fbfaf8` — warm off-white page background
- Surface alt: `#ffffff` — cards, raised areas (with a hairline border)
- Text: `#1a1a1a` primary / `#5c5c5c` muted
- Accent: `#0f766e` (deep teal) — single accent, used for CTAs + links only
- Border: `#e7e4df`
- Success / warning / danger: `#15803d` / `#b45309` / `#b91c1c`

## Spacing
- Base unit: 8px
- Section vertical rhythm: 80px desktop / 48px mobile
- Card padding: 24px

## Motion
- Default transition: 150ms ease (color, background, border only)
- Rule: hover states animate; layout never animates. No scroll-jacking, no parallax.

## What this system rejects
- No gradients, glassmorphism, or neon.
- No colored headings (hierarchy is size + weight only).
- No stock "doctor smiling at laptop" photography.
- No more than one accent color.
- No dark mode for v1 (scope creep).
