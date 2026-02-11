from __future__ import annotations

import logging

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

logger = logging.getLogger(__name__)

_TRACER_PROVIDER_SET = False


def setup_otel(
    service_name: str,
    enabled: bool = False,
    otlp_endpoint: str | None = None,
) -> TracerProvider:
    """
    OpenTelemetry setup (safe-by-default).

    Rules:
    - enabled=False -> install provider with NO exporters (no network, no spam)
    - enabled=True + missing/empty endpoint -> behave like disabled
    - enabled=True + endpoint -> configure OTLP/HTTP exporter

    Returns a TracerProvider (never raises).
    """
    global _TRACER_PROVIDER_SET

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    # Avoid warnings if the app reloads: keep the already-set provider when possible.
    if not _TRACER_PROVIDER_SET:
        trace.set_tracer_provider(provider)
        _TRACER_PROVIDER_SET = True
    else:
        provider = _get_current_provider_fallback(provider)

    if not enabled:
        logger.info("otel_disabled")
        return provider

    endpoint = (otlp_endpoint or "").strip()
    if not endpoint:
        logger.info("otel_disabled_missing_endpoint")
        return provider

    try:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )

        exporter = OTLPSpanExporter(
            endpoint=f"{endpoint.rstrip('/')}/v1/traces",
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))
        logger.info("otel_enabled", extra={"otlp_endpoint": endpoint})
    except Exception as e:
        # Never crash the service because telemetry isn't available.
        logger.warning("otel_setup_failed", extra={"error": str(e)})

    return provider


def _get_current_provider_fallback(fallback: TracerProvider) -> TracerProvider:
    try:
        current = trace.get_tracer_provider()
        if isinstance(current, TracerProvider):
            return current
    except Exception:
        pass
    return fallback
