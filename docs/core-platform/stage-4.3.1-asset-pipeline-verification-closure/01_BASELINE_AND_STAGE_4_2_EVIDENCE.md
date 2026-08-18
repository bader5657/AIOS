# Baseline and Stage 4.2 Evidence

## Exact Git Baseline

Git resolved the following before verification:

| Ref | SHA |
|---|---|
| `HEAD` | `ca2a9b9ea146c74c42bb56724643d3c65e95781c` |
| `main` | `ca2a9b9ea146c74c42bb56724643d3c65e95781c` |
| `origin/main` | `ca2a9b9ea146c74c42bb56724643d3c65e95781c` |

The worktree was clean. PR #16 was `MERGED`; its sole implementation commit
was `402feac49b0f47cacd9feb0e677988ac90334c65` and its merge commit was the
verification baseline above. Unrelated historical PR #1 does not modify or
supersede accepted `main` and is not a Stage 4 blocker.

## Stage 4.2 Evidence Mapping

| Plan item | Required evidence | Accepted baseline evidence | Result |
|---|---|---|---|
| 4.2.1 approved runtime | Focused implementation diff | New `core/pipeline/asset_pipeline.py` and package export in PR #16 | PASS |
| 4.2.1 approved states/transitions | No invented state; bounded success/failure only | Frozen runtime transport result; no state module or enum | PASS |
| 4.2.2 Request Context input | Integration scope and tests | Universal Ingestion constructs active Request Context before Pipeline call | PASS |
| 4.2.2 recognized identity | Upstream integration | Primitive `recognized_input_type.value` passed explicitly | PASS |
| 4.2.2 Document Manifest output | Integration tests | Pipeline delegates current Manifest entrypoint and returns its path/readiness | PASS |
| 4.2.2 lifecycle order | Connects Stages 2–3 without bypass | Store → Metadata → Manifest call-order and failure tests | PASS |

The active implementation approval explicitly applies to Stage 4.2.1 and the
minimum Stage 4.2.2 caller integration. PR #16 changed exactly its three
runtime and five test paths. No intervening Stage 4.2 sub-step remains.
