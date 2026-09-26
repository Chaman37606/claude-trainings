"""OpenTelemetry wiring: traces + metrics over OTLP, disabled by default so
pytest never touches the network. Enabled by setting
OTEL_EXPORTER_OTLP_ENDPOINT (see docs/observability_setup.md for the
pre-provisioned collector/Tempo/Prometheus/Grafana stack this points at).
"""
from __future__ import annotations

from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.system_metrics import SystemMetricsInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from backend.app.config import settings

_initialized = False

# Module-level handles other modules import to create spans/record metrics.
# trace.get_tracer()/meter.create_*() return proxy objects that transparently
# start delegating to the real SDK provider the moment setup_observability()
# calls set_tracer_provider()/set_meter_provider() — no rebinding needed, and
# these work as no-ops if observability is never enabled.
tracer = trace.get_tracer("biomed_rag")
meter = metrics.get_meter("biomed_rag")

tool_call_counter = meter.create_counter(
    "tool_call_count", description="Number of agent tool calls, by tool and outcome"
)
tool_call_duration = meter.create_histogram(
    "tool_call_duration_seconds", unit="s", description="Agent tool call latency"
)
llm_call_duration = meter.create_histogram(
    "llm_call_duration_seconds", unit="s", description="Anthropic Messages API call latency"
)
llm_token_usage = meter.create_counter(
    "llm_token_usage", description="Anthropic token usage, by model and token type"
)
rag_retrieve_duration = meter.create_histogram(
    "rag_retrieve_duration_seconds", unit="s", description="RAG retrieval latency, by domain"
)


def setup_observability(app: FastAPI) -> None:
    global _initialized

    if not settings.otel_exporter_otlp_endpoint or _initialized:
        return
    _initialized = True

    resource = Resource.create({"service.name": settings.otel_service_name})

    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint, insecure=True))
    )
    trace.set_tracer_provider(tracer_provider)

    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[
            PeriodicExportingMetricReader(
                OTLPMetricExporter(endpoint=settings.otel_exporter_otlp_endpoint, insecure=True)
            )
        ],
    )
    metrics.set_meter_provider(meter_provider)

    FastAPIInstrumentor.instrument_app(app)
    RequestsInstrumentor().instrument()
    SystemMetricsInstrumentor().instrument()
