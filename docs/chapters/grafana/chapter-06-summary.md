# Grafana chapter 6: Traces with Tempo and TraceQL, and how context propagates

*Observability with Grafana (Rob Chapman and Peter Holmes, Packt, 2024). Course lesson: `#g-6`. Code: POC 27 · 5. Read: full text, one pass; all figures seen.*

## Summary

Tempo stores traces in object storage and searches them with **TraceQL**, modelled like LogQL on PromQL. At the version the book covers (2.3), TraceQL selects spans and traces well but analysis is limited; that is changing fast.

From a span, *Logs for this span* opens Loki filtered by the span’s service name and namespace. In the other direction, services that write trace and span IDs into their logs let Loki link back to Tempo. From a metric, exemplars open a trace. That three-way movement is what makes the stack worth more than its parts.

Spans reach the collector separately from each service; what ties them together is the context each service passes in request headers.

OTel SDKs speak W3C, B3 and Jaeger. AWS X-Ray’s header isn’t in the mainline distribution, which is why AWS ships its own distribution, ADOT. Baggage is the elegant part: a top-level service can pass `tenantId` so a downstream service can record it in telemetry without adding it to its own data model.

## Key ideas

- Tempo’s view of a trace, its search modes and the service graph
- TraceQL: intrinsic and attribute fields, selection, structural operators, aggregates
- Pivoting between traces, logs and metrics
- OTLP, Zipkin and Jaeger; W3C traceparent, B3, Jaeger headers and baggage
- Tempo’s architecture and the metrics generator

## What the lesson covers

- The big picture
- TraceQL
- Pivoting
- Context propagation
- Tempo’s architecture

## Terms

TraceQL, Distributor, Ingester, Object storage, Across the books, Trace context

## Interview line

Tempo stores traces in object storage and I search them with TraceQL: intrinsic fields like status and duration, span and resource attributes, and structural operators for parent, descendant and sibling relationships. Traces only work if context propagates, so I standardise on W3C traceparent, use baggage for things like tenant IDs, and link spans to logs and metrics to traces through exemplars. Tempo’s metrics generator turns spans into RED metrics and service graphs.

## On AWS

X-Ray is AWS’s trace store, with Application Signals building service maps and SLOs on it; Tempo on EKS with S3 is the self-managed option, and Amazon Managed Grafana can query both. ADOT handles X-Ray’s `X-Amzn-Trace-Id` alongside W3C so traces survive ALB, API Gateway and Lambda hops; use an X-Ray-compatible trace ID generator when exporting to X-Ray. POC 27 converts headers, enforces baggage limits, evaluates TraceQL structural operators and builds span metrics and a service graph.

## Takeaways

- TraceQL: intrinsics, span and resource attributes, structural operators, aggregates.
- Traces exist only through propagation: standardise on W3C, use baggage carefully.
- Pivot freely: spans to logs, logs to traces, metrics to traces.
