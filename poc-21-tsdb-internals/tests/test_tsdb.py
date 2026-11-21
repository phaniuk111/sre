import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import tsdb as T  # noqa: E402

N = 120  # one 30-minute chunk at 15s


def perfect(interval=15000):
    return [1_700_000_000_000 + i * interval for i in range(N)]


def test_regular_scrapes_cost_about_one_bit_per_timestamp():
    ts = perfect()
    assert T.timestamp_bits(ts) < 64 + 16 + N  # header, then ~1 bit each


def test_constant_values_compress_to_one_bit():
    assert T.value_bits([1.0] * N) == 64 + (N - 1)


def test_jitter_costs_disk_and_tolerance_wins_it_back():
    rnd = random.Random(7)
    clean = perfect()
    jittery = [t + rnd.randint(-30, 30) for t in clean]
    vals = [float(i // 10) for i in range(N)]
    good = T.bytes_per_sample(clean, vals)
    bad = T.bytes_per_sample(jittery, vals)
    assert bad > 2 * good
    assert not T.jitter_report(jittery, 15000)["aligned"]
    # 30ms tolerance is allowed for a 15s interval? max is 1% = 150ms, so yes
    fixed = T.snap_timestamps(jittery, 15000, tolerance_ms=60)
    assert T.bytes_per_sample(fixed, vals) < bad
    assert T.jitter_report(fixed, 15000)["aligned"]


def test_tolerance_is_capped_at_one_percent_of_interval():
    ts = [0, 15500, 31000]
    assert T.snap_timestamps(ts, 15000, tolerance_ms=1000) == [0, 15500, 31000]  # 500ms > 150ms cap


def test_counter_values_cost_more_than_constants_but_far_less_than_raw():
    vals = [float(i * 3) for i in range(N)]
    bps = T.bytes_per_sample(perfect(), vals)
    assert 0.5 < bps < 4  # raw would be 16 bytes per sample


def test_postings_intersection_starts_from_the_shortest_list():
    series = [{"__name__": "http_requests_total", "job": "api", "pod": f"p{i}", "code": c} for i in range(200) for c in ("200", "500")]
    series += [{"__name__": "up", "job": "api", "pod": f"p{i}"} for i in range(200)]
    idx = T.Index(series)
    got, work = idx.select([("__name__", "=", "http_requests_total"), ("pod", "=", "p7"), ("code", "=~", "5..")])
    assert got == [{"__name__": "http_requests_total", "job": "api", "pod": "p7", "code": "500"}]
    assert work < 40  # a few binary searches, not a scan of 600 series


def test_compaction_ranges():
    assert T.compaction_ranges(15) == [2, 6, 18]  # 10% of 15 days is 36h
    assert T.compaction_ranges(365)[-1] <= 31 * 24


EXPO = """# HELP http_requests_total requests
# TYPE http_requests_total counter
""" + "\n".join(f'http_requests_total{{env="production",path="/user/{u}",code="200"}} 1' for u in range(50)) + """
up{env="production",job="api"} 1
"""


def test_cardinality_report_finds_the_unbounded_label_and_useless_ones():
    r = T.cardinality_report(T.parse_exposition(EXPO))
    assert r["label_value_counts"][0] == ("path", 50)
    assert r["series_by_metric"][0] == ("http_requests_total", 50)
    assert "env=production" in r["everywhere"]  # same on every series: make it an external label


def test_limits_fail_the_whole_scrape():
    s = T.parse_exposition(EXPO)
    ok, why = T.apply_limits(s, sample_limit=20)
    assert not ok and "sample_limit" in why
    assert T.apply_limits(s, sample_limit=100, label_limit=5)[0]
    assert not T.apply_limits(s, label_value_length_limit=5)[0]
