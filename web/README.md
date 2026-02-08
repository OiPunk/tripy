# tripy-web

Frontend console for `tripy`.

## Features

- JWT login + local session persistence
- Graph chat workspace (`/graph/execute`)
- RBAC identity inspector (`/auth/me`)
- Admin users table (`/admin/users`)
- Health monitor (`/health/live`, `/health/ready`)
- Runtime i18n (`en` / `zh`)
- Keyboard-accessible tab navigation + ARIA landmarks
- Playwright E2E with axe accessibility audit

## Run

```bash
npm install
cp .env.example .env
npm run dev
```

Default URL: [http://127.0.0.1:4174](http://127.0.0.1:4174)

## Build

```bash
npm run build
npm run preview -- --host 127.0.0.1 --port 4174
```

## E2E + A11y Audit

```bash
npm run test:e2e
```

## Environment

- `VITE_API_BASE`: backend API base URL, defaults to `http://localhost:8000/api/v1`.
