# POC 13: Safe Coding — "if it isn't secure, it shouldn't compile"

**Book:** *Platform Engineering at Google* (early release), chapter "Security" (chapter 15 of the final book)

The chapter's argument: SQL injection persists because the API takes a string, and a string carries no record of where its characters came from. Asking every developer to get every call site right can't work. So take the risky API away and replace it with a **safe abstraction** whose interface can't be misused.

| Path | What it shows |
|---|---|
| `safedb/` | `TrustedSql`, a type that can only be built from developer-written text, and `SafeDB`, the one place allowed to touch the raw driver. Builders for the awkward cases: `placeholders(n)` for IN lists, `identifier(name, allowed)` for runtime-chosen columns |
| `conformance.py` | An AST check for CI. R1: no raw SQL driver outside `safedb`. R2: `sql()` only ever receives a string literal. Narrow, decidable rules, so no false negatives and little noise |
| `examples/vulnerable.py` | The album lookup written with string concatenation |
| `examples/safe.py` | The same lookup through the safe API |
| `examples/sneaky.py` | Three attempts to smuggle input through `sql()`; each is rejected by the conformance check |

```bash
python -m pytest -q
python conformance.py examples     # exits 1: vulnerable.py and sneaky.py are flagged
python conformance.py examples/safe.py safedb
```

The first test shows the attack working: an album ID of `x' OR id='b7` returns another user's album from the string-based version. The second shows the same input doing nothing against the safe version.

## How this is the chapter's pattern
* **Risky operation:** `connection.execute(sql)`, safe only if `sql` came from trusted parts.
* **Two properties of a safe abstraction:** the public API puts no safety condition on callers, and the implementation owns the condition. So a reviewer verifies `safedb/__init__.py` once, for every caller.
* **Technique:** a *type invariant*. A runtime check isn't possible because the information (provenance) isn't in a string.
* **Enforcement:** in Go or Java the compiler does it. Python has no compile step, so the literal-only rule is a CI conformance check.
* **Ergonomics:** the safe API has to cover what people really need, or they will queue for exceptions.
* **Exceptions:** `EXCEPTIONS` in `conformance.py` is the tracked, reviewed list. Start with legacy call sites there and burn it down.

## On AWS
The pattern is language-level, so it travels. Wrap the RDS Data API (`execute_statement` with `parameters`), a PostgreSQL driver for Aurora, or Athena parameterised queries the same way. Run `conformance.py` as a CodeBuild or GitHub Actions step, and report the share of services with zero findings as a fleet metric: that number is evidence the bug class is absent.

## Interview talking points
* Testing can't show the absence of security bugs: an attacker chooses the input you didn't test.
* Shift down, don't only shift left: experts solve the problem once in the platform and every application inherits it.
* Google reports zero SQL injection in protected applications for more than a decade from this pattern.
* Stopping new unsafe code is enough to bring the rate down; old code's bugs get found and fixed over time.
* The same idea covers HTML (auto-escaping templates, Trusted Types), memory (safe languages) and cryptography (intent-based APIs).
