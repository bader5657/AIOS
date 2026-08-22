# Project Owner Approval, Activation, and Next Action

## Project Owner approval

I, as Project Owner, authorize exactly one synthetic live staging integration request through the accepted OllamaInferenceProvider into the isolated Ollama/Qwen staging runtime.

The purpose is only to prove the approved InferenceRequest → provider adapter → runtime → validated InferenceResult path.

No production inference, Brain wiring, business use, retry, fallback, dynamic routing, or Core modification is authorized.

## Activation

This approval becomes active only after:

1. governance-only review confirms this package matches the accepted Stage 0.7 adapter and all preceding authority;
2. Project Owner acceptance is recorded by this package;
3. the governance branch is committed, pushed, reviewed as CLEAN / MERGEABLE, and normally merged;
4. post-merge audit confirms `HEAD == main == origin/main` and a clean worktree.

No inference is part of approval publication.

## Remaining blocker and operator action

The remaining controlled action is the separately performed live execution itself. The operator must execute, in order:

1. mandatory preflight and stop-control evaluation;
2. exactly one temporary-harness adapter invocation using the fixed synthetic request;
3. no retry regardless of result;
4. mandatory postflight safety evaluation;
5. privacy-bounded evidence capture and Stage 0.8 execution classification.

## Next-stage eligibility

Only a passing controlled execution and its separately accepted evidence establish eligibility to evaluate:

`Intelligence Stage 0.9 — First Brain Inference Invocation Boundary Evaluation / Approval`

Stage 0.9 is not authorized or implemented by this package. If Stage 0.8 execution fails, the exact failure returns to governance review without retry or automatic stage advancement.
