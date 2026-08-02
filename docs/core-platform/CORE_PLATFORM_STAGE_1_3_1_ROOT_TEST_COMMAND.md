# Core Platform Stage 1.3.1 Repository-Root Test Command

## Record

| Field | Value |
|---|---|
| Execution Plan position | Stage 1 — Main Step 1.3 — Sub Step 1.3.1 |
| Command-selection baseline | `24ec9f5b5d07c4c247b1788e450cd5fdf9a370b2` (`main`) |
| Invocation location | Repository root |
| Test framework | Python standard-library `unittest` |
| Expected suite inventory | 16 `test_*.py` modules and 212 test methods under `tests/unit/domain/` |
| Prepared and reviewed by | Codex implementation agent |
| Review date | `2026-08-02` |
| Review status | Accepted for Stage 1 verification |

## Accepted Command

Run this single command from the repository root:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/unit/domain -p 'test_*.py' -v
```

This is the repository-root test command for the current suite. The explicit
`tests/unit/domain` discovery start is required because the current tracked
tree does not make every directory between `tests/` and the test modules an
importable package. Using `python3 -m unittest discover -s tests` on this
baseline can therefore exit successfully after discovering zero tests.

`PYTHONDONTWRITEBYTECODE=1` prevents the verification command from creating
tracked-tree-adjacent bytecode artifacts. The command uses only Python's
standard library and does not introduce a test dependency.

## Expected Suite Inventory

The accepted command must discover this current tracked inventory:

| Test area | Modules | Test methods |
|---|---:|---:|
| Shared Domain Foundation | 8 | 105 |
| Customer domain | 8 | 107 |
| Total | 16 | 212 |

The expected module set is every tracked `test_*.py` file beneath
`tests/unit/domain/` at the command-selection baseline. No current tests exist
outside that directory. Future authorized test additions require the command
and expected inventory to be revalidated; this record does not silently claim
that later suites are covered.

## Discovery Acceptance

The accepted command was invoked from the repository root against the exact
baseline recorded above. It discovered and ran 212 tests, reported `OK`, and
created no bytecode files. This confirms that the command does not reproduce
the known zero-test root-discovery result and matches the expected suite
inventory.

This invocation accepts the command for discovery. Recording the current
functional and dependency-boundary baseline, including coverage gaps and the
verification interpretation of the 212 results, belongs exclusively to Sub
Step 1.3.2 and is not performed by this record.

## Scope and Result

This Sub Step defines and accepts only one repository-root test command and
its expected current-suite inventory. It adds no alternate command, runner,
test package marker, source behavior, test case, dependency, configuration,
workflow, architecture, authority, gate, milestone status, release claim, or
product-version change.

No Blueprint, Roadmap, Governance, `VERSION`, Domain Foundation, Execution
Plan, freeze document, milestone document, source, or test file is changed.

**Sub Step 1.3.1 result: PASS**

Main Step 1.3 remains in progress. The next frozen-plan position is Stage 1,
Main Step 1.3, Sub Step 1.3.2. That Sub Step is not started by this record.
