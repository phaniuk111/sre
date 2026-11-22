# Checkout journey SLO lab: exercises

Each exercise follows the same rhythm: **predict** (write your answer down first), **do**,
**watch**, then check **what you should see** and **why**. The last line of each is the sentence
to use in an interview.

You need about 90 minutes for the whole set. Exercises 2–7 each change one thing; reset it before
the next one (`python lab.py chaos <service> --reset`, `python lab.py config --retries --recommendations soft`).

Everything uses real time and real 5-minute and 1-hour windows, so after you break something,
**wait**: an alert needs its condition to hold for 2 minutes, and it clears about 5 minutes after the fix.

| | Exercise | Lesson section |
|---|---|---|
| 0 | Start the lab and take a baseline | |
| 1 | Compute the journey SLI by hand from the counters | §1 |
| 2 | Kill checkout: who notices? | §1 |
| 3 | Payment fails 2% of calls at random | §2, §4 |
| 4 | Add one retry | §3 |
| 5 | The same failure rate as outages | §3 |
| 6 | Recommendations: soft, then hard | §2 |
| 7 | Slow successes, and percentiles that don't add | §1, §2 |
| 8 | Write payment's internal SLO | §2 |
| 9 | The `le` trap | §4 |
| 10 | Roll several SLIs into one with the bad-minute rule | §4 |
| 11 | Stretch: run the rules on Amazon Managed Service for Prometheus | |

---

## 0 · Start the lab and take a baseline

**Do**

```bash
cd poc-31-checkout-journey-slo-lab
pip install prometheus_client
make prometheus          # one time: downloads prometheus + promtool into ./bin
make up                  # shop + load generator (~10 orders/s) + Prometheus on :9090
```

Or, with Docker: `make compose-up`, which adds Grafana on http://localhost:3000 with the
*Checkout journey SLO (lab)* dashboard already loaded. `lab.py` works against either.

Wait three minutes, then:

```bash
python lab.py status
```

**What you should see:** journey SLI 100%, burn rates near 0x, every dependency at 100%, no alerts.
The load generator sends about 2% malformed orders (400) and 3% declined cards (200, "declined").
Neither costs you anything: 400s are left out of valid events, and a decline is a correct answer.

**Interview:** "Before I set a target I look at what the journey actually does today, measured at the edge."

---

## 1 · Compute the journey SLI by hand

**Predict:** the SLI is good ÷ valid. Which status codes go in each?

**Do:** open http://127.0.0.1:9090 and run these one at a time:

```promql
sum by (code) (rate(edge_request_duration_seconds_count{route="POST /checkout"}[5m]))
sum(rate(edge_request_duration_seconds_bucket{route="POST /checkout", code=~"2..", le=~"2(\\.0)?"}[5m]))
journey:checkout_error_ratio:rate5m
```

Now read `rules/checkout-slo.yml` top to bottom. Find where 400 is excluded, where the 2-second
threshold lives, and why there are five windows (5m, 30m, 1h, 6h, 3d).

**What you should see:** your hand calculation (2xx under 2 s ÷ everything except 400) equals
`1 - journey:checkout_error_ratio:rate5m`.

**Interview:** "The SLI is a ratio of two rates at the edge, saved as recording rules for every alert window."

---

## 2 · Kill checkout: who notices?

**Predict:** if every checkout process dies, what does checkout's own success-rate metric say?

**Do**

```bash
python lab.py stop checkout        # docker: docker compose stop checkout
sleep 150; python lab.py status
```

Also run `up{job="checkout"}` in Prometheus.

**What you should see**

* Journey SLI falls sharply; the edge is answering 502 (`sum by (code) (...)` from exercise 1).
* "Checkout's own success rate" still says 100%. It isn't being scraped (`up` is 0), and the
  requests it never received were never counted.
* `CheckoutBudgetBurnFast` goes pending, then FIRING after 2 minutes. `CheckoutBudgetBurnSlow` follows.

Now fix it and time how long the page takes to stop:

```bash
python lab.py start checkout
watch -n 15 python lab.py status   # or re-run status every minute
```

The page stops about 5 minutes after the fix, even though the 1-hour burn rate is still huge.
That is the 5-minute window's job.

**Why:** a service can only count requests that reached it. The load balancer saw every attempt.

