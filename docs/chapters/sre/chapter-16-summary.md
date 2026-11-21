# SRE chapter 16: Data management

*Site Reliability Engineering, 2nd Edition. Course lesson: `#ch-16`. Code: POC 08. Read: full text, two passes.*

## Summary

Users rarely forgive data failures. Start with the law and ethics: children's data, retention and deletion (soft and hard deletes, TTLs; Bigtable has a "fast" deletion SLO and a guaranteed "eventual" one), residency, purpose restrictions and cross-division sharing limits.

- **1 · Integrity**: What you read is what you wrote
- **2 · Security**: You, and only you
- **3 · Availability**: There when you need it
- **4 · Efficiency**: At a cost you can sustain

Classify data as original or derived (derived data that's expensive to rebuild counts as original), identifiable or not, and flag high-value personal data, which you should avoid collecting if you can. The **hierarchy of data needs**: integrity, then security, then availability, then efficiency.

Integrity comes from redundancy, checksums at every layer including RPCs (the case where a bad network cable corrupted replicas), append-only logs and MVCC, and application-level reconciliation.

Map failure scenarios to defences. Operator error or malice: backups, and no single person with unilateral access. Bad application writes: PITR or snapshots, transaction logs, reconciliation. **Replication does not help** with either, because the corruption or the delete replicates too.

## Key ideas

- the legal and ethical constraints that come before any design
- the hierarchy of data needs
- RPO, RTO and RWO, and what each mechanism does and doesn’t protect
- how to plan, test and govern backups and recovery

## What the lesson covers

- The big picture
- RPO, RTO and RWO on one timeline
- Why data failures are different
- Legal and ethical first
- Classification
- Hierarchy of data needs
- Failure scenarios and defences
- RPO, RTO, RWO
- Replication
- Backups
- Restore testing, plans and recovery policy

## Claims and numbers

- Silent corruption found after 40 days with 30 days of backups is unrecoverable.
- On 9/11, Aon's planning had it operating again within hours with no data lost.
- The chapter's authors run Bigtable: 10 exabytes and 7 billion queries per second.
- GDPR fines reach €20M or 4% of global revenue.
- Efficiency : cross-region "RAID" (half the data in A, half in B, parity in C) has 50% overhead instead of 100%, cutting cost by 25%.
- Storage-system bugs : RocksDB research found roughly one corruption per 3 months per 100 PB, with 40% already copied to replicas.
- RWO example: daily backups kept for two days can't recover corruption from three days ago, and with 14 days you can still lose up to 24 hours if the corruption landed at 23:50.
- Build a catalogue with labels and group it into buckets, then give each bucket objectives (24 h RPO with 12 h RTO works manually; 5 min RPO with 3 min RTO must be software-driven).
- On AWS AWS Backup plans selected by tag, Vault Lock in compliance mode, cross-Region and cross-account copies, restore testing, DynamoDB PITR and deletion protection, S3 versioning and Object Lock, Aurora backtrack.

## Terms

hierarchy of data needs, Replication does not help, Test restores, Integrity outranks recovery, Minors, Retention and deletion, Bigtable, fast, eventual, Residency, Purpose limits, Ethics, Integrity, The GFS case, Reconciliation versus repair, Security

## On AWS

AWS Backup plans selected by tag, Vault Lock in compliance mode, cross-Region and cross-account copies, restore testing, DynamoDB PITR and deletion protection, S3 versioning and Object Lock, Aurora backtrack. See POC 08.

## Takeaways

- Law and ethics first, then integrity, security, availability, efficiency.
- Replication is not a backup. Set RPO, RTO and RWO first and let them drive the design.
- A backup you haven’t restored is a hope. Test restores automatically and validate the data.
