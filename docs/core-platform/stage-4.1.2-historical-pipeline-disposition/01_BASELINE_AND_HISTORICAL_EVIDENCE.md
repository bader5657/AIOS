# Baseline and Historical Evidence

## Accepted Assessment Baseline

| Ref | Git-resolved SHA |
|---|---|
| `main` | `f80b47c288295fd59cbdd3f92fbd344f494f07e2` |
| `origin/main` | `f80b47c288295fd59cbdd3f92fbd344f494f07e2` |
| Stage 4.1.1 governance merge | `f80b47c288295fd59cbdd3f92fbd344f494f07e2` |

The worktree was clean and the complete active Stage 4.1.1 package was present
on `main` before this governance package was created.

## Historical Git Object

| Field | Value |
|---|---|
| Commit | `9d1288cca4b47d6fca963a8bff16041599b5e5c4` |
| Parent | `b68dc674f54310f0b00e7a365b78db5c2f197d0a` |
| Subject | `feat(core-platform): add asset pipeline` |
| Historical branch evidence | `origin/sprint-18-conversation-engine` at `e6ac77a3b287d839f6f8709da0c4652a332083c1` |

The commit added exactly five files and 108 lines:

- `core/pipeline/__init__.py` — empty package marker;
- `core/pipeline/asset_pipeline.py` — 56-line runtime;
- `core/pipeline/state.py` — 10-line six-value enum;
- `tests/unit/pipeline/__init__.py` — empty package marker; and
- `tests/unit/pipeline/test_asset_pipeline.py` — 42-line single test.

Git-wide searches at the commit and historical branch tip found no production
caller or integration reference outside those runtime files and the single
test. The historical component was isolated, not integrated into Universal
Ingestion, Request Context, Registry, or another runtime entrypoint.
