"""Find coupling nobody chose (Platform Engineering at Google, "Coupling").

The chapter lists four ways to discover implicit coupling: static analysis,
tracing, log correlation and chaos engineering. This script takes the kind of
evidence those methods produce and reports the antipatterns the chapter names:

  shared database        several services touch the same table
  implicit queue coupling producers and consumers tied by an unregistered format
  distributed monolith   services that almost always deploy together
  megamorphic artifact   a config file read by many services, none of which needs it all
  call cycles            A -> B -> A at runtime
  hidden physical deps   a fault in one failure domain hurt services outside it

On AWS the inputs come from: X-Ray / Application Signals service map (calls),
CloudTrail data events or database audit logs (table access), pipeline events
on EventBridge (deploys), EventBridge Schema Registry or Glue Schema Registry
(schemas), and a Fault Injection Service experiment report (chaos).
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from itertools import combinations


def shared_tables(access):
    """access: [{service, table, mode: 'r'|'w'}] -> tables used by more than one service."""
    by_table = defaultdict(lambda: {"r": set(), "w": set()})
    for a in access:
        by_table[a["table"]][a["mode"]].add(a["service"])
    out = []
    for table, m in sorted(by_table.items()):
        users = m["r"] | m["w"]
        if len(users) > 1:
            # several writers means schema changes need lockstep releases: the worst case
            sev = "high" if len(m["w"]) > 1 else "medium"
            out.append({"table": table, "writers": sorted(m["w"]), "readers": sorted(m["r"] - m["w"]), "severity": sev})
    return out


def queue_coupling(spans, schemas):
    """Publishers and consumers never call each other, yet a format change breaks the consumer."""
    pub, sub = defaultdict(set), defaultdict(set)
    for s in spans:
        if s["kind"] == "publish":
            pub[s["topic"]].add(s["caller"])
        elif s["kind"] == "consume":
            sub[s["topic"]].add(s["caller"])
    return [{"topic": t, "producers": sorted(pub[t]), "consumers": sorted(sub[t])}
            for t in sorted(pub) if sub[t] and not schemas.get(t, False)]


def co_deployed(deploys, min_deploys=4, threshold=0.7):
    """Pairs of services that ship together most of the time (Jaccard similarity of their deploys)."""
    seen = defaultdict(set)
    for d in deploys:
        for s in d["services"]:
            seen[s].add(d["id"])
    out = []
    for a, b in combinations(sorted(seen), 2):
        union = seen[a] | seen[b]
        both = seen[a] & seen[b]
        if len(union) >= min_deploys and len(both) / len(union) >= threshold:
            out.append({"services": [a, b], "together": len(both), "of": len(union), "ratio": round(len(both) / len(union), 2)})
    return out


def independent_release_rate(deploys):
    """Share of releases that shipped exactly one service. The number to drive up."""
    return round(sum(1 for d in deploys if len(d["services"]) == 1) / len(deploys), 2) if deploys else None


def megamorphic(configs, min_consumers=5, max_share=0.5):
    """configs: {artifact: {key: [services]}}. Many readers, and no reader needs most of it."""
    out = []
    for name, keys in sorted(configs.items()):
        per_service = defaultdict(set)
        for k, services in keys.items():
            for s in services:
                per_service[s].add(k)
        if len(per_service) >= min_consumers:
            biggest = max(len(v) for v in per_service.values()) / len(keys)
            if biggest <= max_share:
                out.append({"artifact": name, "consumers": len(per_service), "keys": len(keys), "largest_share_read": round(biggest, 2)})
    return out


def call_cycles(spans):
    graph = defaultdict(set)
    for s in spans:
        if s["kind"] == "rpc":
            graph[s["caller"]].add(s["callee"])
    cycles, seen = [], set()

    def walk(node, path):
        for nxt in sorted(graph[node]):
            if nxt == path[0]:
                key = frozenset(path)
                if key not in seen:
                    seen.add(key)
                    cycles.append(path + [nxt])
            elif nxt not in path:
                walk(nxt, path + [nxt])

    for start in sorted(graph):
        walk(start, [start])
    return cycles


def hidden_physical(chaos):
    """chaos: [{domain, placed_in_domain: [...], impacted: [...]}]. Impact outside the domain is a hidden dependency."""
    return [{"domain": c["domain"], "unexpected": sorted(set(c["impacted"]) - set(c["placed_in_domain"]))}
            for c in chaos if set(c["impacted"]) - set(c["placed_in_domain"])]


def analyse(data):
    return {
        "shared_database": shared_tables(data.get("table_access", [])),
        "implicit_queue_coupling": queue_coupling(data.get("spans", []), data.get("schemas", {})),
        "distributed_monolith": co_deployed(data.get("deploys", [])),
        "independent_release_rate": independent_release_rate(data.get("deploys", [])),
        "megamorphic_artifacts": megamorphic(data.get("configs", {})),
        "call_cycles": call_cycles(data.get("spans", [])),
        "hidden_physical_dependencies": hidden_physical(data.get("chaos", [])),
    }


def fail_open(call, default):
    """Loosen runtime coupling: if the dependency fails, degrade to a default.

    Use for optional enrichments (recommendations, avatars). Never for a security
    or correctness check: those must fail closed.
    """
    try:
        return call()
    except Exception:
        return default


if __name__ == "__main__":
    report = analyse(json.load(open(sys.argv[1])))
    json.dump(report, sys.stdout, indent=2)
    print()
