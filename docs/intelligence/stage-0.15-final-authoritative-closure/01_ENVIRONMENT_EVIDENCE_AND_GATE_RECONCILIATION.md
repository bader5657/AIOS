# Environment, Evidence, and Gate Reconciliation

## Exact verification authority

The authoritative run used an isolated disposable checkout at exact source
`21aeed1ad0f87a3a28835a9aaf4b67a0f8fab44f`, Python `3.12.3`, and exactly
`pytest 8.4.2`. The dependency freeze was identical before and after execution.

Authoritative retained evidence:

- raw directory: `/opt/aios/runtime/verification/stage-0.15-evidence/authoritative-run-20260823T072739Z`;
- summary: `/opt/aios/runtime/verification/stage-0.15-evidence/authoritative-run-20260823T072739Z/authoritative-summary.txt`;
- summary SHA-256: `78929d9ff2d678885c688ce38d6a62ee2c47f22d7dc6aff8fd33f9f6e3bca73f`;
- prepared venv-only freeze SHA-256: `5b48645e6a267aa8db2be40179a409f0663285727baee06a2e5c7987f351e75c`;
- effective execution freeze SHA-256 before and after:
  `e32f8888f2b36378bdc9178c3d03ac8e1b86043e0b714b11deae3d9424d08093`.

The raw evidence is retained outside the source checkout and is not modified by
this governance closure.

## Exact seventeen-gate result

| Gate | Result |
|---|---|
| 1 — Stage 0.15 integration | `PASS — 3 passed` |
| 2 — CoreToBrainMapper | `PASS — 40 passed` |
| 3 — BrainInput | `PASS — 67 passed` |
| 4 — BrainSemanticReceiver | `PASS — 21 passed` |
| 5 — BrainInferenceInvoker | `PASS — 23 passed` |
| 6 — Ollama adapter mock | `PASS — 61 passed`; mocks only |
| 7 — Stage 0.3 | `PASS — 129 passed` |
| 8 — Core regressions | `PASS — 188 passed`; `58` environment-skipped |
| 9 — Domain regressions | `PASS — 212 passed`; `3` unchanged warnings |
| 10 — Stage 8 | `PASS — 9 passed`; `12` environment-skipped |
| 11 — Stage 9 | `PASS — 8 passed` |
| 12 — Full repository | `PASS — 730 passed`; `58` skipped; `3` warnings; `0` failures |
| 13 — Compile/static | `PASS — 108` Python files compiled in memory |
| 14 — Dependency/import | `PASS — 18` audit tests |
| 15 — Prohibited source | `PASS — 6` audit tests |
| 16 — `git diff --check` | `PASS`; clean worktree |
| 17 — Closed world | `PASS`; exactly one authorized path |

No unresolved failure exists. The 58 skips are existing environment guards for
isolated PostgreSQL tests requiring `AIOS_REGISTRY_TEST_DATABASE_URL`; no manual
skip was introduced and no failure was converted to skip. The three warnings
are the unchanged Domain `PytestCollectionWarning` records for helper
`TestEvent` classes with constructors.

Historical primary pass, skip, and failure totals reconcile exactly. The fresh
runner did not emit a separate aggregate subtest count, so this closure does not
manufacture one. Historical subtest counts remain comparison-only evidence.
