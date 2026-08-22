# Project Owner Approval, Activation, and Next Action

## Project Owner approval

I, as Project Owner, authorize repository-only implementation of the first
BrainInferenceInvoker within the verified Stage 0.9 boundary.

The invoker may construct one provider-neutral InferenceRequest from explicit
Brain-local arguments, invoke exactly one injected InferenceProvider, and
return the resulting InferenceResult unchanged.

No Core handoff wiring, concrete Ollama dependency, Brain production
composition, Memory, Specialist, business action, retry, fallback, persistence,
live inference, or production activation is authorized.

## Publication and activation

This approval becomes active only after this governance-only package is
committed, pushed, reviewed as clean and mergeable, normally merged into
`main`, and a post-merge audit confirms `HEAD == main == origin/main` with a
clean worktree.

Publication changes no implementation or runtime. After activation, only the
two paths in `00_PACKAGE_CONTROL_BASELINE_AND_AUTHORITY.md` may be created by a
separate implementation task.

## Stop conditions

Implementation stops if a third path, Core change, concrete Ollama import,
canonical contract change, Memory/Specialist/business logic, composition root,
new dependency, or live inference is required.

## Remaining blockers and next official action

There is no blocker to activating this implementation approval. Core handoff,
concrete composition, live Brain staging invocation, cleanup, and production
activation are deferred, separately governed work and are not prerequisites
for repository-only implementation.

After activation, the exact next official action is:

`Intelligence Stage 0.9 — BrainInferenceInvoker Repository Implementation`

It must create only the two authorized paths, run the full approved regression
matrix, execute no live inference, and then return its evidence for separate
verification and final acceptance closure.

`INTELLIGENCE STAGE 0.9 BRAIN INFERENCE INVOCATION IMPLEMENTATION APPROVED — READY TO BUILD`
