import os
import sys

import pytest

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "examples"))

import safe  # noqa: E402
import vulnerable  # noqa: E402
from conformance import check_paths, check_source  # noqa: E402
from safedb import SafeDB, TrustedSql, identifier, sql  # noqa: E402

ATTACK = "x' OR id='b7"  # AND binds tighter than OR, so the owner check drops out


def test_injection_works_against_string_api():
    conn = vulnerable.setup()
    assert vulnerable.get_album(conn, "alice", "a1") == [("Holiday",)]
    assert vulnerable.get_album(conn, "alice", "b7") == []          # not her album
    assert vulnerable.get_album(conn, "alice", ATTACK) == [("Private",)]  # ...and yet


def test_same_attack_is_inert_against_safe_api():
    db = safe.setup()
    assert safe.get_album(db, "alice", "a1") == [("Holiday",)]
    assert safe.get_album(db, "alice", ATTACK) == []  # compared as data, never parsed as SQL


def test_safe_api_rejects_plain_strings():
    db = safe.setup()
    with pytest.raises(TypeError):
        db.query("SELECT title FROM albums WHERE id = '" + ATTACK + "'")
    with pytest.raises(TypeError):
        TrustedSql("SELECT 1")          # no constructing one directly
    with pytest.raises(TypeError):
        sql("SELECT 1") + " OR 1=1"     # no appending a str


def test_builders_cover_in_lists_and_sort_columns():
    db = safe.setup()
    assert safe.get_albums(db, "alice", ["a1", "b7"]) == [("Holiday",)]
    with pytest.raises(ValueError):
        identifier("title; DROP TABLE albums", {"title", "id"})


def test_conformance_passes_safe_code_and_flags_the_rest():
    ex = os.path.join(ROOT, "examples")
    assert check_paths([os.path.join(ex, "safe.py")]) == []
    assert {f[2] for f in check_paths([os.path.join(ex, "vulnerable.py")])} == {"R1"}
    sneaky = check_paths([os.path.join(ex, "sneaky.py")])
    assert [f[2] for f in sneaky] == ["R2", "R2", "R2"]
    # the abstraction itself is the one place allowed to import the driver
    assert check_paths([os.path.join(ROOT, "safedb")]) == []


def test_conformance_accepts_joined_literals_only():
    assert check_source('from safedb import sql\nq = sql("SELECT a " + "FROM t")\n') == []
    assert check_source('from safedb import sql\nq = sql("SELECT %s" % x)\n')[0][2] == "R2"
