# Prometheus chapter 5: Alertmanager, and alerts that don’t wake people for nothing

*Mastering Prometheus (William Hegedus, Packt, 2024). Course lesson: `#m-5`. Code: POC 23 · 7. Read: full text, one pass; all figures seen.*

## Summary

A common misunderstanding is that Prometheus sends notifications. It doesn’t. Prometheus evaluates alerting rules, and when an expression has been true for the rule’s `for` duration it sends the alert to **every** Alertmanager it knows, re-sending while it fires. Alertmanager owns everything after that: routing, grouping, inhibition, silencing and delivery.

The only mandatory parts of an Alertmanager config are a top-level **route** and a **receiver**. The top route matches every alert and can’t have matchers; everything else is a tree of sub-routes underneath it. Matchers look like PromQL: `=`, `!=`, `=~`, `!~`. Quoting the value with double quotes is optional; single quotes become part of the value, a gotcha the book calls out.

Without `continue`, the first matching child wins and evaluation stops. With it, the alert also tries the following siblings, which is how you send the same alert to Slack and to PagerDuty.

The book’s table puts the third notification at 10:05:00, five minutes after the first alert. In Alertmanager the group timer restarts when it fires, so the update goes out at 10:05:30. The difference is small, but explaining it shows you understand the mechanism.

## Key ideas

- Routing trees, matchers, continue, and how to test routes
- group_by, group_wait, group_interval and repeat_interval, on a timeline
- Time intervals, receivers, send_resolved and inhibition
- Alertmanager high availability: what it gossips and what it doesn’t
- Robust rules: set operators, for durations, _over_time, unit tests

## What the lesson covers

- The big picture
- Routing
- Grouping, on a timeline
- Time intervals, receivers and inhibition
- High availability
- Robust rules
- Unit tests

## Claims and numbers

- The book’s table puts the third notification at 10:05:00, five minutes after the first alert.
- Time intervals, receivers and inhibition. active_time_intervals and mute_time_intervals (added in 2022) reference named intervals built from weekdays, days of month (negative numbers count from the end), months, years, times and an IANA time zone.
- That catches people out: an incident fixed at 17:05 never gets its “resolved” message if warnings only notify in business hours.
- The standard rule mutes warnings and infos when a critical with the same namespace and alertname fires, which lets you keep a 90% disk warning and a 98% disk critical without double pages.
- The author’s rule of thumb: warnings wait at least 15 minutes, criticals fire within 15.
- The book expects the alert at 14 minutes.
- That is true in Prometheus 2.x; Prometheus 3 made range selectors left-open, so max_over_time(.[5m]) turns true a minute earlier.
- Testing at 15 minutes passes on both, which is the kind of robustness a test suite should have.

## Terms

every, route, receiver, Inhibition, silences, notification log, Combine signals, Choose for durations deliberately, Wrap selectors in _over_time, Alert on symptoms, Across the books, Alertmanager routing

## Interview line

Prometheus decides that an alert is firing; Alertmanager routes it through a tree where the most specific match wins unless continue is set, groups alerts by labels with group_wait, group_interval and repeat_interval, mutes warnings while a related critical fires, and holds notifications outside active time intervals. In HA, Alertmanagers gossip silences and the notification log, so every Prometheus must send to every Alertmanager directly.

## On AWS

AMP’s managed Alertmanager accepts a standard Alertmanager config, but its receivers are SNS topics: fan out from SNS to email, chat through Amazon Q Developer in chat applications, PagerDuty, Lambda or AWS Systems Manager Incident Manager. Load rules into an AMP rule groups namespace unchanged. In Amazon Managed Grafana, Grafana alerting’s notification policies follow the same routing model. POC 23 has an Alertmanager config with SNS receivers and a CI workflow.

## Takeaways

- Most specific route wins; continue tries the siblings; missing labels are empty strings.
- group_wait, group_interval, repeat_interval shape the noise; inhibition and time intervals cut it further.
- Robust rules combine signals, use sensible for durations and _over_time, and are unit-tested.
