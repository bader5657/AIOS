# Test Strategy, Decisions, Blockers, and Next Action

## Required future repository verification

After prerequisites are approved, tests must prove:

1. a non-Brain route calls neither mapper nor receiver;
2. one eligible exact route calls the mapper exactly once;
3. correlation ID, semantic data, and provenance pass exactly;
4. mapper-generated `BrainInput` reaches the receiver exactly once;
5. successful and failed `InferenceResult` objects return unchanged;
6. mapper and receiver `TypeError`/`ValueError` remain distinct;
7. native async execution has no nested runner, blocking call, or hidden task;
8. retry, fallback, business action, persistence, and content logging are absent;
9. no concrete provider or provider lifecycle dependency exists; and
10. request ID remains mapper-owned with exact end-to-end ID propagation.

Fakes are required for the receiver/provider boundary. After repository wiring
passes, a separate authority may exercise the actual Core route through the
mapper and receiver into isolated Ollama/Qwen using synthetic data. No such test
or inference is authorized now.

## Project Owner decisions required

Only these unresolved decisions block implementation approval:

1. define the originating runtime correlation-ID contract and owner;
2. define the exact approved provider-neutral semantic-data projection and its
   owner for every eligible input class;
3. define which existing identifiers, if any, become `input_reference` and
   `context_references`;
4. choose direct unchanged `InferenceResult` return or a separately approved
   later Brain-result boundary;
5. choose one exact dependency seam: narrowly approved direct boundary types or
   one minimal Core-side async callable/protocol;
6. ratify mapper and receiver as explicit injected lifecycle dependencies;
7. identify the inactive Level A implementation path only after decisions 1–5;
   and
8. identify the future composition-root path separately before Level B.

The likely continuation owner is Universal Ingestion immediately after exact
Core route resolution, but its production module must not be named as an
authorized change until the semantic contract and dependency seam are frozen.
No clean exact implementation path set is currently authoritative.

## Final decision and next action

No frozen architecture meaning must change, and no new architectural layer is
yet proven necessary. The current blocker is missing contract and composition
authority, not an architecture-change finding.

Stage 0.16 implementation approval is withheld. The next official action is a
bounded Project Owner decision package for correlation identity, semantic
projection, provenance, result destination, and the minimal async dependency
seam. Only after those decisions may a Runtime Wiring Implementation Approval
freeze exact production/test paths. Production activation remains prohibited.

Preserve all Stage 0.15 evidence and Stage 0.8/0.10/0.13 temporary sources;
cleanup is not authorized here.
