"""Validate OpenTelemetry/ADOT collector configs against the deployment rules in the books.

Observability with Grafana (ch7, ch10, ch11) gives the placement rules: kubelet, host and log
collection per node (DaemonSet); cluster metrics and Kubernetes events from exactly one instance;
a gateway for processing and fan-out. The rest are collector good practice that the books touch on:
memory_limiter first, batch last, health checks, no log cascade, SigV4 for AMP.
"""
from __future__ import annotations

import math

import yaml

PER_NODE = {"kubeletstats", "hostmetrics", "filelog"}
SINGLETON = {"k8s_cluster", "k8sobjects"}


def kind(name):
    return name.split("/")[0]


def load(path):
    return yaml.safe_load(open(path))


def validate(cfg):
    errors, warnings = [], []
    mode, replicas = cfg.get("mode", "deployment"), cfg.get("replicas", 1)
    defined = {sec: set(cfg.get(sec, {}) or {}) for sec in ("receivers", "processors", "exporters", "connectors", "extensions")}
    pipelines = cfg["service"]["pipelines"]
    used = {"receivers": set(), "processors": set(), "exporters": set()}
    connector_as_exporter, connector_as_receiver = set(), set()
    for pname, p in pipelines.items():
        for r in p.get("receivers", []):
            if r in defined["connectors"]:
                connector_as_receiver.add(r)
            elif r not in defined["receivers"]:
                errors.append(f"{pname}: receiver {r} is not defined")
            used["receivers"].add(r)
        for e in p.get("exporters", []):
            if e in defined["connectors"]:
                connector_as_exporter.add(e)
            elif e not in defined["exporters"]:
                errors.append(f"{pname}: exporter {e} is not defined")
            used["exporters"].add(e)
        procs = p.get("processors", [])
        for pr in procs:
            if pr not in defined["processors"]:
                errors.append(f"{pname}: processor {pr} is not defined")
            used["processors"].add(pr)
        if procs and kind(procs[0]) != "memory_limiter":
            errors.append(f"{pname}: memory_limiter must be the first processor")
        if "batch" in procs and procs[-1] != "batch" and not (kind(procs[-1]) == "tail_sampling"):
            warnings.append(f"{pname}: batch should be the last processor")
        if not procs:
            warnings.append(f"{pname}: no processors; add at least memory_limiter")
    for c in defined["connectors"]:
        if (c in connector_as_exporter) != (c in connector_as_receiver):
            errors.append(f"connector {c} must be an exporter in one pipeline and a receiver in another")
    for sec in ("receivers", "processors", "exporters"):
        for unused in defined[sec] - used[sec]:
            warnings.append(f"{sec[:-1]} {unused} is defined but not used")
    kinds = {kind(r) for r in used["receivers"]}
    if mode == "daemonset" and kinds & SINGLETON:
        errors.append(f"{sorted(kinds & SINGLETON)} in a DaemonSet duplicates cluster data on every node; run one instance")
    if mode != "daemonset" and replicas > 1 and kinds & SINGLETON:
        errors.append("cluster receivers need exactly one replica")
    if mode != "daemonset" and kinds & PER_NODE:
        errors.append(f"{sorted(kinds & PER_NODE)} only see the node they run on: use a DaemonSet")
    if "prometheus" in kinds and mode != "daemonset" and replicas > 1:
        warnings.append("prometheus receiver with several replicas scrapes every target several times; shard or use the target allocator")
    for name, r in (cfg.get("receivers") or {}).items():
        if kind(name) == "filelog" and not any("otel" in x or "collector" in x for x in r.get("exclude", [])):
            errors.append("filelog must exclude the collector's own logs, or it reads what it writes (a log cascade)")
        if kind(name) in ("hostmetrics", "kubeletstats"):
            secs = int(str(r.get("collection_interval", "10s")).rstrip("s"))
            if secs < 30:
                warnings.append(f"{name}: collection_interval {secs}s; the Helm preset's 10s is a lot of samples, consider 60s")
    for name, e in (cfg.get("exporters") or {}).items():
        if kind(name) == "prometheusremotewrite" and "aps-workspaces" in e.get("endpoint", ""):
            if (e.get("auth") or {}).get("authenticator") != "sigv4auth" or "sigv4auth" not in defined["extensions"]:
                errors.append(f"{name}: AMP needs SigV4: add the sigv4auth extension and reference it")
    if "health_check" not in cfg["service"].get("extensions", []):
        warnings.append("enable the health_check extension for liveness and readiness probes")
    return errors, warnings


def tail_sampling_needs_trace_routing(agent_cfg, gateway_cfg):
    """With more than one gateway replica, every span of a trace must reach the same replica,
    or tail sampling decides on fragments. The agents must route by trace ID."""
    if "tail_sampling" not in {kind(p) for p in (gateway_cfg.get("processors") or {})} or gateway_cfg.get("replicas", 1) == 1:
        return True
    trace_exporters = [e for p, pl in agent_cfg["service"]["pipelines"].items() if p.startswith("traces") for e in pl["exporters"]]
    return all(kind(e) == "loadbalancing" and agent_cfg["exporters"][e].get("routing_key") == "traceID" for e in trace_exporters)


def buffer_size_mb(outage_minutes, events_per_sec, avg_event_bytes):
    """How much disk the file_storage queue needs to ride out a backend outage. Publish the outage you
    can tolerate as an SLI of the collection layer."""
    return math.ceil(outage_minutes * 60 * events_per_sec * avg_event_bytes / 1_000_000)