**Interview:** "I measure the journey at the edge, because a crashed service can't count the requests it dropped."

---

## 3 · Payment fails 2% of calls at random

**Predict:** the SLO is 99.9%. What burn rate will 2% payment failures cause? Will it page?

**Do**

```bash
python lab.py chaos payment --error-rate 0.02 --mode random
sleep 180; python lab.py status
```

**What you should see:** journey SLI about 98%, burn rate about 20x on the 5-minute window,
`payment` at about 98% in the dependency table, and after the hour window catches up the fast page fires
(2% > 1.44%). The edge shows 503 for those orders: checkout answered, but a hard dependency failed.

**Why:** payment is a hard dependency, so its failures pass straight into the journey.
Burn rate = error ratio ÷ budget ratio = 0.02 ÷ 0.001 = 20.

**Interview:** "Burn rate is the error ratio over the budget ratio; at 20x a 30-day budget lasts a day and a half."

---

## 4 · Add one retry

**Predict:** with one retry, roughly what journey error ratio? What happens to payment's own number?

**Do** (keep the 2% chaos from exercise 3)

```bash
python lab.py config --retries payment=1
sleep 330; python lab.py status
```

**What you should see**

* Journey error ratio about 0.04% (0.02 × 0.02): the SLI is back above 99.9% and the page clears.
* Payment, as checkout sees it, **still** shows about 98%: retries hide the failures from customers,
  not from the dependency's own record.

**Why:** with independent failures both attempts must fail. The dependency table is where payment's
internal SLO lives, and it is still being missed. Exercise 8 turns that into an alert.

**Interview:** "Retries protect the journey SLO; the internal SLO on the dependency still shows the real failure rate."

---

## 5 · The same failure rate as outages

**Predict:** payment is down 10% of the time, in one 30-second block every 5 minutes. Does the retry still help?

**Do**

```bash
python lab.py chaos payment --error-rate 0.1 --mode outage --period-s 300
sleep 330; python lab.py status
```

Watch the Grafana panel *Requests at the edge by status code*, or query
`sum by (code) (rate(edge_request_duration_seconds_count{route="POST /checkout"}[1m]))`.

**What you should see:** a block of 503s every 5 minutes. The retry 50 ms later lands in the same
outage, so the journey loses about 10% of orders even with `retries payment=1`.

**Why:** retries multiply away independent failures only. In an outage the second attempt fails because the first did.

**Interview:** "A retry turns 0.5% scattered failures into 0.0025%, and does nothing for an outage."

Reset: `python lab.py chaos payment --reset && python lab.py config --retries`

---

## 6 · Recommendations: soft, then hard

**Predict:** recommendations fail 5% of calls. Does checkout's SLI care? What if checkout waits for them?

**Do**

```bash
python lab.py chaos recommendations --error-rate 0.05
sleep 120; python lab.py status          # soft (the default): page shown without the panel
python lab.py config --recommendations hard
sleep 330; python lab.py status
```

**What you should see:** while soft, recommendations shows about 95% in the dependency table and
the journey is untouched. Once hard, the journey drops by about 5% and pages.

**Why:** a soft dependency has a fallback, so it leaves the multiplication. Making one dependency
hard put its whole failure rate into the journey. Compare with the calculator in §2 of the lesson.

**Interview:** "The cheapest way to raise a journey's ceiling is often to make a dependency soft."

Reset: `python lab.py chaos recommendations --reset && python lab.py config --recommendations soft`

---

## 7 · Slow successes, and percentiles that don't add

**Predict (a):** payment takes 2.3 s, but every order still succeeds. Is the SLO hurt?

```bash
python lab.py chaos payment --latency-ms 2300
sleep 180; python lab.py status
```

**What you should see:** every order is a 200, yet the journey SLI collapses and the page fires.
Good means *confirmed in under 2 seconds*; a slow success is a bad event. (The promtool test
"slow successes are bad events too" pins this down.)

**Predict (b):** 2% of cart calls and 2% of payment calls are 1.5 s slower than usual, at random.
Each one's p99 is then about 1.5 s. Is the journey's p99 about 3 s?

```bash
python lab.py chaos payment --reset
python lab.py chaos cart --slow-rate 0.02 --slow-ms 1500
python lab.py chaos payment --slow-rate 0.02 --slow-ms 1500
sleep 180; python lab.py status
```

