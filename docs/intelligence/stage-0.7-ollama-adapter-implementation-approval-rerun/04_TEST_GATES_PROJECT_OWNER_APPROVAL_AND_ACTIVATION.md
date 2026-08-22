# Test Gates, Project Owner Approval, and Activation

## Focused unit-test contract

Use injected `httpx.MockTransport` or equivalent mocks/fakes and fake schema
resolver/validator callables. No live Ollama or network is required or allowed.
Tests must cover:

1. frozen/slotted exact config and every config validation rule;
2. exact descriptor and static model binding;
3. exact payload acceptance, missing/unknown keys, blank/untrimmed/overlong/
   non-string instruction, non-mapping data, empty and nested data;
4. NaN rejection inherited at request construction;
5. exact canonical UTF-8/sorted/compact rendering with no trailing newline;
6. exactly one user message, no system/history/multi-turn state;
7. separate schema-ref resolution, unknown-ref failure, provider schema copy,
   and independent validation;
8. exact body allowlist, `stream=false`, `keep_alive=5m`, configured model,
   and absence of `options`;
9. effective minimum timeout and exactly one POST;
10. valid success, exact metadata, monotonic bounded duration;
11. connect/unreachable, timeout, HTTP/provider, model mismatch, incomplete,
    malformed/oversized envelope, missing content, invalid/non-object JSON, and
    schema-mismatch mappings;
12. cancellation propagation with no second action;
13. no retry, fallback, persistence, state, content logging, or raw-response
    escape;
14. no dynamic model/provider setting, Core reverse dependency, Brain wiring,
    production integration, or runtime lifecycle behavior; and
15. exact path/import/dependency/prohibited-source audits.

## Regression and verification matrix

Implementation verification must run focused adapter/payload/rendering tests;
Stage 0.3 inference-contract tests; Stage 0.5 provider-abstraction tests; Core
and relevant Domain regressions; Stage 8/9 critical gates; complete compile/
static checks; dependency/import and prohibited-source audits;
`git diff --check`; and an exact three-path diff audit.

No live inference occurs. A live test of
`InferenceRequest → OllamaInferenceProvider → staging Ollama/Qwen → validated InferenceResult`
is required later under separate authority using synthetic data.

## Project Owner approval

I, as Project Owner, authorize repository implementation of the first Brain-owned OllamaInferenceProvider adapter under the now-accepted Stage 0.7 input payload contract.

The adapter may translate exactly one provider-neutral instruction/data payload into one Ollama user message, execute one bounded async local request, independently validate the structured result, and return an InferenceResult.

No Brain orchestration wiring, live staging inference, production inference, provider routing, persistence, retry, fallback, or Core modification is authorized.

## Publication and activation

- branch: `implementation/intelligence-stage-0.7-ollama-adapter` for the later
  implementation;
- exact implementation diff: the three authorized paths only;
- approval activation: normal clean, mergeable governance PR into `main`;
- force/history rewrite: none; and
- runtime/inference/Brain/Core/production effect: none.

Merging this approval activates repository implementation authority only. The
next action is:

`Intelligence Stage 0.7 — implement exactly the three authorized adapter/test paths, then run the complete approved verification matrix without live inference.`

`INTELLIGENCE STAGE 0.7 OLLAMA ADAPTER IMPLEMENTATION APPROVED — READY TO BUILD`
