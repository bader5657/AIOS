# State, Logging, Network, Brain/Core, and Resource Boundaries

## State and logging

The adapter is stateless per invocation. It persists no request, result, raw
response, prompt, conversation, embedding, session, schema result, or history.
It owns no Memory, cache treated as Memory, database, or telemetry store.

Only these bounded metadata fields may be logged:

- `correlation_id`;
- `request_id`;
- `provider_id`;
- `model_id`;
- duration;
- success/failure; and
- `failure_code`.

Logs must exclude input/prompt content, `input_payload`, structured output, raw
provider response/error body, Telegram/user/business data, schemas, endpoint,
and credentials. Failure details must be sanitized and content-free. Existing
journald contextual-metadata privacy limitations remain binding.

## Network and production boundary

The first adapter may target only the explicitly configured approved
local/private Ollama endpoint from a separately authorized staging integration
peer. No public endpoint, outbound remote provider, credentials, paid API, or
production network route is authorized.

Initial implementation and repository unit tests must not connect the adapter
to production Brain flow. Production inference, production service wiring,
startup activation, business use, and production data remain prohibited.

## Smallest future Brain seam

The future dependency direction is:

`Brain request builder → configured provider instance → infer(request) → InferenceResult → Brain orchestration`

- a future Brain request builder owns policy-cleared intent and constructs
  `InferenceRequest`;
- a future Brain composition root owns the immutable config, schema validator,
  async client, and one configured provider instance;
- future Brain orchestration invokes `await provider.infer(request)`;
- `InferenceResult` returns only to that Brain orchestration boundary.

Stage 0.7 does not choose or implement a production Brain receiver/orchestrator.
The first adapter implementation can remain standalone behind the abstraction;
the first end-to-end seam is a separately authorized staging test harness.

## Core dependency boundary

Core remains unchanged and stops at the readiness marker
`AIOS_BRAIN_BOUNDARY`. Core must not import the provider abstraction, Ollama
adapter, schema validator, Brain implementation, or provider configuration.
The adapter must not import Core. No Core-to-Brain runtime call is introduced.

## Dependencies and resources

No new package is necessary: the repository already pins `httpx==0.28.1`,
which provides bounded asynchronous HTTP. Any new schema-validation dependency
requires separate explicit governance approval; the first approved static
schema validator may be implemented without adding one if the implementation
approval proves exact conformance behavior.

Adapter overhead should be negligible relative to the model runtime. It does
not change the existing `3 GiB` runtime RAM, `1 vCPU`, concurrency `1`, one
loaded model, disk, or timeout ceilings. It must not introduce queues,
parallelism, background workers, or model lifecycle processes.

## Rollback and architecture impact

Future repository changes must be confined to independently reversible Brain
adapter/config/validator and test paths named by implementation approval.
Rollback removes those repository additions; it requires no database rollback
and does not modify or remove the separate staging runtime/model.

`ARCHITECTURE CHANGE REQUIRED = NO`

The evaluated design realizes the provider-adapter seam explicitly reserved by
Stages 0.4–0.6.4 inside the existing Brain architecture.