**What you should see:** cart and payment each near 1.5 s at p99, and the journey's p99 nowhere
near 3 s (it shows somewhere between 1.5 and 2 s), because an order almost never hits both slow
calls. About 4% of orders hit one of them, which pushes the journey's p99 above either dependency's,
but far below the sum. (`histogram_quantile` interpolates inside a bucket, here the 1–2 s one, so
read these as estimates.)

**Interview:** "Percentiles don't add. I budget time per step to design against, and measure the journey's latency end to end."

Reset both services with `--reset`.

---

## 8 · Write payment's internal SLO

**Task:** the journey is 99.9%. Using the rule of the extra nine, write recording rules and a
fast-burn alert for payment's internal SLO, measured as the success rate of checkout's calls to
payment. It should open a ticket for the payment team, not page checkout's on-call.

Hints: the metric is `checkout_dependency_attempts_total{dep, outcome}`; the budget ratio is 0.0001.

**Check:** compare with `solutions/internal-slos.yml`. Load it:

```bash
# add ../solutions/internal-slos.yml under rule_files in prometheus/prometheus.local.yml, then
curl -X POST http://127.0.0.1:9090/-/reload
```

Repeat exercise 4 (2% random + one retry). **What you should see:** the journey is healthy and
`CheckoutBudgetBurnFast` stays quiet, but `PaymentInternalSLOBurnFast` fires with `owner=payment-team`.

**Interview:** "Internal SLOs are promises between teams. A dependency can break its promise while the journey is still fine, and that's a ticket for them, not a page for us."

---

## 9 · The `le` trap

**Predict:** the rules match the 2-second bucket with `le=~"2(\\.0)?"`. Why not just `le="2"`?

**Do:** in Prometheus, run

```promql
count by (le) (edge_request_duration_seconds_bucket)
sum(rate(edge_request_duration_seconds_bucket{route="POST /checkout", code=~"2..", le="2"}[5m]))
```

**What you should see:** the bucket is stored as `le="2.0"`, and `le="2"` returns nothing. This shop's
Python client writes `2.0`, and Prometheus 3 rewrites classic-histogram `le` values into that form
on scrape even when a client sends `2`. An exact `le="2"` makes the good-events rule empty, so the error
ratio is empty and **no burn-rate alert can ever fire**.

Then change one recording rule to `le="2"`, reload, and look at `journey:checkout_error_ratio:rate5m`.
Change it back. Run `make rules-test`: the last promtool test shows the same thing.

**Interview:** "I check that every SLI series actually returns data, and match bucket labels in a way that survives label formatting."

---

## 10 · Roll several SLIs into one with the bad-minute rule

When a journey is several requests and no single request covers them all, your SRE book's
observability chapter judges it minute by minute: a minute is bad if **any** step's SLI was bad.

**Task:** write rules that produce a 0/1 "bad minute" from the per-dependency error ratios, ignoring
recommendations, and the share of good minutes in the last hour. Hint: `> bool`, `max`, `avg_over_time`.

**Check:** compare with `solutions/bad-minute.yml`, load it, then inject `python lab.py chaos inventory --error-rate 0.005`.

**What you should see:** the request-based SLI barely moves (0.5% of orders fail), but most minutes
become bad minutes, because at 10 orders a second almost every minute contains a failure. Window-based
SLOs need a per-minute threshold that fits your traffic, and a target expressed in minutes.

**Interview:** "Request-based SLOs weight every request; window-based SLOs weight every minute. For low or bursty traffic I prefer windows."

---

## 11 · Stretch: the same rules on AWS

`terraform/amp.tf` creates an Amazon Managed Service for Prometheus workspace, loads
`rules/checkout-slo.yml` and the internal SLO as rule group namespaces, and routes `severity=page` and
`severity=ticket` to two SNS topics. Apply it in a sandbox account, then add remote write to your local
Prometheus (SigV4 needs AWS credentials in your environment):

```yaml
remote_write:
  - url: <remote_write_url output>
    sigv4:
      region: eu-west-2
```

On EKS you would scrape the ingress controller or gateway with the ADOT collector or AMP's managed
collector instead of `edge`, and send the pages to AWS Systems Manager Incident Manager.

`terraform destroy` when you finish.
