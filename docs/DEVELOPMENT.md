# Development

## Local Commands

```bash
make install-dev
make run
make lint
make typecheck
make test
make migrate
```

## Environment Variables

See `.env.example` for the full list.

Most important variables:

- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `OPENAI_API_KEY`
- `OPENAI_API_BASE`
- `LLM_MODEL`
- `GRAPH_ENABLED`
- `OTEL_ENABLED`
- `OTEL_EXPORTER_OTLP_ENDPOINT`

## API Base Path

All endpoints are namespaced under:

`/api/v1`

OpenAPI docs are available at:

- `/docs`
- `/openapi.json`

## Database Migrations

```bash
alembic upgrade head
alembic downgrade -1
```

`tripy` also exposes a convenience CLI entrypoint:

```bash
tripy-db-upgrade
```
