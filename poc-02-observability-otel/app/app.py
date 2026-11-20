"""A tiny 'checkout' service instrumented with OpenTelemetry, exporting to the
AWS Distro for OpenTelemetry (ADOT) collector -> CloudWatch (EMF metrics),
X-Ray (traces) and CloudWatch Logs (structured logs carrying trace IDs).

Demonstrates (book ch. 9):
  * RED metrics (Rate, Errors, Duration) per route - a starting point for SLIs
  * Causal correlation: trace_id/span_id injected into every structured log
  * CUJ propagation: the critical user journey name travels in OTel *baggage*
    so every downstream span/metric can be sliced by CUJ (Google's
    "CUJ as another dimension" idea)
  * Version metadata on responses for client-focused change supervision (ch. 14)

Run:  docker compose up  (see ../docker-compose.yml) then
      curl -H 'x-cuj: checkout' localhost:8080/checkout
"""
from __future__ import annotations

import json
import logging
import os
import random
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

from opentelemetry import baggage, context, metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

SERVICE = os.getenv("OTEL_SERVICE_NAME", "checkout")
VERSION = os.getenv("SERVICE_VERSION", "1.4.2")
ERROR_RATE = float(os.getenv("INJECT_ERROR_RATE", "0.01"))
ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

# Runtime correlation: every signal is attached to a *resource*.
resource = Resource.create({
    "service.name": SERVICE,
    "service.version": VERSION,
    "deployment.environment": os.getenv("ENV", "dev"),
    "cloud.provider": "aws",
})

tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=ENDPOINT, insecure=True)))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=ENDPOINT, insecure=True), export_interval_millis=10_000)
metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[reader]))
meter = metrics.get_meter(__name__)

requests_total = meter.create_counter("http.server.requests", description="RED: rate")
errors_total = meter.create_counter("http.server.errors", description="RED: errors")
duration = meter.create_histogram("http.server.duration", unit="ms", description="RED: duration")


class JsonTraceFormatter(logging.Formatter):
    """Structured ('wide event') logs that join to traces in X-Ray / CloudWatch."""

    def format(self, record: logging.LogRecord) -> str:
        span = trace.get_current_span().get_span_context()
        event = {
            "ts": round(time.time(), 3),
            "level": record.levelname,
            "msg": record.getMessage(),
            "service": SERVICE,
            "version": VERSION,
            "trace_id": format(span.trace_id, "032x") if span.is_valid else None,
            "span_id": format(span.span_id, "016x") if span.is_valid else None,
            "cuj": baggage.get_baggage("cuj"),
        }
        event.update(getattr(record, "fields", {}))
        return json.dumps(event)


handler = logging.StreamHandler()
handler.setFormatter(JsonTraceFormatter())
log = logging.getLogger("checkout")
log.addHandler(handler)
log.setLevel(logging.INFO)


def call_dependency(name: str, p50_ms: float) -> None:
    with tracer.start_as_current_span(f"dependency:{name}") as span:
        span.set_attribute("cuj", baggage.get_baggage("cuj") or "unknown")
        time.sleep(random.lognormvariate(0, 0.4) * p50_ms / 1000)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        cuj = self.headers.get("x-cuj", "browse")
        token = context.attach(baggage.set_baggage("cuj", cuj))
        start = time.perf_counter()
        status = 200
        try:
            with tracer.start_as_current_span(f"GET {self.path}") as span:
                span.set_attribute("http.route", self.path)
                span.set_attribute("cuj", cuj)
                call_dependency("inventory", 20)
                call_dependency("payments", 45)
                if random.random() < ERROR_RATE:
                    status = 503
                    span.set_status(trace.Status(trace.StatusCode.ERROR, "injected failure"))
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            attrs = {"route": self.path, "cuj": cuj, "status": str(status)}
            requests_total.add(1, attrs)
            duration.record(elapsed_ms, attrs)
            if status >= 500:
                errors_total.add(1, attrs)
            log.info("request", extra={"fields": {"route": self.path, "status": status, "duration_ms": round(elapsed_ms, 1)}})
            self.send_response(status)
            # Client-focused change supervision: tell callers which version served them.
            self.send_header("x-served-by-version", VERSION)
            self.end_headers()
            self.wfile.write(json.dumps({"ok": status == 200}).encode())
            context.detach(token)

    def log_message(self, *args) -> None:  # silence default access log
        pass


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
