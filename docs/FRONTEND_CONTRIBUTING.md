# Frontend Contributing Guide

This guide covers `tripy/web` contribution standards.

## Stack

- React + TypeScript + Vite
- API layer via Axios in `src/api.ts`
- i18n dictionary in `src/i18n.ts`
- Playwright E2E + axe a11y audit

## Local Development

```bash
cd /Users/liweiguang/aiagent/ctrip_assistant/web
npm install
cp .env.example .env
npm run dev
```

Default URL: `http://127.0.0.1:4174`

## Mandatory Quality Gates

```bash
npm run build
npm run test:e2e
```

`test:e2e` validates:
- login flow
- graph conversation flow
- admin users flow
- accessibility audit (axe serious/critical = 0)

## Engineering Conventions

- Keep all network requests in `src/api.ts`.
- Use typed models from `src/types.ts` for request/response boundaries.
- Add `data-testid` for workflow-critical UI actions.
- Preserve keyboard-only operation for navigation and primary actions.

## I18n Rules

- Every visible string must map to `src/i18n.ts` for `en` and `zh`.
- Add new keys in both locales in the same change.
- Prefer concise, domain-specific wording over generic copy.

## Accessibility Rules

- Keep form labels explicit and unique.
- Use landmark regions (`header`, `main`, `footer`) and skip link.
- Preserve semantic tab navigation (`tablist`, `tab`, `tabpanel`).
- Keep async status in `aria-live="polite"` region.

## PR Checklist

- [ ] UI strings updated in both languages
- [ ] Keyboard navigation verified for changed workflows
- [ ] `npm run build` passes
- [ ] `npm run test:e2e` passes
- [ ] Token usage follows `docs/UI_DESIGN_TOKENS.md`
