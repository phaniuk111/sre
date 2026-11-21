# Grafana chapter 12: Real user monitoring, continuous profiling and load testing

*Observability with Grafana (Rob Chapman and Peter Holmes, Packt, 2024). Course lesson: `#g-12`. Code: POC 30 · 7. Read: full text, one pass; all figures seen; lesson covers chapters 12–13.*

## Summary

RUM measures what real users experience in their browsers, all the way through to the backend. Grafana’s version is the open-source **Faro Web SDK** in your web app, a hosted collector (or your own agent), and a Frontend Observability app with Overview, Errors and Sessions tabs. By default Faro sends Web Vitals, unhandled exceptions, browser details, page URL changes, a session ID and activity traces; it uses opentelemetry-js for tracing. Logs go to Loki and traces to Tempo; the metrics are generated from logs with LogQL.

Setting up an app asks for a name, the allowed CORS origins, extra Loki labels and an acknowledgement of the cost, then offers NPM, CDN-with-tracing or CDN-without-tracing snippets.

From the Sessions tab, a session ID opens its own vitals, exceptions and, if the backend is traced, links into the traces and on to backend logs: one user’s experience reconstructed end to end. A session starts when Faro initialises and ends when the visitor leaves (the end event isn’t sent by default). Enhancements, each with configuration effort and some browser overhead: frontend tracing, custom errors, measurements, logs, and events (stored in Loki with `kind=event`).

Profiles are the fourth signal: which functions use CPU and memory, sampled continuously (every 15 seconds by default in Pyroscope, with a few percent overhead), so code behaviour can be tied to what users were doing. Pyroscope (founded 2020, acquired 2023, merged with Grafana’s Phlare) uses the same horizontally scalable, object-storage architecture as Loki, Mimir and Tempo. Its query is selection only: a profile type and tags.

## Key ideas

- What Faro collects and how Frontend Observability is set up
- Web Vitals and their targets
- Pivoting from a user session to backend traces and logs
- Continuous profiling with Pyroscope: top table, flame graphs, eBPF versus SDKs
- The six kinds of load test, and k6 checks, thresholds, options and life cycle

## What the lesson covers

- Real user monitoring
- Continuous profiling
- Load testing

## Claims and numbers

- Profiles are the fourth signal: which functions use CPU and memory, sampled continuously (every 15 seconds by default in Pyroscope, with a few percent overhead), so code behaviour can be tied to what users were doing.

## Terms

Faro Web SDK, Top table, Self, Total, Flame graph, Checks, thresholds, Across the books, Client-side telemetry, Fleet-wide profiling, Continuous profiling, Load test types

## Interview line

I measure the user’s side with RUM, judging Web Vitals such as LCP, INP and CLS at the 75th percentile and following a bad session into backend traces. I use continuous profiling to explain why code is slow or expensive: self time for hot functions, total time for hot paths. And I load test with thresholds taken from our SLOs, using smoke tests after every deploy and stress, spike, breakpoint and soak tests before big events, with their telemetry kept out of production.

## On AWS

CloudWatch RUM collects Web Vitals, JavaScript errors and sessions and links to X-Ray traces; CloudWatch Synthetics runs scripted canaries. For load tests, k6 on EKS with the k6 operator, Grafana Cloud k6, or the Distributed Load Testing on AWS solution; send their telemetry to a separate AMP workspace. For profiling, run Pyroscope on EKS with the eBPF DaemonSet or language SDKs. POC 30 turns SLOs into k6 thresholds, scores Web Vitals at p75 and computes a top table and flame-graph widths.

## Takeaways

- RUM measures the user’s experience; Web Vitals are judged at p75.
- Profiles explain cost and slowness: self time versus total time.
- Six load test shapes; thresholds from SLOs; keep test telemetry separate.
