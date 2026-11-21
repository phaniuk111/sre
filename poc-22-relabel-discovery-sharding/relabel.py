"""Service discovery, relabeling and hashmod sharding, implemented the way Prometheus does them.

- ec2_discovery(): what ec2_sd_configs hands to relabeling: __address__ plus __meta_ec2_* labels.
- relabel(): the relabel_configs actions (replace, keep, drop, hashmod, labelmap, labeldrop, labelkeep).
- finalize(): after relabeling, instance defaults to __address__ and every __-prefixed label is removed.
- http_sd_app(): a custom HTTP SD endpoint (status 200, JSON, UTF-8, static_config-shaped body).
- shard(): hashmod sharding of targets across Prometheus servers.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from http.server import BaseHTTPRequestHandler, HTTPServer

DEFAULT = {"separator": ";", "regex": "(.*)", "replacement": "$1", "action": "replace"}


def _expand(template, m):
    # Prometheus uses $1 and ${1}; Python's re uses \1
    return re.sub(r"\$\{?(\w+)\}?", lambda g: m.group(int(g.group(1))) if g.group(1).isdigit() else m.group(g.group(1)) or "", template)


def hashmod(value, modulus):
    """Prometheus: md5 of the joined source labels, last 8 bytes as a big-endian uint64, modulo N."""
    digest = hashlib.md5(value.encode()).digest()
    return int.from_bytes(digest[8:], "big") % modulus


def relabel(labels, configs):
    """Apply relabel_configs in order. Returns the new label dict, or None if the target is dropped."""
    labels = dict(labels)
    for raw in configs:
        c = {**DEFAULT, **raw}
        action = c["action"]
        regex = re.compile(f"^(?:{c['regex']})$")
        value = c["separator"].join(labels.get(s, "") for s in c.get("source_labels", []))
        if action == "keep":
            if not regex.match(value):
                return None
        elif action == "drop":
            if regex.match(value):
                return None
        elif action == "replace":
            m = regex.match(value)
            if m:
                target = _expand(c["target_label"], m)
                new = _expand(c["replacement"], m)
                if new == "":
                    labels.pop(target, None)
                else:
                    labels[target] = new
        elif action == "hashmod":
            labels[c["target_label"]] = str(hashmod(value, c["modulus"]))
        elif action == "labelmap":
            for k in list(labels):
                m = regex.match(k)
                if m:
                    labels[_expand(c["replacement"], m)] = labels[k]
        elif action == "labeldrop":
            labels = {k: v for k, v in labels.items() if not regex.match(k)}
        elif action == "labelkeep":
            labels = {k: v for k, v in labels.items() if regex.match(k)}
        else:
            raise ValueError(f"unsupported action {action}")
    return labels


def finalize(labels):
    """What survives to become the target's labels: instance defaults to __address__, __* labels vanish."""
    out = {k: v for k, v in labels.items() if not k.startswith("__")}
    out.setdefault("instance", labels["__address__"])
    return out


def ec2_discovery(instances, port):
    """Shape of ec2_sd_configs output. Every tag becomes __meta_ec2_tag_<Key>."""
    out = []
    for i in instances:
        t = {"__address__": f"{i['private_ip']}:{port}", "__meta_ec2_instance_id": i["id"],
             "__meta_ec2_instance_state": i["state"], "__meta_ec2_availability_zone": i["az"],
             "__meta_ec2_private_ip": i["private_ip"], "__meta_ec2_instance_type": i["type"]}
        for k, v in i.get("tags", {}).items():
            t[f"__meta_ec2_tag_{re.sub(r'[^a-zA-Z0-9_]', '_', k)}"] = v
        out.append(t)
    return out


# the relabel_configs a platform team would ship for EC2 node exporters
EC2_RELABEL = [
    {"source_labels": ["__meta_ec2_instance_state"], "regex": "running", "action": "keep"},
    {"source_labels": ["__meta_ec2_tag_Monitoring"], "regex": "true", "action": "keep"},
    {"source_labels": ["__meta_ec2_tag_Service"], "target_label": "job"},
    {"source_labels": ["__meta_ec2_tag_Name"], "target_label": "instance"},  # friendly name, still scrape the IP
    {"source_labels": ["__meta_ec2_availability_zone"], "target_label": "az"},
    {"regex": "__meta_ec2_tag_(Team|CostCenter)", "action": "labelmap", "replacement": "${1}"},
]


def discover(instances, port=9100, configs=EC2_RELABEL):
    out = []
    for t in ec2_discovery(instances, port):
        r = relabel(t, configs)
        if r is not None:
            out.append({"address": r["__address__"], "labels": finalize(r)})
    return out


# ───────────────────────────────────────────── HTTP SD
def http_sd_body(instances, port=9100):
    """static_config in JSON: a list of {targets: [...], labels: {...}}. One group per instance so each
    can carry its own instance label while Prometheus connects by IP, avoiding DNS outages."""
    groups = []
    for i in instances:
        if i["state"] != "running":
            continue
        groups.append({"targets": [f"{i['private_ip']}:{port}"], "labels": {"instance": i["tags"].get("Name", i["id"])}})
    return groups


def http_sd_app(instances):
    class H(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            if self.path != "/targets":
                self.send_response(404); self.end_headers(); return
            body = json.dumps(http_sd_body(instances)).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):
            pass

    return HTTPServer(("127.0.0.1", 0), H)


def validate_http_sd(status, content_type, body_bytes):
    """The three requirements from the Prometheus docs, plus the body shape."""
    problems = []
    if status != 200:
        problems.append("status must be 200")
    if not content_type.startswith("application/json"):
        problems.append("Content-Type must be application/json")
    try:
        data = json.loads(body_bytes.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return problems + ["body must be UTF-8 JSON"]
    if not isinstance(data, list) or not all(isinstance(g, dict) and isinstance(g.get("targets"), list) for g in data):
        problems.append("body must be a list of {targets: [...], labels: {...}}")
    return problems


# ───────────────────────────────────────────── sharding
def shard_config(shards, index, source="__address__"):
    """The two relabel steps the Prometheus Operator adds to every job for spec.shards."""
    return [{"source_labels": [source], "modulus": shards, "target_label": "__tmp_hash", "action": "hashmod"},
            {"source_labels": ["__tmp_hash"], "regex": str(index), "action": "keep"}]


def shard(targets, shards):
    """Which shard scrapes each target. Deterministic, but not balanced for small target counts."""
    return {t: hashmod(t, shards) for t in targets}


def moved_when_resharding(targets, before, after):
    a, b = shard(targets, before), shard(targets, after)
    return sum(1 for t in targets if a[t] != b[t]) / len(targets)


def balance(targets, shards):
    return Counter(shard(targets, shards).values())
