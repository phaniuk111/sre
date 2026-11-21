# Prometheus chapter 3: The data model and the TSDB: how samples are stored and found

*Mastering Prometheus (William Hegedus, Packt, 2024). Course lesson: `#m-3`. Code: POC 21 · 7. Read: full text, one pass; all figures seen.*

## Summary

A **sample** is a float64 value and a millisecond timestamp. A **series** is all the samples that share one metric name and one exact set of label values. A **metric** is the family of series with the same name. Change any label value and you have a new series, with its own memory, index entries and chunks.

Under the hood the metric name is just another label, `__name__`. So `http_requests_total{code="500"}` and `{__name__="http_requests_total", code="500"}` are the same selector.

Incoming samples are appended to an in-memory chunk per series. When a chunk fills (120 samples) it is written to disk and memory-mapped, so memory holds only the active chunk per series. To survive a crash, every sample is also written to the **write-ahead log**: 128 MB segment files that are replayed on startup. Periodically a **checkpoint** condenses old WAL segments so replay doesn’t have to read all of them.

That replay is why a Prometheus with millions of series can take many minutes to start, and why the book lists slow startup as one of the first signs of trouble.

## Key ideas

- Metric, series, sample, and why labels decide cost
- The four metric types and what each is for
- The head block, the write-ahead log, checkpoints and memory-mapped chunks
- Blocks, the index and postings, compaction and retention
- Why delta-of-delta and XOR compression make samples cost about a byte

## What the lesson covers

- The big picture
- Metric types
- Where samples live
- Gorilla compression
- Further reading the book recommends

## Claims and numbers

- The compactor merges three adjacent blocks into one three times as long (2h, 6h, 18h, 54h…), up to 31 days or a tenth of the retention period.
- Head block, WAL and blocks : Two hours in memory with a write-ahead log, then immutable blocks compacted up to 31 days.

## Terms

sample, series, metric, Why histograms usually win, write-ahead log, checkpoint, block, compactor, Retention, symbol table, postings list, difference between consecutive differences, Across the books, Series and cardinality, rate, increase and irate

## Interview line

A series is a metric name plus a unique label set; every new label value is a new series with its own memory, index entries and chunks, which is why cardinality is the cost driver. Samples land in an in-memory head block backed by a write-ahead log, get cut into immutable two-hour blocks, and the compactor merges those up to 31 days. Queries use an inverted index of postings lists, intersecting the lists for each label matcher.

## On AWS

AMP runs a Cortex-based storage engine that keeps the same data model in S3-backed blocks, so cardinality is still what you pay for: AMP bills per sample ingested and per GB stored, and has per-workspace quotas on active series. If you self-manage on EKS, give each Prometheus replica its own gp3 EBS volume in its own AZ, size memory for head-block series, and expect WAL replay after a restart to scale with series count.

## Takeaways

- Every unique label set is a series, and series are what cost memory, disk and query time.
- Head block plus WAL for recent data; immutable two-hour blocks compacted up to 31 days.
- Regular scrapes and steady values compress to about a byte per sample.
