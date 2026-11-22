# POC 31 · Checkout journey SLO lab: build it, break it, watch the SLO react

A hands-on lab for setting **one SLO for a journey that crosses several services**. A tiny online
shop runs on your laptop: a load balancer (`edge`), a `checkout` service and five dependencies, with
steady customer traffic. Prometheus records the journey SLI at the edge and runs multiwindow
burn-rate alerts. You inject failures, retries, outages, slow calls and design changes, and watch
what the SLI, the dependency numbers and the alerts do.

> Books: *Site Reliability Engineering, 2nd ed.* (O’Reilly, 2026) chapter 8 (SLOs, critical user
> journeys, burn-rate alerting), chapter 9 (the bad-minute rule) and Appendix E (composing SLOs);
> *The Site Reliability Workbook*, “Alerting on SLOs”; *Mastering Prometheus* (Packt, 2024) chapter 13.
> Lesson: *SLOs across multiple services: checkout lesson* (Claude artifact).

```
customers ──► edge :8080 ──► checkout :8081 ──► cart :8082          (hard)
 (loadgen)     │  journey SLI      │            ├► inventory :8083     (hard)
               │  measured here    │            ├► recommendations :8086 (soft: page shown without it)
               ▼                   │            ├► payment :8084       (hard; card …0002 is declined)
          Prometheus :9090 ◄───────┘            └► orders :8085        (hard)
          rules/checkout-slo.yml
```

## Quick start

```bash
pip install prometheus_client      # the shop's only dependency
make prometheus                    # one time: prometheus + promtool into ./bin
make up                            # shop + ~10 orders/s + Prometheus, all local, no Docker
python lab.py status               # after ~3 minutes
```

With Docker instead (adds Grafana with a ready-made dashboard on http://localhost:3000):

```bash
make compose-up
python lab.py status
```

Then work through **[EXERCISES.md](EXERCISES.md)**. `make down` / `make compose-down` when finished.

## What you can change while it runs

| Command | Effect |
|---|---|
| `python lab.py chaos payment --error-rate 0.02 --mode random` | 2% of payment calls fail, independently |
| `python lab.py chaos payment --error-rate 0.1 --mode outage --period-s 300` | payment is down 30 s in every 5 minutes |
| `python lab.py chaos payment --latency-ms 2300` | every payment call takes 2.3 s longer |
| `python lab.py chaos cart --slow-rate 0.02 --slow-ms 1500` | 2% of cart calls take 1.5 s longer (a long tail) |
| `python lab.py chaos payment --reset` | back to healthy |
| `python lab.py config --retries payment=1` | checkout retries a failed payment call once |
| `python lab.py config --recommendations hard` | checkout fails the order if recommendations fail |
| `python lab.py stop checkout` / `start checkout` | kill and restart one service (Docker: `docker compose stop checkout`) |
| `python lab.py promql '<expr>'` | run any PromQL query |

## The SLO, as code

`rules/checkout-slo.yml`: **99.9% of valid checkout attempts are confirmed (2xx) in under 2 seconds,
measured at the edge over 30 days.**

* **Valid** = every attempt except malformed requests (400). Your own 5xx and timeouts stay in.
* **Good** = 2xx answered within the 2-second histogram bucket. A declined card answers 200 quickly, so it is good.
* **Recording rules** for 5m, 30m, 1h, 6h, 3d and 30d windows; budget remaining; checkout's own view; each dependency as checkout sees it.
* **Alerts:**
  * `CheckoutBudgetBurnFast` pages when the 1h and 5m burn rates are both above 14.4×, which uses 2% of the budget in an hour.
  * `CheckoutBudgetBurnSlow` pages at 6× over 6h and 30m.
  * `CheckoutBudgetBurnTicket` opens a ticket at 1× over 3d and 6h, which uses 10% of the budget in three days.

`rules/checkout-slo.test.yml` has promtool unit tests, one per behaviour the exercises show:
* healthy traffic is quiet;
* an outage pages, then stops about 5 minutes after the fix;
* a 2-minute blip pages nobody;
* slow successes burn budget;
* 400s aren't valid events;
* a missing 2-second bucket makes the SLI empty.

**A finding from building this lab.** Prometheus 3 stores classic-histogram bucket labels in float
form, `le="2.0"`, even when a client sends `le="2"`. So an exact `le="2"` matcher returns nothing, and
no burn-rate alert built on it can ever fire. The rules match `le=~"2(\\.0)?"`. Exercise 9 shows the trap.

## On AWS

| Lab piece | On AWS |
|---|---|
| `edge` (where the journey SLI is measured) | ingress controller or API gateway on EKS, scraped by ADOT or the AMP managed collector. An ALB's CloudWatch metrics lack per-route detail |
| Prometheus rules | Amazon Managed Service for Prometheus rule group namespaces (`terraform/amp.tf` loads the same files) |
| page / ticket routing | AMP alert manager → SNS → AWS Systems Manager Incident Manager or a ticket queue |
| Grafana dashboard | Amazon Managed Grafana with the AMP data source (same JSON) |
| client-side SLI | CloudWatch RUM, plus CloudWatch Synthetics canaries that place a test order |

## Tests

```bash
make test            # 11 tests: the shop's behaviour for each exercise, plus promtool on the rules
make rules-test      # promtool only
```

## Runbook

**CheckoutBudgetBurnFast / CheckoutBudgetBurnSlow (page):** customers can't place orders at the
expected rate. Run `python lab.py status`. Then, in order:
1. Check `up` for every job, and the edge's status codes:
   * a 502 means no checkout process answered;
   * a 503 means a hard dependency failed;
   * a 504 means checkout was too slow.
2. Check the dependency table to find the dependency below its internal SLO.
3. Mitigate first: roll back, fail over, or make the failing dependency soft. Then diagnose.

**CheckoutBudgetBurnTicket:** a slow leak. Find the dependency or route that has been spending
the budget over the last three days, and plan the fix this week.

## Interview talking points

* "I set one SLO per critical user journey and measure it where every attempt passes, the edge, not by averaging each service's success rate. A crashed service can't count the requests it dropped."
* "Hard dependencies multiply, so I check the design's ceiling before agreeing a target, and give each dependency an internal SLO about one nine tighter. A dependency missing its internal SLO is a ticket for its team, not a page for mine."
* "Retries rescue scattered failures, not outages, and they hide failures from the journey, not from the dependency's own SLI."
* "I alert on burn rate with paired windows (1 hour and 5 minutes at 14.4×) and test the rules with promtool, including a check that the SLI actually returns data."
