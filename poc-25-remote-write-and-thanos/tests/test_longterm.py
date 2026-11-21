import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import longterm as L  # noqa: E402


def test_remote_write_plan_from_the_ingestion_rate():
    p = L.remote_write_plan(250_000)
    assert p["min_shards"] == 100 and p["warnings"] == []
    assert "3x" in L.remote_write_plan(10_000, capacity=1000, max_samples_per_send=500)["warnings"][0]
    assert L.remote_write_plan(1_000_000)["warnings"]  # 1M/s needs more than 200 x 2500


def test_backoff_doubles_from_30ms_to_5s():
    s = L.backoff_schedule()
    assert s[:4] == [0.03, 0.06, 0.12, 0.24] and s[-1] == 5.0


def two_replicas():
    a = [(t, 1.0) for t in range(0, 600, 15) if not 120 <= t < 300]   # replica A restarts
    b = [(t, 1.0) for t in range(0, 600, 15) if t not in (45, 60)]      # replica B misses two scrapes
    return {"a": a, "b": b}


def test_thanos_dedup_fills_gaps_from_the_other_replica():
    out = L.dedup_thanos(two_replicas())
    assert [t for t, _, _ in out] == list(range(0, 600, 15))  # no gaps at all
    assert {r for t, _, r in out if 120 <= t < 300} == {"b"}


def test_mimir_ha_tracker_loses_samples_during_failover():
    r = {k: {t for t, _ in v} for k, v in two_replicas().items()}
    got = L.dedup_mimir(r, "a", failover_after=30, now_series=list(range(0, 600, 15)))
    times = [t for t, _ in got]
    assert 120 not in times and 135 not in times  # 30s of silence before electing b
    assert 150 in times


def test_victoria_dedup_keeps_one_sample_per_interval():
    both = [(t, 1) for t in range(0, 300, 15)] + [(t + 3, 1) for t in range(0, 300, 15)]
    assert len(L.dedup_victoria(both, 15)) == 20


def test_downsampling_keeps_aggregates_and_grows_storage():
    raw = [(t, float(t)) for t in range(0, 3600, 15)]
    five = L.downsample(raw, 300)
    assert len(five) == 12 and five[0]["count"] == 20 and five[0]["max"] == 285.0
    assert L.downsample_plan(30) == ["raw"] and L.downsample_plan(48) == ["raw", "5m"] and L.downsample_plan(300) == ["raw", "5m", "1h"]
    # three copies of old data: raw + 5m + 1h. Downsampling speeds queries; it doesn't save space.


def test_unequal_retention_makes_old_data_unreachable_at_fine_steps():
    assert L.queryable(200, {"raw": 90, "5m": 90, "1h": 365}) == ["1h"]


def test_query_frontend_splits_by_day_and_reuses_cached_days():
    day = 86400
    assert len(L.split_by_interval(0, 7 * day, day)) == 7
    c = L.ResultCache()
    c.query(0, 7 * day, day, lambda s, e: (s, e))
    c.query(0, 8 * day, day, lambda s, e: (s, e))
    assert c.fetches == 8  # the second query only fetched the new day


def test_ketama_moves_far_fewer_series_than_hashmod_when_adding_a_receiver():
    series = [f'up{{instance="10.0.{i // 250}.{i % 250}:9100"}}' for i in range(5000)]
    three, four = ["r0", "r1", "r2"], ["r0", "r1", "r2", "r3"]
    hm = L.moved(L.hashmod_ring(series, three), L.hashmod_ring(series, four))
    kt = L.moved(L.ketama_ring(series, three), L.ketama_ring(series, four))
    assert hm > 0.6 and kt < 0.35


def test_replication_quorum():
    assert L.write_quorum(3) == 2 and L.write_quorum(1) == 1 and L.write_quorum(5) == 3


def test_recommendations():
    assert "Managed Service for Prometheus" in L.recommend({"aws-managed"})
    assert L.recommend({"global-view-without-central-ingest"}).startswith("Thanos")
    assert L.recommend({"multi-tenant"}).startswith("Grafana Mimir")
