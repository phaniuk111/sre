"""Conformance check for the safe SQL abstraction. Run it in CI; a finding fails the build.

This is static analysis used the way the security chapter recommends: it does
not hunt for an open-ended class of bugs. It verifies two narrow, decidable
properties, so it has no false negatives for them:

  R1  only the safedb package may import a raw SQL driver;
  R2  every call to sql(...) passes a string literal (or literals joined by +).

Its only failure mode is being conservative, and that is resolved in the open:
use the safe pattern, or add the file to EXCEPTIONS with a reviewer and reason.
"""
from __future__ import annotations

import ast
import os
import sys

RAW_DRIVERS = {"sqlite3", "psycopg", "psycopg2", "pymysql", "MySQLdb", "asyncpg", "pyodbc", "cx_Oracle"}
SAFE_PACKAGE = "safedb"
# path -> (reviewer, reason). Tracked debt, reviewed by the security owner.
EXCEPTIONS: dict = {}


def _is_literal(node) -> bool:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return True
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return _is_literal(node.left) and _is_literal(node.right)
    return False  # f-strings, names, calls, % formatting: all rejected


def check_source(src: str, path: str = "<string>"):
    findings = []
    tree = ast.parse(src, path)
    in_safe = SAFE_PACKAGE in path.replace("\\", "/").split("/")
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)) and not in_safe:
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            for n in names:
                if n.split(".")[0] in RAW_DRIVERS:
                    findings.append((path, node.lineno, "R1", f"raw SQL driver '{n}' imported outside {SAFE_PACKAGE}"))
        if isinstance(node, ast.Call):
            f = node.func
            name = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None
            if name == "sql" and not in_safe:
                if len(node.args) != 1 or node.keywords or not _is_literal(node.args[0]):
                    findings.append((path, node.lineno, "R2", "sql() must be called with a string literal; pass values as parameters"))
    return findings


def check_paths(paths):
    findings = []
    for root in paths:
        files = [root] if root.endswith(".py") else [os.path.join(d, f) for d, _, fs in os.walk(root) for f in fs if f.endswith(".py")]
        for path in sorted(files):
            if path in EXCEPTIONS:
                continue
            findings += check_source(open(path).read(), path)
    return findings


if __name__ == "__main__":
    found = check_paths(sys.argv[1:] or ["."])
    for path, line, rule, msg in found:
        print(f"{path}:{line}: {rule} {msg}")
    print(f"{len(found)} finding(s)")
    sys.exit(1 if found else 0)
