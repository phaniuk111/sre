# Prometheus chapter 10: Thanos: a global view and unlimited retention, one component at a time

*Mastering Prometheus (William Hegedus, Packt, 2024). Course lesson: `#m-10`. Code: POC 25 · 6. Read: full text, one pass; all figures seen.*

## Summary

Thanos began at Improbable, written by Bartłomiej Płotka and Fabian Reinartz, and is a CNCF incubating project. Its goals are a global query view, unlimited retention and highly available components. Unlike Mimir or VictoriaMetrics it is not one system but a set of small components, all subcommands of one `thanos` binary, that you add as you need them. The author recommends it as the first step beyond plain Prometheus, and notes almost nobody runs every component.

The Compactor compacts as Prometheus would. **Vertical compaction** also merges overlapping blocks from HA replicas to save storage; it needs three flags precisely because a mistake can destroy history, and the book says not to turn it on after reading one chapter.

**Downsampling** is widely misunderstood. It doesn’t save space: it adds a 5-minute version of raw data older than 40 hours and a 1-hour version of 5-minute data older than 10 days, each storing count, sum, min, max and a counter value. Because the index barely shrinks, expect storage to double or triple. What you gain is fast queries over months. Keep the three per-resolution retentions equal, or old data becomes reachable only at a coarse step.

## Key ideas

- The three goals of Thanos and the StoreAPI that ties it together
- Sidecar, Compactor, Query, Query Frontend, Store, Ruler and Receive
- Vertical compaction and downsampling, and what each really buys
- Scaling the read path: the distributed engine, splitting, sharding, caching, partitioning

## What the lesson covers

- The big picture
- The components
- Compaction and downsampling
- Making Query fast
- Receive in more detail

## Claims and numbers

- It doesn’t save space: it adds a 5-minute version of raw data older than 40 hours and a 1-hour version of 5-minute data older than 10 days, each storing count, sum, min, max and a counter value.
- In the book, a week-long p99 went from about 30 s to 20 s with the frontend, and to 15 s with a second querier.

## Terms

Vertical compaction, Downsampling, Across the books, Thanos, Mimir, VictoriaMetrics

## Interview line

Thanos is a toolbox around Prometheus. Sidecars expose each server over the StoreAPI and upload two-hour blocks to S3; Query fans out across them and deduplicates HA replicas on the replica label; Store serves the bucket; the Compactor compacts and downsamples, which speeds long queries rather than saving space. I add Query Frontend for splitting and caching, Ruler only for global rules, and Receive when clusters must push rather than be queried.

## On AWS

On AWS, Thanos uses S3 for blocks with an IRSA role per component, and S3 lifecycle rules move old blocks to Standard-IA. Query, Store, Compactor and Frontend run on EKS; ElastiCache for Memcached or Redis backs the frontend and store caches. The managed alternative is AMP, which gives the same global view and long retention without operating components, at the cost of central ingestion. POC 25 includes the S3 objstore config, the bucket Terraform and simulations of dedup, downsampling, splitting and hashrings.

## Takeaways

- Every Thanos component speaks the StoreAPI; add them one at a time.
- Sidecar + Query gives a global, deduplicated view; Store + Compactor give retention.
- Downsampling speeds long queries and costs storage; the Thanos engine and Query Frontend scale reads.
