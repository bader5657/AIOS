# Verification Evidence and Level B Boundary

| Gate | Verified result |
|---|---|
| Focused Stage 0.17 | `43 passed` |
| Stage 0.16 | `23 passed`; `45 subtests passed` |
| Stage 0.15 | `3 passed` |
| Stage 0.14 | `40 passed` |
| Stage 0.11 | `67 passed` |
| Stage 0.12 | `21 passed` |
| Stage 0.9 | `23 passed` |
| Stage 0.7 | `61 passed`; mocks only |
| Stage 0.3 | `84 passed` |
| Core regressions | `246 passed`; `58 skipped`; `275 subtests passed` |
| Domain regressions | `212 passed`; `454 subtests passed`; `3` unchanged warnings |
| Stage 8 | `9 passed`; `12 environment-skipped` |
| Stage 9 | `20 passed`; `76 subtests passed` |
| Full repository | `782 passed`; `58 skipped`; `750 subtests passed` |
| Compile/static | `PASS` |
| Dependency/import | `PASS` |
| Prohibited-source | `PASS` |
| `git diff --check` | `PASS` |
| Exact two-path closed world | `PASS` |

Focused, full-suite, compile/static, diff, and protected-path checks were
repeated at the exact merge commit during closure and passed. The PostgreSQL
environment skips and three Domain collection warnings are unchanged and are
not failures.

Stage 0.17 closes only the semantic projection contract and normalized-field
prerequisites at repository-capability level. Level B remains unauthorized and
still requires schema binding; isolated staging composition;
Mapper/Receiver/provider lifecycle assembly; synthetic staging authority;
operational safety gates; and explicit Level B activation authority. Separate
privacy/DLP governance is required if real user prose must be scanned for
embedded secrets.
