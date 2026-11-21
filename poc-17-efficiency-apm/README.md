# POC 17: Efficiency — application productivity metrics and on-by-default optimisation

**Book:** *Platform Engineering at Google* (early release), chapter "Deep Dive: Efficiency" (chapter 14 of the final book)

Two services both use 20% more CPU this month. One is handling 20% more traffic. The other got slower. The bill can't tell them apart. The chapter's answer is the **application productivity metric**: each service reports its useful work, and the platform divides by the resources it used.

| Function in `apm.py` | Idea from the chapter |
|---|---|
| `classify(before, after)` | growth, regression, optimisation or steady, from work per CPU-second |
| `suspicious_work_metrics(series)` | a work metric that doesn't track resource use is probably the wrong metric (a batch job counting batches, not items) |
| `default_on_decision(effects)` | ship optimisations on by default; absorb small regressions; give large ones an opt-out and investigate it |
| `wasted_work(requests)` | CPU spent after the caller's deadline is waste; probes and hedges are a necessary cost worth sizing |

```bash
python apm.py examples/fleet.json
python -m pytest -q
```

## On AWS
* **Work counters:** emit a business counter per service with CloudWatch Embedded Metric Format (requests, orders, records). Give the golden path a default: API services report requests, pipelines report records.
* **Resources:** vCPU-seconds and memory from Container Insights or Lambda duration; cost from Cost and Usage Reports with cost allocation tags.
* **The ratio:** CloudWatch metric math, alarmed with anomaly detection so a productivity drop after a deploy raises a ticket.
* **Where to optimise:** a continuous profiler across the fleet (CodeGuru Profiler or an eBPF profiler) to find the shared library or runtime that dominates, and Compute Optimizer for sizing.
* **Shift down:** deliver the fix through base images, shared libraries and Graviton-by-default in the pipeline template, so teams receive it at their next deploy without doing anything.

## Interview talking points
* Shared foundations create leverage twice: you can see the whole fleet, and one fix helps everyone. In 2015 Google's memory allocator was about 8% of fleet usage, larger than any single application.
* Effort deters adoption. Automatic profile-guided optimisation doubled its fleet share in a year once it became a one-line change.
* Options are a cost: each one enlarges the set of states every later change must be tested against.
* A hash table with deliberately random iteration order stops code depending on the order (Hyrum's law), which keeps the implementation free to improve.
* Three lessons: take the long view, don't assume the platform is fixed, create leverage and use it.
