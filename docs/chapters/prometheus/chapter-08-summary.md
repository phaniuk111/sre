# Prometheus chapter 8: The Node Exporter, and what any exporter is made of

*Mastering Prometheus (William Hegedus, Packt, 2024). Course lesson: `#m-8`. Code: POC 21 · 5. Read: full text, one pass; all figures seen.*

## Summary

An exporter is a separate program that reads some other system and exposes what it finds as Prometheus metrics. Its anatomy is small: metric **descriptors** (name, help, labels), a **collector** with `Describe` and `Collect` methods, a **registry**, and an HTTP handler on `/metrics` that runs every collector on each scrape. The client library adds Go runtime and HTTP metrics for free.

The Node Exporter is one of the few exporters maintained by the Prometheus project itself, alongside the Blackbox and SNMP exporters. Its motto in the book: if it is in `/proc`, the Node Exporter can get it. It has 49 collectors on by default on Linux, each running in its own goroutine, so turning collectors off doesn’t make scrapes faster. On Windows, use windows_exporter.

The author begs you not to alert on load average; the kernel source itself calls it a silly number. **Pressure stall information** measures time lost waiting for CPU, memory or I/O. For memory and I/O it has two levels: *waiting* (some tasks blocked but the CPU found other work) and *stalled* (everything blocked, CPU cycles wasted). CPU has only waiting. Alert on memory and I/O stalled time; it can replace naïve “95% memory used” alerts, which fire on healthy caches.

## Key ideas

- The parts of an exporter: descriptors, collector, registry, handler
- The collectors that matter most and the queries that go with them
- Why load average misleads and pressure stall information doesn’t
- The textfile collector and how to keep it honest
- Troubleshooting slow scrapes per collector

## What the lesson covers

- What an exporter is
- The collectors you will query
- Pressure, not load average
- The textfile collector
- When scrapes get slow

## Claims and numbers

- Alert on memory and I/O stalled time; it can replace naïve “95% memory used” alerts, which fire on healthy caches.

## Terms

descriptors, collector, registry, Pressure stall information

## Interview line

An exporter is a small program with descriptors, a collector and a registry behind a /metrics handler. From the Node Exporter I rely on cpu, meminfo with MemAvailable, filesystem, diskstats, netdev, conntrack and especially pressure stall information, which shows real contention where load average misleads. For machine facts from batch jobs I use the textfile collector with an alert on file age so it can’t go stale silently.

## On AWS

On EC2, run node_exporter as a systemd service from the AMI or install it with SSM Run Command, and discover it with `ec2_sd_configs`. On EKS, it runs as a DaemonSet from kube-prometheus-stack, or use the ADOT collector’s `hostmetrics` receiver instead. The CloudWatch agent covers similar host metrics for CloudWatch-native setups, but doesn’t expose pressure stall information by default. For Windows instances, windows_exporter.

## Takeaways

- An exporter is descriptors, a collector, a registry and a handler.
- Use MemAvailable and pressure stall information; avoid load average.
- The textfile collector needs an age alert; per-collector durations find slow scrapes.
