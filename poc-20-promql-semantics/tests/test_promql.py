import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import promql as P  # noqa: E402


def counter(step, values, start=0):
    return [(start + i * step, v) for i, v in enumerate(values)]


def test_instant_selector_lookback_and_staleness():
    s = [({"__name__": "up", "job": "a"}, [(0, 1), (60, 1)]), ({"__name__": "up", "job": "b"}, [(0, 1)])]
    assert P.instant(s, 120) == [({"__name__": "up", "job": "a"}, 1), ({"__name__": "up", "job": "b"}, 1)]
    assert [l["job"] for l, _ in P.instant(s, 330)] == ["a"]  # b's last sample is older than 5 minutes


def test_rate_of_a_steady_counter_is_exact():
    samples = counter(15, [i * 30 for i in range(21)])  # +2 per second, scraped every 15s
    assert P.rate(samples, 300, 300) == pytest.approx(2.0)


def test_counter_reset_is_not_a_negative_rate():
    # 0,10,20,30 then the process restarts: 5,15
    samples = counter(10, [0, 10, 20, 30, 5, 15])
    raw = 15 - 0
    corrected = raw + 30  # Prometheus adds the value before the drop
    assert P.increase(samples, 50, 50) > 0
    assert P.increase(samples, 50, 51) == pytest.approx(corrected * 51 / 50, rel=0.15)
    assert P.irate(samples, 50, 60) == pytest.approx(1.0)


def test_increase_is_extrapolated_to_the_window_edges():
    # samples at 5..55 every 10s in a 60s window, +1 per second: 50 observed, 60 expected
    samples = counter(10, [100 + i * 10 for i in range(6)], start=5)
    assert P.increase(samples, 60, 60) == pytest.approx(60.0)
    # a counter that starts at 0 in the window is only extrapolated forwards: 55, not 60
    fresh = counter(10, [i * 10 for i in range(6)], start=5)
    assert P.increase(fresh, 60, 60) == pytest.approx(55.0)


def test_extrapolation_stops_at_zero_for_a_new_counter():
    # a counter born inside the window can't be extrapolated back below zero
    samples = [(30, 1), (40, 11), (50, 21), (60, 31)]
    inc = P.increase(samples, 60, 60)
    assert 30 < inc < 32


def test_irate_follows_the_last_two_points_only():
    samples = counter(15, [0, 15, 30, 45, 60, 600])  # a burst at the end
    assert P.irate(samples, 75, 300) == pytest.approx(36.0)
    assert P.rate(samples, 75, 300) < P.irate(samples, 75, 300)


def test_delta_for_gauges_can_be_negative_and_changes_counts():
    targets = counter(60, [10, 10, 9, 9, 8])  # count(up) quietly losing targets
    assert P.delta(targets, 240, 300) < 0
    restarts = counter(60, [100, 100, 160, 160, 220])  # kube_pod_start_time changing
    assert P.changes(restarts, 240, 300) == 2


def test_histogram_quantile_interpolates_inside_the_bucket():
    buckets = [(0.1, 50), (0.25, 80), (0.5, 95), (1.0, 100), (math.inf, 100)]
    # rank for p95 = 95, which lands exactly on the 0.5 bucket boundary
    assert P.histogram_quantile(0.95, buckets) == pytest.approx(0.5)
    # p90: rank 90 is in (0.25, 0.5], 10 of 15 observations into it
    assert P.histogram_quantile(0.9, buckets) == pytest.approx(0.25 + 0.25 * 10 / 15)
    # p50: rank 50 in the first bucket, interpolated from 0
    assert P.histogram_quantile(0.5, buckets) == pytest.approx(0.1)


def test_histogram_quantile_in_the_inf_bucket_returns_highest_finite_bound():
    buckets = [(0.1, 10), (0.5, 20), (math.inf, 100)]
    assert P.histogram_quantile(0.99, buckets) == 0.5


def test_aggregation_by_and_without():
    v = [({"__name__": "x", "ns": "a", "pod": "1"}, 1), ({"__name__": "x", "ns": "a", "pod": "2"}, 2), ({"__name__": "x", "ns": "b", "pod": "3"}, 4)]
    assert P.aggregate("sum", v, by=["ns"]) == [({"ns": "a"}, 3), ({"ns": "b"}, 4)]
    assert P.aggregate("count", v, without=["pod"]) == [({"ns": "a"}, 2), ({"ns": "b"}, 1)]


A = [({"color": "blue", "smell": "ocean"}, 10), ({"color": "red", "smell": "cinnamon"}, 31), ({"color": "green", "smell": "grass"}, 27)]
B = [({"color": "blue", "smell": "ocean"}, 19), ({"color": "red", "smell": "cinnamon"}, 8), ({"color": "green", "smell": "jungle"}, 14)]


def test_one_to_one_matches_all_labels_by_default():
    out = P.binop("+", A, B)
    assert out == [({"color": "blue", "smell": "ocean"}, 29), ({"color": "red", "smell": "cinnamon"}, 39)]  # green differs on smell


def test_on_and_ignoring_narrow_the_match():
    assert P.binop("+", A, B, on=["color"]) == [({"color": "blue"}, 29), ({"color": "green"}, 41), ({"color": "red"}, 39)]
    assert [v for _, v in P.binop("+", A, B, ignoring=["smell"])] == [29, 41, 39]


def test_many_to_one_needs_group_left():
    A2 = [({"color": "blue", "smell": "ocean"}, 7), ({"color": "red", "smell": "cinnamon"}, 5), ({"color": "blue", "smell": "powder"}, 2)]
    B2 = [({"color": "blue", "smell": "ocean"}, 20), ({"color": "red", "smell": "cinnamon"}, 8), ({"color": "green", "smell": "jungle"}, 14)]
    with pytest.raises(ValueError):
        P.binop("+", A2, B2, on=["color"])
    out = P.binop("+", A2, B2, on=["color"], group_left=[])
    assert sorted(v for _, v in out) == [13, 22, 27]


def test_info_metric_join_copies_labels():
    mem = [({"__name__": "container_memory_rss", "node": "n1", "pod": "a"}, 100), ({"__name__": "container_memory_rss", "node": "n1", "pod": "b"}, 50)]
    info = [({"__name__": "kube_node_info", "node": "n1", "os_image": "Bottlerocket", "kubelet_version": "v1.29"}, 1)]
    out = P.binop("*", mem, info, on=["node"], group_left=["os_image"])
    assert all(l["os_image"] == "Bottlerocket" for l, _ in out) and [v for _, v in out] == [100, 50]


def test_set_operators():
    assert [l["color"] for l, _ in P.set_op("and", A, B)] == ["blue", "red"]
    assert [l["color"] for l, _ in P.set_op("unless", A, B)] == ["green"]
    assert len(P.set_op("or", A, B)) == 4


def test_ntp_alert_suppressed_after_reboot_with_unless():
    offset = [({"instance": "a"}, 0.2), ({"instance": "b"}, 0.3)]
    rebooted = [({"instance": "b"}, 1)]  # changes(node_boot_time_seconds[30m]) > 0
    firing = P.set_op("unless", P.compare(offset, ">", 0.05), rebooted, on=["instance"])
    assert [l["instance"] for l, _ in firing] == ["a"]


def test_bool_turns_a_filter_into_zero_or_one():
    v = [({"svc": "a"}, 0.9995), ({"svc": "b"}, 0.99)]
    assert P.compare(v, ">=", 0.999, as_bool=True) == [({"svc": "a"}, 1.0), ({"svc": "b"}, 0.0)]
