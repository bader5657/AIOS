# Dependency, Security, Test, and Review Evidence

## Exact dependencies and default-deny policy

The mapper imports only `CoreRouteResult` and `CoreRouteTarget` from the public
Core route contract, and `BRAIN_INPUT_SCHEMA_VERSION`, `BrainInput`, and
`BrainIntent` from `core.brain.input_contracts`, plus standard-library types and
UUID support.

The active policy exception permits only:

`core/core_to_brain_mapper.py → core.brain.input_contracts`

and enforces exactly those three Brain symbols. All other Core-to-Brain imports
remain default-deny, including receiver, invoker, provider, Ollama/runtime,
Memory, Specialist, and orchestration dependencies.

The mapper has no database, Registry, Storage, filesystem, environment,
network, httpx, logging, persistence, Memory, Specialist, business semantics,
or runtime lifecycle surface. It uses CoreRouteResult only for eligibility.

## Verification evidence

| Gate | Result |
|---|---|
| Focused mapper | `40 PASS` |
| Stage 0.11 | `67 PASS` |
| Stage 0.12 | `21 PASS` |
| Stage 0.9 | `23 PASS` |
| Stage 0.7 | `61 PASS` |
| Stage 0.3 | `129 PASS` |
| Core regressions | `188 PASS`; `253` subtests PASS |
| Domain regressions | `212 PASS`; `454` subtests PASS |
| Stage 8 | `9 PASS`; `12` environment-skipped |
| Stage 9 | `8 PASS`; `53` subtests PASS |
| Full repository | `727 PASS`; `58` skipped; `727` subtests PASS; `0` failures |
| Compile/static | `PASS` |
| Dependency/import audit | `PASS` |
| Prohibited-source audit | `PASS` |
| `git diff --check` | `PASS` |
| Exact three-path audit | `PASS` |

Reviewer audit found no unresolved issue. The dependency audit was narrowed
only for the exact approved semantic-contract edge; mapper behavior required no
redesign.
