# Prometheus chapter 13: SLOs with Prometheus: recording rules, burn-rate alerts, Sloth and Pyrra

*Mastering Prometheus (William Hegedus, Packt, 2024). Course lesson: `#m-13`. Code: POC 24 · 6. Read: full text, one pass; all figures seen.*

## Summary

An **SLI** is a measurement (good events over valid events), an **SLO** a target for it over a window, and an **SLA** an SLO with a contract and penalties. The error budget is one minus the objective, and the burn rate is how fast you are spending it. The SRE lessons covered the theory (SRE chapter 8); this chapter is the Prometheus implementation.

Two points of emphasis from the author. SLOs work best set bottom-up by the team that runs the service, signed off by leadership, because missing them must be allowed to redirect work to reliability. And they should be realistic, not aspirational: some teams even schedule outages when they over-achieve, so users don’t come to depend on more than was promised.

`clamp_min(…, 1)` stops endpoints with no traffic from producing missing results; the book admits the edge case where a single slow request still scores 100%. The window-based version leans on `bool`, which turns a comparison into 0 or 1, and a subquery.

Use one series name per kind of value and labels to tell SLOs apart, for example `slo:sli_error:ratio_rate5m{service="checkout", slo="availability"}`. The 30-day value is `sum_over_time(…5m[30d]) / count_over_time(…5m[30d])`, deliberately the same formula Sloth and Pyrra use.

## Key ideas

- SLIs, SLOs, SLAs, error budgets, and who should set SLOs
- Request-based and window-based SLOs, with PromQL for both
- Recording rules for SLOs and the 30-day ratio
- Multiwindow, multi-burn-rate alerts
- Sloth and Pyrra, and how their outputs differ

## What the lesson covers

- The big picture
- Two kinds of SLO
- Recording rules first
- Alerting on burn rate
- Generating it all

## Claims and numbers

- Two kinds of SLO. clamp_min(…, 1) stops endpoints with no traffic from producing missing results; the book admits the edge case where a single slow request still scores 100%.
- The 30-day value is sum_over_time(…5m[30d]) / count_over_time(…5m[30d]), deliberately the same formula Sloth and Pyrra use.
- Each bar is a burn-rate threshold, its short and long windows, and how quickly it would exhaust a 30-day budget.Alerting when the SLO is already broken is too late.
- Burn-rate alerts compare the error ratio with burn × (1 − objective), which is what Sloth generates and what POC 24 emits and tests.
- The book counts more than 80% fewer lines with Pyrra than writing the rules by hand.

## Terms

both, error, Across the books, SLI, SLO, SLA, Error budget, Burn rate, Low-traffic alerting, Window-based SLO

## Interview line

I define SLIs as good over valid events in recording rules with consistent names and labels, compute the 30-day ratio from the 5-minute one, and alert on burn rate with paired windows: 14.4× over five minutes and an hour, and 6× over thirty minutes and six hours, page; 3× and 1× open tickets. Window-based SLOs, with bool and a subquery, suit low-traffic services. In practice I generate it all with Sloth or Pyrra so every team gets the same rules.

## On AWS

Load generated SLO rules into an AMP rule groups namespace and route `severity=page` and ticket alerts to different SNS topics through the AMP Alertmanager; show budget remaining in Amazon Managed Grafana. For services instrumented with CloudWatch Application Signals, CloudWatch SLOs offer burn-rate alarms natively. POC 24 generates the rules, simulates outages and slow burns, and has Terraform for the AMP namespace and alert routing.

## Takeaways

- SLI in recording rules, 30-day ratio from the 5-minute one.
- Page on fast burn confirmed by two windows; ticket on slow burn.
- Generate rules with Sloth or Pyrra; compare error ratios, never success ratios.
