# POC 24: SLO recording rules and multiwindow, multi-burn-rate alerts

**Books:** *Mastering Prometheus* chapter 13 (SLIs, SLOs, request- and window-based SLOs, burn-rate alerts, Sloth and Pyrra); *Observability with Grafana* chapter 9 (SLIs, SLOs, SLAs and error budgets in incident management). It completes POC 01, which computed budgets for the SRE book; this one produces the Prometheus rules.

`generate.py` reads Sloth-style specs (`slo.yml`) and writes what Sloth or Pyrra would: error-ratio recording rules for seven windows, a 30-day ratio, objective and budget-remaining series, and two alerts per SLO. Then it simulates traffic minute by minute to show why the windows were chosen.

| Window pair | Burn rate | Budget spent before it fires | Severity |
|---|---|---|---|
| 5m and 1h | 14.4× | 2% in one hour | page |
| 30m and 6h | 6× | 5% in six hours | page |
| 2h and 1d | 3× | 10% in a day | ticket |
| 6h and 3d | 1× | 10% in three days | ticket |

What the tests prove:
* 99.9% over 30 days is 43.2 minutes; the factors in the table spend 2%, 5% and 10% of the budget.
* A full outage pages within a couple of minutes, and the fast pair clears within five minutes of recovery because of the short window.
* A steady 4× burn never pages but opens a ticket; three minutes at 10% errors bother nobody.
* When the 14.4× pair fires, about 2% of the budget has gone, as designed.
* The book's window-based example: one 15-minute window at 500 req/s among quiet 20 req/min windows takes almost 16 days of normal traffic to recover to 50% on a request basis, but only 15 good windows (3.75 hours) to get back to 95% on a window basis.

One correction to the book: a printed alert compares `slo:sli_success:ratio5m` against `14.4 * 0.001`. A *success* ratio is around 0.999, so that alert would always fire. Burn-rate alerts compare *error* ratios, which is what Sloth generates and what this POC emits.

```bash
python generate.py > generated/slo-rules.yml   # regenerate (a test checks the committed copy is current)
python -m pytest -q
promtool check rules generated/slo-rules.yml    # if you have promtool
```

`terraform/amp_rules.tf` loads the generated file into an AMP workspace as a rule groups namespace and routes `sloth_severity="page"` to one SNS topic and tickets to another.

## On AWS
| Need | Service |
|---|---|
| Evaluate the rules | AMP rule groups namespace (this file, unchanged) |
| Route page vs ticket | AMP alert manager definition with two SNS receivers |
| Page a human | SNS → AWS Systems Manager Incident Manager or PagerDuty |
| Ticket | SNS → Lambda → Jira, or an EventBridge rule |
| Show budget remaining | Amazon Managed Grafana panel on `slo:period_error_budget_remaining:ratio` |
| CloudWatch-native alternative | CloudWatch Application Signals SLOs with burn-rate alarms, for services instrumented with Application Signals |

## Interview talking points
* Alert on how fast the budget burns, not on whether the SLO is currently met: by the time it isn't, it's too late.
* Two windows per condition: the long one makes it significant, the short one makes it stop paging soon after recovery.
* Request-based SLOs suit steady traffic and revenue-bearing requests; window-based SLOs suit low traffic and "how long were we down" questions.
* Generate the rules (Sloth, Pyrra or your own generator) so every team gets the same, reviewed alerting.
* Pyrra assumes a 28-day window, so its burn windows look odd (32m, 1h4m, 6h26m…); explain that before rolling it out.
