# Identifier Variance and Permanent Limitation

| Identifier | Approved value | Executed value |
|---|---|---|
| Correlation | `stage-0.10-live-1` | `stage010-live-001` |
| Request | `stage-0.10-live-request-1` | `stage010-request-001` |

Both executed identifiers satisfy the accepted inference contract and were
preserved exactly through `BrainInferenceInvoker`, `InferenceRequest`, the
provider, and `InferenceResult`. The approved and executed values remain
visibly different in this permanent record.

## Required limitation

The single Stage 0.10 live invocation used valid alternate
correlation/request identifiers rather than the literal identifiers recorded
in the approval. The alternate identifiers were preserved exactly end-to-end,
and no payload, provider, model, runtime, resource, security,
invocation-count, or production-safety semantics changed. No rerun was
performed.

The variance applies only to the consumed Stage 0.10 evidence. It grants no
prospective flexibility for later governed execution.

## Process-control correction

The harness identifiers were not copied exactly from controlling authority.
Future controlled execution must derive constants directly from the approval,
apply an explicit pre-inference equality gate, and abort before provider
invocation if harness and authority values differ. This control does not
rewrite historical evidence.
