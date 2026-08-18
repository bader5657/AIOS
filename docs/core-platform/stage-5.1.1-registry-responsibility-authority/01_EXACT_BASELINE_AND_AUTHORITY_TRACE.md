# Exact Baseline and Authority Trace

## Git Baseline

| Evidence | SHA/result |
|---|---|
| `HEAD` at governance start | `c3e12f4fc4adf9dfddc5e6427fab63284cba09b1` |
| local `main` | `c3e12f4fc4adf9dfddc5e6427fab63284cba09b1` |
| local `origin/main` | `c3e12f4fc4adf9dfddc5e6427fab63284cba09b1` |
| remote `refs/heads/main` | `c3e12f4fc4adf9dfddc5e6427fab63284cba09b1` |
| Stage 4 exit-gate merge | `c3e12f4fc4adf9dfddc5e6427fab63284cba09b1` |
| Working tree before branch creation | clean |

PR #18 is merged at the baseline. Historical PR #1 is unrelated, dirty
against current `main`, and carries no check result; the active Stage 4 closure
already classifies it as non-current evidence and not a blocker.

## Authority Trace

| Requirement | Controlling authority | Stage 5.1.1 consequence |
|---|---|---|
| Official pipeline contains PostgreSQL Registry after Document Manifest | Blueprint | Establish the named capability's bounded responsibility |
| PostgreSQL stores identity, metadata, relationships, status, and file location | Blueprint | Exact closed responsibility categories |
| Original binary is not primarily stored in PostgreSQL | Blueprint | Binding binary exclusion |
| No roadmap scope invention | Frozen Roadmap | Remain inside Core Platform |
| Missing authority cannot be inferred | Authority Hierarchy | Stop at undecided representation and implementation details |
| `PostgreSQL Registry` canonical; `Registry Entry` unresolved | Canonical Model | Use the canonical capability name; create no Registry Entry |
| Register boundary is Ingestion-to-Core | Layer Architecture | Preserve producer/consumer direction without runtime design |
| PostgreSQL Registry owns Register | Core Platform Authority Decision extension | Preserve bounded ownership only |
| Stage 5.1.1 requires an approved data-responsibility contract | Frozen Execution Plan | This package is the required governance output |
| Stage 4 ends at Register handoff readiness | Stage 4 exit closure | Consume readiness as prerequisite, not execution |
| Storage, Metadata, and Manifest retain their approved meanings | Active Stage 3 authority | Registry consumes bounded results without redefining them |
| Historical Registry implementation is rejected | Stage 1.2.2 disposition | Treat commit `d58c1c3` as evidence only |

The Project Owner instruction initiating this package supplies the scoped
Stage 5.1.1 decisions recorded here. It grants no runtime or persistence
implementation authority.
