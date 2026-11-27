# POC 32: an SLO for an ETL pipeline (hands-on lab)

**Interview question this prepares:** *"How would you set an SLO for a batch pipeline? What is its critical user journey?"*

**The 30-second answer.** The user of a pipeline is whoever reads the data. The journey is "when I need
the data, it is there, complete and correct", so the SLIs are freshness, completeness and correctness,
measured at the output table and judged at the consumer's deadline. The job's exit status is not an SLI.
With one run a day there is no traffic for burn-rate alerts, so I alert on "the deadline is at risk" and
"the data doesn't match the source", early enough to rerun.

## What is in the box

| File | What it is |
|---|---|
| `etl.py` | A nightly revenue pipeline (orders database to warehouse, pence to pounds) and the three read-only checks |
| `lab.py` | Runs it a day at a time with faults you choose, and prints what finance would have seen |
| `rules/etl-slo.yml` | Prometheus alerts for a batch pipeline, with `promtool` tests beside them |
| `tests/` | 11 tests: every fault below, the CLI, and the alert rules |

The source database belongs to another team. Nothing in the checks writes to it: freshness compares the
newest timestamp on each side, completeness and correctness reconcile counts and totals per day, and a
few real orders are traced end to end.

## Run it (no dependencies beyond Python 3)

```bash
python lab.py reset
python lab.py day                 # a normal day
python lab.py month
python -m pytest -q
```

## Exercises: predict, then run

Write your prediction down before each command. That is the part that sticks.

**1. A good day.** `python lab.py day`. Which three lines must say `ok` for finance to have a good day?

**2. The job crashes, and you rerun it in time.**
```bash
python lab.py day --fail
python lab.py rerun --at 03:30
```
Is day 2 good or bad for the SLO? *It is good: the deadline is 07:00 and the rerun finished at 03:30.
Retries are your friend in batch, as long as the load is idempotent (it replaces the partition).*

**3. Exit status 0, data wrong.** `python lab.py day --drop 0.02`. The job says `ok`. Which check fails,
and which check does **not** notice? *Completeness fails (393 of 400 rows). The five traced orders all
look fine, because a sample of five rarely contains one of the eight lost rows. Sampling finds wrong
values; only reconciliation finds missing rows.*

**4. A transform bug.** `python lab.py day --corrupt`. Row counts match. What catches it? *Totals differ
by millions and every traced order is 100 times too big: the transform forgot to divide pence by 100.*

**5. A non-idempotent load.** `python lab.py day --duplicate`. What is the row ratio? *2.0. This is why
"at least 99.9% of rows" is the wrong completeness rule: it must fail in both directions.*

**6. The shop is closed.**
```bash
python lab.py day --quiet
python lab.py lag
```
No orders arrived. Is the pipeline stale? *No. The high-water gap is zero because source and warehouse
stopped together. "Now minus the newest row" says more than a day, and would have paged you for nothing.*

**7. Late is bad, even when right.** `python lab.py day --late 09:15`. *Complete and correct, but
finance read the dashboard at 08:00. Freshness fails.*

**8. Read the month.** `python lab.py month`. The SLO is 29 good days in 30. How many bad days does that
allow, and why would 99.9% be a meaningless target here? *One. With 30 events a month, 99.9% allows
0.03 failures.*

**9. The alerts.** Read `rules/etl-slo.yml`, then run the tests (needs `promtool`; POC 31's
`make prometheus` downloads it):
```bash
cd rules && promtool test rules etl-slo.test.yml
```
Why is there no burn-rate alert? Why does `ETLDeadlineAtRisk` fire at 05:00 and not at 07:00? What does
`ETLCheckerSilent` protect you from?

**10. Stretch.** Add a fourth SLI, a schema check (a column disappears at source), and make a day with a
missing column a bad day.

## Follow-ups an interviewer will ask

* **"You can't insert test rows into the source. How do you probe?"** Read it: compare high-water marks,
  reconcile per partition, trace real records. Or ask the source team for a heartbeat table.
* **"Why not alert when the job fails?"** I do, as a ticket. But a job can exit 0 with half the rows
  (exercise 3), and a failed job that is rerun in time harmed nobody (exercise 2).
* **"What about streaming?"** Freshness becomes lag (event time behind the newest event), traffic is
  steady, and burn-rate alerts work again.

## On AWS

Glue or EMR job, Step Functions or MWAA as the scheduler, S3 and Redshift as the warehouse. Publish the
checker's numbers as CloudWatch custom metrics or to Amazon Managed Service for Prometheus; for CDC
pipelines use DMS's `CDCLatencySource` and `CDCLatencyTarget`. Glue Data Quality or Deequ runs the
reconciliation rules; an EventBridge schedule runs the checker.
