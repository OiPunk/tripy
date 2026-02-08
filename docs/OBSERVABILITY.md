# Observability

`tripy` supports OpenTelemetry-based tracing for API and database operations.

## Enable Tracing

Set in `.env`:

```env
OTEL_ENABLED=true
OTEL_SERVICE_NAME=tripy-api
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318/v1/traces
OTEL_EXPORTER_OTLP_HEADERS=authorization=Bearer your-token
OTEL_EXPORTER_CONSOLE=false
```

## Instrumented Components

- FastAPI request lifecycle
- SQLAlchemy query spans
- Optional log correlation

## Notes

- If `OTEL_ENABLED=false`, instrumentation is skipped.
- If OTLP endpoint is not configured and console exporter is enabled, spans are printed to stdout.
