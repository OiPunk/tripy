## Tripy v0.2.0

Tripy reaches a production-ready open-source baseline with enterprise backend capabilities and a tested web console.

### Highlights

- Introduced `tripy` project identity and modernized packaging layout
- Added Alembic migration framework with initial schema
- Implemented RBAC model and permission-gated API endpoints
- Integrated OpenTelemetry hooks for API and DB instrumentation
- Delivered React web console with runtime i18n (`en` / `zh`)
- Added keyboard-accessible navigation and ARIA landmarks
- Added Playwright E2E tests with axe accessibility audit

### API updates

- `GET /api/v1/admin/users` now protected by `users:read`
- `POST /api/v1/graph/execute` now protected by `graph:execute`
- Auth responses expose resolved roles and permissions

### Quality gates

- Backend: `ruff`, `mypy`, `pytest`
- Frontend: `vite build`, Playwright E2E, accessibility audit
- CI now runs both backend quality and frontend E2E checks

### Upgrade notes

- Run migrations before startup:

```bash
alembic upgrade head
```

- For web local dev:

```bash
cd web
npm install
npm run dev
```
