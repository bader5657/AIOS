# Dependency Boundary, Regression Review, and Benchmark Limitation

## Stage 8 and dependency boundary

The Stage 8 allowlist adds exactly:

`"httpx": {"core/brain/providers/ollama.py"}`

The test remains path-specific and default-deny. All prior dependency entries,
Core/Domain restrictions, provider-SDK prohibitions, reverse-dependency gates,
and unauthorized-import failure behavior remain intact.

`httpx==0.28.1` was already pinned. No dependency/requirements file changed and
no provider SDK or new dependency was added.

## Verification evidence

| Gate | Evidence | Result |
|---|---|---|
| Focused adapter | `61 passed` | `PASS` |
| Adapter plus Stage 8 | `70 passed` | `PASS` |
| Stage 0.3 / Stage 0.5 plus adapter | `190 passed` | `PASS` |
| Core | `113 passed`; `232 subtests passed` | `PASS` |
| Domain | `212 passed`; `454 subtests passed` | `PASS` |
| Full suite | `576 passed`; `58 skipped`; `727 subtests passed`; zero failures | `PASS` |
| Compile/static | complete `compileall` | `PASS` |
| Dependency/import audit | full suite plus Stage 8 exact-path gate | `PASS` |
| Prohibited-source audit | focused static/source gates | `PASS` |
| `git diff --check` | implementation and post-merge audit | `PASS` |
| Closed-world diff | exactly four authorized paths | `PASS` |

The three existing Pytest collection warnings concern pre-existing Domain test
classes with constructors; they are not failures or Stage 0.7 regressions.

## Reviewer fixes

Both fixes remained within approved scope and architecture: relative Brain
imports satisfy reverse-dependency audits, and non-finite/contract-invalid
provider output is contained as `MALFORMED_OUTPUT`.

## Preserved benchmark limitation

`The first official cold structured-output request produced a contained schema-invalid confidence value (100 instead of 0.0–1.0). The result was rejected correctly. After methodology clarification, all 20 official warm requests were valid. Official reliability is therefore 20/21 (95.24%).`

The limitation remains permanent. Repository adapter verification does not
replace or upgrade the Stage 0.6.4 benchmark classification.
