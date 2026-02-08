# UI Design Tokens Specification

Token baseline for `tripy/web/src/styles.css`.

## Token Strategy

- Tokens are defined in `:root` with CSS custom properties.
- Component styles should consume tokens, not raw color literals.
- New tokens require semantic naming and documented intent.

## Typography

Primary tokens:
- `--font-body`
- `--font-display`

Scale guidance:
- Body: `14px`
- Meta: `11px`-`13px`
- Section heading: `20px`
- Hero heading: `clamp(30px, 3.4vw, 50px)`

## Color System

Background/surfaces:
- `--bg-top`, `--bg-bottom`
- `--panel`, `--panel-strong`

Text:
- `--ink`, `--ink-muted`

Brand/action:
- `--teal`, `--teal-strong`

State accents:
- Success/online states use green-tinted chips
- Warning states use amber-tinted containers
- Error/system messages use red-tinted containers

Elevation and borders:
- `--line`
- `--shadow-1`, `--shadow-2`

## Layout Tokens

Spacing rhythm:
- Panel gaps: `14px`-`18px`
- Form/control gaps: `6px`-`10px`
- Primary panel padding: `20px`-`30px`

Corner radii:
- Primary cards: `20px`-`22px`
- Interactive controls: `12px`-`14px`
- Pills/chips: `999px`

## Motion

- Entry animation: `rise`
- Duration envelope: `0.18s`-`0.44s`
- Prefer transform + opacity transitions

## Accessibility Constraints

- Maintain visible focus states for all interactive controls.
- Ensure text and controls meet WCAG AA contrast targets.
- Preserve minimum control size suitable for touch usage.

## Governance

When updating token semantics:
1. Update `src/styles.css` token values/usages.
2. Update this document.
3. Run `npm run test:e2e` and verify no a11y regression.
