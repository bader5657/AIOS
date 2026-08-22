# Provider, State, Failure, Security, and Operations Policy

## Provider and cost authority

`PROVIDER STRATEGY = ABSTRACTION + LOCAL-FIRST`

- no hard-coded Ollama or paid remote provider;
- provider/runtime must be replaceable behind one bounded contract;
- local execution is preferred when operationally reasonable;
- this is configuration/contract flexibility, not multi-provider orchestration;
- no provider or runtime is selected in Stage 0.1;
- `OLLAMA = CANDIDATE / DEFERRED / NOT AUTHORIZED FOR INSTALLATION`;
- `PAID_EXTERNAL_AI_API = NOT AUTHORIZED BY DEFAULT`.

Any paid provider requires separate Project Owner approval naming provider,
purpose, budget ceiling, data/privacy treatment, secrets handling, outbound
network policy, and fallback behavior. No credential is authorized here.

## State, persistence, retry, and model selection

- initial inference boundary: `STATELESS PER INVOCATION`;
- transient in-process state: allowed only for one invocation;
- prompt, response, embedding, session, and cross-request-context persistence:
  prohibited by default;
- persistent Memory: separate future Brain capability;
- `INTELLIGENCE RETRY = NONE BY DEFAULT`;
- automatic provider retry: not inherited or inferred;
- bounded retry: requires later Intelligence-specific authority;
- dynamic model selection: not authorized;
- AIOS Core and Specialist Router: not model-selection owners;
- first runtime milestone: one explicitly configured provider/model only;
- future dynamic selection: separate ownership and policy approval required.

## Conceptual failure taxonomy

The following categories are approved for contract evaluation; exact names and
serialization remain provisional until contract approval:

- `INVALID_REQUEST`;
- `RUNTIME_UNAVAILABLE`;
- `TIMEOUT`;
- `PROVIDER_FAILURE`;
- `MALFORMED_OUTPUT`;
- `PARTIAL_OUTPUT`;
- `LOCAL_RUNTIME_FAILURE`.

Default behavior is fail closed, no false success, no automatic retry, and no
downstream tool, Specialist, or business execution.

## Security baseline

Future runtime authority must explicitly address untrusted model output,
prompt injection, secret leakage, outbound network control, model download and
provenance integrity, tool authority, resource exhaustion, data retention, and
contextual user/business-data logging. Tool execution, embeddings, vector DB,
broker/queue, and autonomous action remain unauthorized.

## Observability baseline

Permitted by default after runtime approval:

- provider/runtime identifier;
- approved model identifier;
- correlation ID;
- duration;
- success/failure status; and
- bounded failure code.

Prompts, full model responses, Telegram contents, user/business contents, and
credentials must not be logged by default. The accepted Stage 9 journald
contextual-metadata privacy finding remains open and authoritative.

## VPS and resource policy

Current production class is approximately 2 vCPU / 8 GB RAM. Without model
installation or benchmarking:

- remote provider client: technically feasible but separately governed;
- very small CPU-local model: possible but operationally marginal;
- medium/large CPU-local model: unsuitable;
- multi-model local runtime: unsuitable.

Future runtime approval must state explicit maximum RAM, CPU, disk/model size,
concurrent model instances, startup impact, and interaction with the existing
production service. Values remain deferred; production resources are not
consumed in Stage 0.1.
