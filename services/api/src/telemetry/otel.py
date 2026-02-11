from __future__ import annotations

import logging
from typing import Optional

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
) -> Optional[TracerProvider]:
    """
    OpenTelemetry setup (safe-by-default).

    Rules:
    - If enabled=False -> install a TracerProvider with NO exporters (no network, no spam).
    - If enabled=True but otlp_endpoint missing/empty -> behave like disabled (still no exporters).
    - If enabled=True and otlp_endpoint provided -> configure OTLP/HTTP exporter.

    Returns the TracerProvider (always), never raises.
    """
    global _TRACER_PROVIDER_SET

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    # Avoid "Overriding of current TracerProvider is not allowed" warnings in some setups.
    # If the app reloads, we keep the already-set provider.
    if not _TRACER_PROVIDER_SET:
        trace.set_tracer_provider(provider)
        _TRACER_PROVIDER_SET = True
    else:
        try:
            # Reuse existing provider if already set (best effort).
            current = trace.get_tracer_provider()
            if isinstance(current, TracerProvider):
                provider = current
        except Exception:
            # fall back to the newly created provider
            pass

    if not enabled:
        logger.info("otel_disabled")
        return provider

    endpoint = (otlp_endpoint or "").strip()
    if not endpoint:
        logger.info("otel_disabled_missing_endpoint")
        return provider

    try:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

        exporter = OTLPSpanExporter(endpoint=f"{endpoint.rstrip('/')}/v1/traces")
        provider.add_span_processor(BatchSpanProcessor(exporter))
        logger.info("otel_enabled", extra={"otlp_endpoint": endpoint})
        return provider
    except Exception as e:
        # IMPORTANT: never crash the service because telemetry isn't available
        logger.warning("otel_setup_failed", extra={"error": str(e)})
        return provider
