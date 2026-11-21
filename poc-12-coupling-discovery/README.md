# POC 12: Discovering coupling nobody chose

**Book:** *Platform Engineering at Google* (early release), chapter "Coupling" (chapter 9 of the final book)

Coupling is a design decision. It buys efficiency, performance, atomicity and traceability, and it costs reuse, extensibility, robustness and freedom of choice. The trouble is the coupling nobody decided on. This POC takes the evidence produced by the chapter's four discovery methods and reports the antipatterns the chapter names.

| Finding | Evidence used | Where it comes from on AWS |
|---|---|---|
| Shared database (several services on one table; worst when there are several writers) | table access log | CloudTrail data events for DynamoDB, RDS/Aurora audit logs |
| Implicit queue coupling (producer and consumer tied by an unregistered message format) | publish/consume spans, schema registry | X-Ray with trace context on messages, EventBridge or Glue Schema Registry |
| Distributed monolith (services that nearly always ship together) | deploy history | CodePipeline / CodeDeploy events on EventBridge |
| Megamorphic artifact (a config file many services read, none needing most of it) | config key readers | AppConfig or Parameter Store access via CloudTrail |
| Call cycles | RPC spans | X-Ray / Application Signals service map |
| Hidden physical dependency (a fault in one domain hurts services outside it) | chaos experiment result | Fault Injection Service AZ experiment (see POC 06) |

```bash
python coupling_discovery.py examples/evidence.json
python -m pytest -q
```

`independent_release_rate` is the number to watch: the share of releases that shipped one service by itself. A distributed monolith shows up as a low value long before anyone names it.

`fail_open()` is the chapter's runtime-decoupling pattern in three lines. Use it for optional enrichments only. A security or correctness check must fail closed.

## Interview talking points
* Explicit coupling is a direct call. Implicit coupling has no call at all: a queue's consumer depends on the producer's message format.
* Loose patterns: layers, pipe and filter, publish-subscribe, federation, fail open. Antipatterns: shared database, distributed monolith, megamorphic artifacts, control coupling (behaviour flags).
* Kinds of coupling by architectural view: logical, development, process, physical, and scenario. Logical is the most restrictive. Physical is deceptive.
* A workflow engine decouples steps only if they are idempotent and side-effect free. Otherwise expect stuck flows, orphaned state and version skew.
* Chaos engineering is the most expensive discovery method and the only reliable one for physical and scenario coupling.
