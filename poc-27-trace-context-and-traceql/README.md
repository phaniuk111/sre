# POC 27: trace context, sampling, TraceQL and traces turned into metrics

**Books:** *Observability with Grafana* chapters 2 (spans, traces, protocols, sampling) and 6 (Tempo, TraceQL, propagation headers, baggage, architecture); *Mastering Prometheus* chapters 14 and 15 (OpenTelemetry, exemplars, sampling)

A trace exists only because every service copies a few bytes from the request it received into the requests it makes. Get that wrong and spans split into separate traces; sample independently in each service and you keep fragments. `tracing.py` implements the header formats, baggage, sampling, a small TraceQL, and the two collector connectors that produce RED metrics and service graphs.

| In `tracing.py` | Idea |
|---|---|
| `parse_traceparent()`, `traceparent()` | W3C `00-{32 hex trace}-{16 hex parent}-{flags}`; all-zero IDs and unknown versions are invalid |
| `to_b3_single()`, `to_b3_multi()`, `to_uber()` | Zipkin B3 and Jaeger `uber-trace-id` for older services |
| `to_xray()`, `from_xray()`, `xray_id_valid()` | `Root=1-{epoch}-{24 hex};Parent=…;Sampled=1`; X-Ray needs the first 8 hex digits to be a recent epoch time, so use an X-Ray-compatible ID generator |
| `encode_baggage()`, `decode_baggage()` | W3C baggage: percent-encoded, at most 64 members and 8192 bytes, readable by anyone on the wire |
| `ratio_decision()`, `propagate()` | head sampling from the trace ID; parent-based sampling keeps 100% of traces whole, independent sampling leaves fragments |
| `tail_keep()` | tail sampling: every error, half the slow traces, 1% of the rest |
| `spanset()`, `structural()`, `count_gt()`, `avg_duration_gt()` | TraceQL: `{span.http.method="GET" && duration > 100}`, `>` child, `>>` descendant, `~` sibling, `\| count() > 2`, `\| avg(duration) > 200ms` |
| `span_metrics()`, `service_graph()` | the `spanmetrics` and `servicegraph` connectors: calls and duration histograms per span; client→server edges with request and failure counts |

```bash
python -m pytest -q
```

## On AWS
| Need | Service |
|---|---|
| Collect and export traces | AWS Distro for OpenTelemetry (ADOT) collector: OTLP in, `awsxray` exporter to X-Ray or OTLP to Tempo / Grafana Cloud |
| Propagation with AWS services | X-Ray header (`X-Amzn-Trace-Id`) through ALB, API Gateway, Lambda; ADOT SDKs propagate both W3C and X-Ray |
| Store and search traces | AWS X-Ray (and CloudWatch Application Signals on top), or Tempo on EKS with S3 |
| Service map and RED metrics | X-Ray service map / Application Signals; or the collector's `spanmetrics` and `servicegraph` connectors writing to AMP |
| Metric → trace | exemplars from AMP in Amazon Managed Grafana linking to X-Ray or Tempo |

## Interview talking points
* A trace is a tree of spans sharing a trace ID; each span has its own ID and its parent's ID.
* Propagation is headers: W3C `traceparent` (plus `tracestate`) is the standard; B3 and Jaeger headers are legacy; X-Ray has its own.
* Parent-based head sampling keeps traces complete; tail sampling decides after the trace finishes, so you can keep every error.
* Baggage carries context such as a tenant ID downstream for observability without changing each service's data model; never put secrets in it.
* Traces become metrics (span metrics) and maps (service graphs); metrics link back to traces through exemplars.
