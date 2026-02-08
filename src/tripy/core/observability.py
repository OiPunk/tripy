from __future__ import annotations

import logging

from fastapi import FastAPI

from tripy.core.config import Settings
from tripy.db.session import engine

logger = logging.getLogger(__name__)


def _parse_otlp_headers(header_string: str | None) -> dict[str, str] | None:
    if not header_string:
        return None
    headers: dict[str, str] = {}
    for part in header_string.split(","):
        stripped = part.strip()
        if not stripped or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        headers[key.strip()] = value.strip()
    return headers or None


def setup_observability(app: FastAPI, settings: Settings) -> None:
    if not settings.otel_enabled:
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.logging import LoggingInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from opentelemetry.sdk.resources import SERVICE_NAME, Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    except Exception as exc:  # pragma: no cover - guarded by dependency presence
        logger.warning("OpenTelemetry dependencies are not available: %s", exc)
        return

    if getattr(app.state, "otel_instrumented", False):
        return

    resource = Resource.create(
        {
            SERVICE_NAME: settings.otel_service_name,
            "service.version": settings.app_version,
            "deployment.environment": settings.environment,
        }
    )

    provider = TracerProvider(resource=resource)

    if settings.otel_exporter_otlp_endpoint:
        exporter = OTLPSpanExporter(
            endpoint=settings.otel_exporter_otlp_endpoint,
            headers=_parse_otlp_headers(settings.otel_exporter_otlp_headers),
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))

    if settings.otel_exporter_console:
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
    SQLAlchemyInstrumentor().instrument(engine=engine, tracer_provider=provider)

    if settings.otel_log_correlation:
        LoggingInstrumentor().instrument(set_logging_format=False)

    app.state.otel_instrumented = True
