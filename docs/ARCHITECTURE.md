# Architecture

## Layers

- `src/tripy/core`: configuration, logging, security, exception handling.
- `src/tripy/db`: SQLAlchemy models, engine/session, bootstrap init.
- `src/tripy/repositories`: persistence abstraction.
- `src/tripy/services`: business logic and graph orchestration adapter.
- `src/tripy/api`: HTTP contracts and dependency wiring.
- `alembic/`: schema migration lifecycle.
- `graph_chat/` + `tools/`: legacy workflow and business tools (kept for compatibility).

## Request Flow

1. `FastAPI` receives request.
2. Dependencies resolve locale, DB session, and authenticated user.
3. RBAC dependencies enforce role/permission checks for protected routes.
4. Service layer executes domain logic.
5. Response schemas enforce stable API contracts.

## Graph Integration Strategy

- Legacy graph runtime is loaded lazily from `graph_chat.finally_graph`.
- New API guarantees typed request/response, auth isolation, and interrupt-aware responses.
- If graph runtime is unavailable, API returns `503` with stable message.

## Observability

- OpenTelemetry can be enabled via environment variables.
- FastAPI and SQLAlchemy are instrumented for trace propagation/export.

## RBAC Model

- `users`
- `roles`
- `permissions`
- `user_roles` (many-to-many)
- `role_permissions` (many-to-many)
