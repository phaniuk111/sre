import copy
import os
import sys

HERE = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, HERE)
import collector as C  # noqa: E402

AGENT = C.load(os.path.join(HERE, "config", "node-agent.yaml"))
CLUSTER = C.load(os.path.join(HERE, "config", "cluster-agent.yaml"))
GATEWAY = C.load(os.path.join(HERE, "config", "gateway.yaml"))


def test_shipped_configs_have_no_errors():
    for cfg in (AGENT, CLUSTER, GATEWAY):
        errors, warnings = C.validate(cfg)
        assert errors == [], errors
        assert not [w for w in warnings if "not used" in w], warnings


def test_cluster_receivers_in_a_daemonset_duplicate_data():
    bad = copy.deepcopy(AGENT)
    bad["receivers"]["k8s_cluster"] = {"auth_type": "serviceAccount"}
    bad["service"]["pipelines"]["metrics"]["receivers"].append("k8s_cluster")
    assert any("duplicates cluster data" in e for e in C.validate(bad)[0])
    two = copy.deepcopy(CLUSTER); two["replicas"] = 2
    assert any("exactly one replica" in e for e in C.validate(two)[0])


def test_per_node_receivers_need_a_daemonset():
    bad = copy.deepcopy(AGENT); bad["mode"] = "deployment"
    assert any("DaemonSet" in e for e in C.validate(bad)[0])


def test_processor_order_and_log_cascade():
    bad = copy.deepcopy(AGENT)
    bad["service"]["pipelines"]["logs"]["processors"] = ["batch", "memory_limiter"]
    bad["receivers"]["filelog"]["exclude"] = []
    errors, warnings = C.validate(bad)
    assert any("memory_limiter must be the first" in e for e in errors)
    assert any("log cascade" in e for e in errors)


def test_amp_requires_sigv4_and_connectors_must_be_wired_both_ways():
    bad = copy.deepcopy(GATEWAY)
    del bad["exporters"]["prometheusremotewrite/amp"]["auth"]
    bad["service"]["pipelines"]["metrics"]["receivers"].remove("servicegraph")
    errors, _ = C.validate(bad)
    assert any("SigV4" in e for e in errors)
    assert any("connector servicegraph" in e for e in errors)


def test_fast_host_metrics_are_flagged():
    fast = copy.deepcopy(AGENT); fast["receivers"]["hostmetrics"]["collection_interval"] = "10s"
    assert any("10s" in w for w in C.validate(fast)[1])


def test_tail_sampling_across_replicas_needs_trace_id_routing():
    assert C.tail_sampling_needs_trace_routing(AGENT, GATEWAY)
    naive = copy.deepcopy(AGENT)
    naive["service"]["pipelines"]["traces"]["exporters"] = ["otlp/gateway"]
    assert not C.tail_sampling_needs_trace_routing(naive, GATEWAY)


def test_buffer_sizing():
    # ride out a 30-minute backend outage at 5,000 log lines/s of ~400 bytes
    assert C.buffer_size_mb(30, 5000, 400) == 3600
