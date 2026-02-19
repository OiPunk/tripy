# UI Design Tokens Specification

Token baseline for `tripy/web/src/styles.css`.

## Token Strategy

- Define semantic tokens in `:root` only.
- Consume tokens in component styles; avoid one-off hardcoded values.
- Keep visual direction consistent: cloud-control, high-clarity, low-noise.

## Typography

Primary tokens:
- `--font-body`
- `--font-display`

Scale guidance:
- Body: `14px`
- Meta: `10px`-`13px`
- Section heading: `22px`
- Hero heading: `clamp(32px, 3.7vw, 56px)`

## Color System

Background:
- `--bg-0`, `--bg-1`

Surface:
- `--panel`, `--panel-strong`
- `--line`

Text:
- `--ink`, `--ink-muted`

Brand and state:
- `--brand`, `--brand-strong`
- `--accent` (success / healthy)
- `--amber` (warning / interruption)
- `--danger` (error / failure)

## Elevation and Shape

- `--shadow-soft`, `--shadow-deep`
- `--radius-card`, `--radius-control`, `--radius-pill`

## Motion

- Entry motion: `rise`
- Async feedback motion: `pulse`
- Duration envelope: `0.18s`-`0.45s`
- Prefer transform + opacity transitions

## Layout

- Hero + telemetry split on desktop, stacked on tablet/mobile
- Sticky utility rail on large screens only
- Interaction density reduces automatically under `940px`

## Accessibility Constraints

- Keep explicit focus-visible rings for all controls.
- Preserve landmark regions and skip-link behavior.
- Preserve semantic `tablist` / `tab` / `tabpanel` structure.
- Keep color contrast at WCAG AA minimum.

## Governance

When updating token semantics:
1. Update `web/src/styles.css` tokens and usages.
2. Update this document.
3. Run `npm run build` and `npm run test:e2e`.
