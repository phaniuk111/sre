# POC 23: Alertmanager routing, alert rules that don't flap, and CI for both

**Books:** *Mastering Prometheus* chapters 5 (routing, grouping, inhibition, time intervals, HA, robust alerts, unit tests) and 12 (promtool, amtool and Pint in CI); *Observability with Grafana* chapter 9 (notification policies, contact points, silences)

`alerting.py` models Alertmanager's routing tree, its grouping timers, inhibition and time intervals, Prometheus' `for` state machine, and a rule linter in the spirit of Pint. The `config/` files are real: an Alertmanager config with AWS SNS receivers, a rules file and a `promtool` unit test. `ci/` holds the GitHub Actions workflow and the Pint config.

| Piece | Idea |
|---|---|
| `Route.match()` | depth-first; the most specific matching route wins; `continue: true` also tries the siblings; a parent is the fallback when no child matches |
| `matches()` | `=`, `!=`, `=~`, `!~`; a missing label counts as empty; double quotes optional, single quotes kept literally |
| `notification_times()` | `group_wait` before the first message, `group_interval` between updates, `repeat_interval` for unchanged groups |
| `inhibited()` | a critical mutes the warning with the same `namespace` and `alertname`; an alert never mutes itself |
| `should_notify()` | `active_time_intervals`: routing still happens out of hours, only the message (including "resolved") is held back |
| `alert_states()`, `last_over_time()` | a single failed scrape resets `pending`; wrapping the selector in `last_over_time(...[5m])` stops that |
| `lint_rules()` | severity label, one-sentence summary without templates, templated description, runbook link, a comparison, sane `for` durations |

## Two places the book and Alertmanager disagree
The tests pin these down, because both are good interview material.

* **Grouping timeline.** Alerts at 10:00:00, 10:00:17 and 10:00:35 with default timers: the first two go at 10:00:30. The book says the third goes at 10:05:00. In Alertmanager the group timer restarts when it flushes, so the next flush is `group_interval` after 10:00:30, at **10:05:30**.
* **Routing with `continue`.** In the book's second routing table, `{environment="production", team="sre"}` is listed as going to `fallthrough`. With the config as printed, every matcher on the `default` route holds for that alert (a missing `namespace` is not `default`, `team` matches `devops|sre`, a missing `service` doesn't match `^(api.+)`), so it goes to **`default`**. `amtool config routes test` would show the same.

A third subtlety: the book's unit test expects `SSHDown` to fire at 14 minutes. That holds in Prometheus 2.x, where range selectors include the left edge. Prometheus 3 made ranges left-open, so the same rule fires a minute earlier. The test file here checks at 15 minutes, which is true in both.

```bash
python -m pytest -q
# with the real tools:
promtool check rules config/rules.yml && promtool test rules config/unit-test.yml
amtool check-config config/alertmanager.yml
amtool config routes test --config.file=config/alertmanager.yml team=devops environment=production
```

## On AWS
| Need | Service |
|---|---|
| Managed rule evaluation | AMP rule groups namespaces (`aws_prometheus_rule_group_namespace`) take this `rules.yml` unchanged |
| Managed Alertmanager | the AMP alert manager definition (`aws_prometheus_alert_manager_definition`); its receivers are SNS topics, so fan out from SNS to email, chat (Amazon Q Developer in chat applications), PagerDuty or Lambda |
| Paging and on-call | AWS Systems Manager Incident Manager subscribed to SNS, or PagerDuty/Grafana OnCall |
| CI | the GitHub Actions workflow here, or CodeBuild running the same `promtool` and `amtool` commands in the official images |
| HA without AMP | two or three Alertmanagers in different AZs, peered with `--cluster.peer`, every Prometheus sending to all of them, no load balancer in between |

## Interview talking points
* Prometheus decides *that* an alert fires; Alertmanager decides *who* hears about it, *how often*, and *what to suppress*.
* Grouping, inhibition and silences are the three noise tools; `repeat_interval` of a day beats the 4-hour default for most teams.
* Alertmanager HA gossips silences and the notification log, not alerts, so every Prometheus must send to every Alertmanager.
* Robust alerts combine signals with `and`/`unless`, use `for` durations long enough to ignore blips, and use `_over_time` so a failed scrape doesn't reset them.
* Validate config, unit-test rules, test routes and lint against a live server in CI, so people who aren't Prometheus experts can change alerts safely.
