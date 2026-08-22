# Failure, State, Test, Rollback, and Next Gate

## Conditional success and failure behavior

Success requires `success=True`, no failure code, present independently
validated structured output, `provider_id="ollama-local"`, the configured model
ID, bounded duration, and no raw response.

Only the existing failure taxonomy may be used:

| Condition | `FailureCode` |
|---|---|
| unsupported capability, invalid payload, unknown schema ref, prohibited request semantics | `INVALID_REQUEST` |
| connection/DNS/socket/connect failure to the approved endpoint | `RUNTIME_UNAVAILABLE` |
| effective whole-operation deadline | `TIMEOUT` |
| non-success HTTP or provider/runtime/envelope failure without a narrower mapping | `PROVIDER_FAILURE` |
| malformed envelope, missing content, invalid JSON, partial output, schema mismatch | `MALFORMED_OUTPUT` |
| approved pre-invocation policy rejection | `POLICY_DENIED` |
| positively identified approved runtime resource rejection only | `RESOURCE_LIMIT` |

Provider/httpx exceptions must be contained and sanitized. Caller
`asyncio.CancelledError` propagates normally and triggers no retry. Retry,
fallback, persistence, cache, history, sessions, embeddings, and conversation
state remain `NONE`.

Logging is limited to correlation/request/provider/model identifiers, bounded
duration, success/failure, and failure code. Payloads, prompts, message content,
structured output, raw responses, and Telegram/user/business data are excluded.

The adapter does not start/stop Ollama, download/preload models, manage the
container/network/firewall, import Core, or wire Brain orchestration. Core
remains unchanged at `AIOS_BRAIN_BOUNDARY`.

## Conditional verification matrix

After input-payload approval and a later implementation approval, mock/fake
unit tests must cover all 35 requested gates: descriptor/config/URL/model/time/
keep-alive invariants; capability/schema/payload translation; non-streaming
request; success/result metadata/duration; every approved failure mapping;
cancellation; exactly one call/no retry; raw-response, state, and logging
containment; no Core reverse dependency/dynamic model/production integration;
compile/static, dependency/import, prohibited-source, and `git diff --check`.

Regression verification must include focused adapter tests, Stage 0.3 contract
tests, Stage 0.5 abstraction tests, Core and relevant Domain regressions, Stage
8/9 critical gates, complete compile/static checks, dependency/import and
prohibited-source audits, and `git diff --check`.

Live staging inference is `REQUIRED LATER UNDER SEPARATE AUTHORITY` to prove
`InferenceRequest → OllamaInferenceProvider → staging Ollama/Qwen → validated InferenceResult`
with synthetic data only. It is not authorized here.

## Resources and rollback

No new dependency or resource-ceiling change is conditionally needed. Existing
Ollama ceilings remain `3 GiB`, `1 vCPU`, concurrency `1`, approved disk, and
the fixed model. Adapter overhead must remain negligible.

Future rollback is repository-only removal/revert of the three adapter/config/
test paths. There is no database or staging-runtime rollback.

## Stop conditions

Stop on any Core change, Brain orchestration implementation, canonical request
contract change under adapter authority, full schema registry, new dependency,
provider persistence, dynamic routing, production endpoint, or fourth
implementation path. Scope expansion must be approved separately.

## Project Owner authorization disposition

The requested statement beginning “I, as Project Owner, authorize repository
implementation” is intentionally **not activated** because its explicit input
payload prerequisite is unresolved. Activating it now would contradict the
fail-closed Step 10 authority.

## Required next action

`Intelligence Stage 0.7 — Input Payload Contract Evaluation and Approval`

That governance-only action must choose and freeze one minimal provider-neutral
envelope, including exact keys/types/bounds, instruction ownership, data
placement, rejection rules, deterministic rendering, and tests. It must decide
whether this is a bounded semantic profile within the existing
`InferenceRequest.input_payload` field or a canonical contract change. It must
not implement the adapter, execute inference, or connect Brain/Core.

After that approval closes, rerun the Ollama Provider Adapter Implementation
Approval against the new authority baseline.
