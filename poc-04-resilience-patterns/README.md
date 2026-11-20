# POC 04: Designing for resilience: overload, retries, cascades

**Book chapter:** 17 (Designing for Resilience), plus 15 (criticality, crumple zones) and Appendix E (hedging)

```bash
python -m pytest -q
python simulate_cascade.py
```
Sample output:
```
naive     total goodput=  3450 wasted=  7950 min goodput after spike=  0 recovered_by_tick=never
protected total goodput= 10220 wasted=     0 min goodput after spike= 80 recovered_by_tick=60
```
The naive system never recovers after a 20-tick spike to 150% load. Its queue is full of requests whose clients have already timed out, so every unit of capacity goes on wasted work, and immediate retries keep the queue full. This is a **metastable failure**: removing the trigger doesn't end the outage. The protected system sheds early, its clients back off, and goodput recovers as soon as the spike ends.

## Patterns → AWS
| Pattern (book) | Code | AWS equivalent / where to configure |
|---|---|---|
| Exponential backoff + **jitter** | `backoff.py` | AWS SDK retry modes `standard` / `adaptive` (`AWS_RETRY_MODE`, `max_attempts`) |
| **Retry budget** (per client) | `budgets.py` | Not built in. Wrap SDK clients; also avoid retries at every layer (API GW → Lambda → SDK) |
| **Adaptive throttling** `p=max(0,(req-K·acc)/(req+1))` | `throttling.py` | SDK `adaptive` mode client-side rate limiter |
| **Circuit breaker** + fallback | `circuit_breaker.py` | App Mesh/Envoy outlier detection, VPC Lattice health checks; app-level library |
| **Load shedding by criticality** | `shedding.py` | API Gateway usage plans/throttling, ALB + app shedding, SQS as a buffer, Lambda reserved concurrency |
| **Graceful degradation** | flag in app | AppConfig feature flags (POC 05) |
| **Hedged requests** (idempotent reads) | `hedging.py` | DynamoDB/ElastiCache read replicas; DAX |
| **Drain** a failure domain | n/a | Route 53 ARC **zonal shift** / zonal autoshift, Route 53 failover records |
| **Block** a query of death | n/a | AWS WAF rate-based / custom rules |
| Failure domains | n/a | Multi-AZ by default; cell-based architecture; Regions as the blast-radius boundary; static stability (pre-provisioned N+1 AZ capacity) |

## Design checklist from the chapter
- Detect overload from objective signals (queue length, in-flight count, memory), not just CPU.
- Reject at the door with an explicit **"overloaded, retry after N s / don't retry"** response.
- Clients: back off with jitter, cap retries with a budget, be careful retrying queued work after a restart.
- During an emergency: block the excess sources, add capacity *before* domains collapse, **stop automation that restarts unhealthy-looking servers** (it makes things worse), restart in a controlled way, and plan for a cold start with empty caches.
- Validate input: if an update is implausible (empty, partial, a huge diff), keep serving the last good state and alert.
- Data: delete in stages with grace periods, keep independent fallback backups of critical metadata, deglobalise risky operations.
