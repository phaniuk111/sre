# Prometheus chapter 9: Remote write and remote read: VictoriaMetrics and Mimir

*Mastering Prometheus (William Hegedus, Packt, 2024). Course lesson: `#m-9`. Code: POC 25 · 6. Read: full text, one pass; all figures seen.*

## Summary

Prometheus keeps its storage local and unreplicated on purpose. To go further it offers two HTTP APIs using protocol buffers and Snappy compression. **Remote read** lets Prometheus query another store alongside its own; few people use it, partly because a broken remote store can break alert queries. Thanos uses it the other way round, to read *from* Prometheus. **Remote write** streams every sample to another system and is how you feed AMP, Mimir, Cortex or VictoriaMetrics. With `--web.enable-remote-write-receiver`, Prometheus can also accept writes, which is how Loki’s ruler sends metrics it derives from logs.

`--enable-feature=agent` (2.32) turns Prometheus into a scraper only: no queries, no rules, no local blocks. The WAL is kept just long enough to send, up to about two hours. You keep pull’s advantages, such as the `up` series, and gain push’s: stateless edge collectors and one central store. The book still called it experimental; it is how many teams run collection today.

Remote write sends **everything** unless you say otherwise, the opposite of federation. Start by sending less with `write_relabel_configs`, which run after ingestion and see all labels, for example only one team’s series or only production. Don’t micro-optimise; the config becomes unreadable.

Then size the queue. Each destination gets an in-memory queue divided into shards that send in parallel. If a shard fills, Prometheus stops reading the WAL; nothing is lost unless the backlog outlives WAL truncation, which happens every two hours.

## Key ideas

- Remote read and remote write, and why write won
- Agent mode: scraping with no local queries
- Tuning remote write: relabeling, queues, shards, capacity, backoff
- VictoriaMetrics against Mimir: storage, efficiency, compatibility, HA dedup

## What the lesson covers

- Two APIs
- Agent mode
- Tuning remote write
- VictoriaMetrics or Mimir

## Terms

Remote read, Remote write, everything, A detail interviewers like, Across the books, Thanos, Mimir, VictoriaMetrics

## Interview line

Remote write streams every sample to a central store; I filter with write_relabel_configs, size min_shards from the ingestion rate divided by capacity, and keep capacity at three times the batch size. For collection I like Prometheus in agent mode: pull semantics at the edge, no local state. Between backends, VictoriaMetrics wins on efficiency with local disks, Mimir on object storage, multi-tenancy and strict PromQL, and on AWS AMP gives me the Mimir-style model as a managed service.

## On AWS

Amazon Managed Service for Prometheus is the AWS answer to this chapter: a Cortex-based remote-write target on object storage with SigV4 auth, multi-AZ durability and HA-pair dedup on `cluster` and `__replica__`. Point any Prometheus, agent, ADOT collector or the AMP managed collector at its remote-write URL with an IRSA role that has `aps:RemoteWrite`. POC 25 has Terraform for the workspace and role, and kube-prometheus-stack values with tuned queues.

## Takeaways

- Remote write won; agent mode makes collectors stateless.
- Filter first, then size shards from samples per second ÷ capacity.
- VictoriaMetrics for thrift on local disks, Mimir for object storage and tenants, AMP when you want it managed.
