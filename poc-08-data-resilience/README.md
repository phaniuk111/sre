# POC 08: Data management & data resilience on AWS

**Book chapters:** 16 (Data Management), 17 (Data Resilience)

| Path | What |
|---|---|
| `terraform/` | Tag-driven **data tiers** → AWS Backup plans (hourly + PITR for tier 0, daily, weekly), **cross-Region copy**, **Vault Lock** (compliance mode), **restore testing plan**, DynamoDB PITR + deletion protection, S3 versioning + Object Lock + noncurrent-version expiry |
| `backup_slo.py` | Fleet SLO report: "backups for 99% of data sources are within RPO 99% of the time", plus RWO gaps and **untested restores** (no restore test = no RTO). Works offline on sample data or `--live` with boto3 |

```bash
python -m pytest -q
python backup_slo.py            # sample data
python backup_slo.py --live     # your account (needs backup:List*, tag:GetResources)
```

## Failure scenarios → defences (ch. 16)
| Scenario | Replication helps? | AWS defence |
|---|---|---|
| Operator error / malicious delete | ❌ (the delete replicates) | AWS Backup + **Vault Lock**, separate backup account, SCPs, deletion protection, least-privilege/no unilateral human access |
| App writes bad data | ❌ (corruption replicates) | **PITR** (DynamoDB/RDS/Aurora), S3 versioning, reconciliation jobs, app-level validation |
| Storage-system bug | partly | Backups into a *different* system/format, e.g. DynamoDB export to S3 |
| Hardware failure | ✅ | Multi-AZ (built into DynamoDB/S3/Aurora), RDS Multi-AZ |
| Region loss | ✅ if cross-Region | Cross-Region backup copy, DynamoDB global tables, S3 CRR, Aurora Global Database |

## Objectives
* **RPO**: how much data you can lose, which sets backup frequency (or PITR).
* **RTO** (the book calls it *Restore* Time Objective): how fast you must be back. It is cumulative: time to detect + time to act + time to restore, counted from the incident. Snapshots restore faster but share fate with the source; measure the real number with restore tests.
* **RWO** (Restore Window Objective): how far back you can restore. It has to satisfy the business *and* data-deletion law (GDPR erasure), which caps retention.

## Rules of thumb from the chapter
* **3-2-1**: three copies, two media types, one off-site copy (here: another Region in a locked vault).
* Anything that can write to live data should have **zero** admin rights over its backups.
* Prefer *simple* backups (logical exports) over clever ones when restore reliability matters most.
* Annotate data sources with their tier and objectives so new sources get covered automatically.
* Write a **data recovery policy** in advance: repair vs restore, partial restores, who decides what data is lost, whether security can be relaxed to restore.
