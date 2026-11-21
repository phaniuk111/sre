# Prometheus chapter 6: When one Prometheus isn’t enough: sharding, federation and high availability

*Mastering Prometheus (William Hegedus, Packt, 2024). Course lesson: `#m-6`. Code: POC 22, 25 · 5. Read: full text, one pass; all figures seen.*

## Summary

A single Prometheus eventually shows the same symptoms: memory creeps up, queries slow down, restarts take longer because of WAL replay. The book names two root causes. **Cardinality**: too many series, and the query engine is single-threaded, so more hardware only helps so far. **Long-term storage**: blocks max out at 31 days, so years of data means dozens of large independent databases on one disk.

The book’s rule of thumb: most labels should have fewer than ten values, and almost none more than a hundred.

Prometheus servers don’t coordinate, so sharding means splitting **scrape jobs**, not data. There are two ways.

With the Operator this is one field, `shards: 2` on the Prometheus resource, which adds those two rules to every job. Run by hand, you must add them to every job yourself.

## Key ideas

- The two limits that end single-server setups: cardinality and long-term storage
- Sharding by service versus sharding with hashmod
- What federation is for, and why it is usually the wrong answer
- HA replicas, external labels, alert deduplication, and how to query a pair

## What the lesson covers

- The big picture
- Sharding
- Federation
- High availability

## Claims and numbers

- Long-term storage : blocks max out at 31 days, so years of data means dozens of large independent databases on one disk.

## Terms

Cardinality, Long-term storage, scrape jobs, The book’s verdict

## Interview line

One Prometheus runs out of road on cardinality and on long-term storage. I shard scrape jobs by service when ownership is clear, or with hashmod relabeling when I need balance, and I run every shard as two identical replicas in different zones that differ only in a replica external label. Alertmanager drops that label to deduplicate alerts, and Thanos Query or remote storage gives users one deduplicated view. Federation I keep for small aggregated subsets.

## On AWS

Most AWS teams skip hand-built sharding and HA queries by remote-writing every replica to Amazon Managed Service for Prometheus: AMP deduplicates HA pairs that share a `cluster` label and differ in `__replica__`, scales storage and queries itself, and gives Grafana a single endpoint. Keep replicas in different AZs, or use the AMP managed collector, which runs scraping for you. POC 25 has the kube-prometheus-stack values and Terraform.

## Takeaways

- Cardinality and long-term storage are what break a single server.
- Shard by service for predictability or hashmod for balance; federate only aggregates.
- HA is identical replicas plus a replica label, deduplicated by Alertmanager and by Thanos or remote storage.
