"""A safe abstraction over a SQL driver: "if it isn't secure, it shouldn't compile".

Risky operation: connection.execute(sql) is safe only if `sql` was assembled from
trusted parts. A plain string carries no record of where its characters came
from, so there is nothing to check at runtime. The fix tightens the condition
into one a type can carry:

    the query text is made only of constants written by the developer

`TrustedSql` is that type. Holding one is the evidence. `SafeDB.query` accepts
nothing else, and untrusted values travel separately as bound parameters.

Python has no compile step, so the "is this a literal?" half of the guarantee is
enforced by `conformance.py` (an AST check run in CI). Together they give the
two properties of a safe abstraction:
  1. the public API puts no safety condition on callers;
  2. this module alone is responsible for the risky operation inside it.
A reviewer can therefore establish safety by reading this file only.
"""
from __future__ import annotations

import sqlite3
from typing import Iterable

_KEY = object()  # module-private: only the builders below can construct a TrustedSql


class TrustedSql:
    __slots__ = ("_text",)

    def __init__(self, text: str, _key=None):
        if _key is not _KEY:
            raise TypeError("build TrustedSql with sql('literal'), not directly")
        self._text = text

    def __add__(self, other: "TrustedSql") -> "TrustedSql":
        if not isinstance(other, TrustedSql):
            raise TypeError("only TrustedSql can be appended to TrustedSql; pass values as parameters")
        return TrustedSql(self._text + " " + other._text, _KEY)

    def __repr__(self):
        return f"TrustedSql({self._text!r})"


def sql(literal: str) -> TrustedSql:
    """Wrap a query whose text is a string literal in the source. conformance.py verifies the literal part."""
    if not isinstance(literal, str):
        raise TypeError("sql() takes a string literal")
    return TrustedSql(literal, _KEY)


def placeholders(n: int) -> TrustedSql:
    """'(?, ?, ?)' for a variable-length IN list. The values still go in as parameters."""
    if not isinstance(n, int) or n < 1:
        raise ValueError("need at least one placeholder")
    return TrustedSql("(" + ", ".join("?" * n) + ")", _KEY)


def identifier(name: str, allowed: Iterable[str]) -> TrustedSql:
    """A column or sort key chosen at runtime, from an allowlist the developer wrote."""
    allowed = set(allowed)
    if name not in allowed:
        raise ValueError(f"{name!r} is not one of {sorted(allowed)}")
    return TrustedSql(name, _KEY)


class SafeDB:
    """The only place in the codebase allowed to touch the raw driver."""

    def __init__(self, path: str = ":memory:"):
        self._conn = sqlite3.connect(path)

    def query(self, q: TrustedSql, *params):
        if not isinstance(q, TrustedSql):
            raise TypeError("SafeDB.query needs a TrustedSql; build it with sql('...') and pass values as parameters")
        return self._conn.execute(q._text, params).fetchall()

    def script(self, q: TrustedSql):
        if not isinstance(q, TrustedSql):
            raise TypeError("SafeDB.script needs a TrustedSql")
        self._conn.executescript(q._text)
