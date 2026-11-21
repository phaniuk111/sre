import json
import os
import sys
import threading
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import relabel as R  # noqa: E402

FLEET = [
    {"id": "i-1", "private_ip": "10.0.1.10", "az": "eu-west-2a", "state": "running", "type": "m7g.large", "tags": {"Name": "web1", "Service": "web", "Monitoring": "true", "Team": "checkout"}},
    {"id": "i-2", "private_ip": "10.0.2.11", "az": "eu-west-2b", "state": "running", "type": "m7g.large", "tags": {"Name": "web2", "Service": "web", "Monitoring": "true", "Team": "checkout"}},
    {"id": "i-3", "private_ip": "10.0.3.12", "az": "eu-west-2c", "state": "stopped", "type": "t4g.small", "tags": {"Name": "old", "Service": "web", "Monitoring": "true"}},
    {"id": "i-4", "private_ip": "10.0.1.13", "az": "eu-west-2a", "state": "running", "type": "t4g.small", "tags": {"Name": "bastion", "Service": "ops"}},
]


def test_ec2_discovery_then_relabel_keeps_only_monitored_running_instances():
    got = R.discover(FLEET)
    assert [t["labels"]["instance"] for t in got] == ["web1", "web2"]
    assert got[0]["address"] == "10.0.1.10:9100"  # connect by IP, label by name
    assert got[0]["labels"] == {"instance": "web1", "job": "web", "az": "eu-west-2a", "Team": "checkout"}


def test_meta_labels_disappear_after_relabeling():
    t = R.relabel(R.ec2_discovery(FLEET[:1], 9100)[0], [])
    assert not [k for k in R.finalize(t) if k.startswith("__")]
    assert R.finalize(t)["instance"] == "10.0.1.10:9100"  # instance defaults to __address__


def test_keep_on_port_name_and_job_from_service_label():
    k8s = {"__address__": "10.1.0.5:9100", "__meta_kubernetes_endpoint_port_name": "http-metrics", "__meta_kubernetes_service_label_jobLabel": "node-exporter"}
    cfg = [{"source_labels": ["__meta_kubernetes_endpoint_port_name"], "regex": "http-metrics", "action": "keep"},
           {"source_labels": ["__meta_kubernetes_service_label_jobLabel"], "regex": "(.+)", "target_label": "job", "replacement": "${1}"}]
    assert R.finalize(R.relabel(k8s, cfg))["job"] == "node-exporter"
    assert R.relabel({**k8s, "__meta_kubernetes_endpoint_port_name": "grpc"}, cfg) is None


def test_regex_is_anchored():
    assert R.relabel({"x": "running-ish"}, [{"source_labels": ["x"], "regex": "running", "action": "keep"}]) is None


def test_labeldrop_and_replace_to_empty_removes_label():
    out = R.relabel({"a": "1", "pod_template_hash": "abc"}, [{"regex": "pod_template_hash", "action": "labeldrop"}])
    assert out == {"a": "1"}
    out = R.relabel({"a": "1"}, [{"source_labels": ["missing"], "regex": "", "target_label": "a", "replacement": ""}])
    assert out == {}


def test_http_sd_endpoint_meets_the_contract():
    srv = R.http_sd_app(FLEET)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{srv.server_port}/targets") as r:
            body = r.read()
            assert R.validate_http_sd(r.status, r.headers["Content-Type"], body) == []
        groups = json.loads(body)
        assert {"targets": ["10.0.1.10:9100"], "labels": {"instance": "web1"}} in groups
        assert len(groups) == 3  # stopped instance excluded
    finally:
        srv.shutdown()
    assert R.validate_http_sd(200, "text/plain", b"[]") == ["Content-Type must be application/json"]


def test_hashmod_matches_prometheus_definition_and_shards_are_disjoint():
    targets = [f"10.0.{i // 250}.{i % 250}:9100" for i in range(1000)]
    shards = [[t for t in targets if R.relabel({"__address__": t}, R.shard_config(3, k)) is not None] for k in range(3)]
    assert sum(map(len, shards)) == 1000 and not set(shards[0]) & set(shards[1])
    assert all(250 < len(s) < 420 for s in shards)  # roughly even at scale


def test_small_target_counts_are_uneven_and_resharding_moves_most_targets():
    few = [f"10.0.0.{i}:9100" for i in range(24)]
    counts = R.balance(few, 2)
    assert max(counts.values()) - min(counts.values()) >= 2  # the book saw 8 vs 16
    many = [f"10.0.{i // 250}.{i % 250}:9100" for i in range(2000)]
    assert R.moved_when_resharding(many, 2, 3) > 0.5  # plain modulo reshuffles: plan resharding
