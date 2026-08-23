# Test, Regression, Rollback, and Stop Contract

## Focused unit-test contract

The authorized test module must verify at minimum:

- class existence, exact constructor dependency, default/injected factories,
  non-callable rejection, and no construction-time factory call;
- acceptance of the exact eligible route-result tuple and rejection of every
  failed, wrong-target, failure-bearing, inconsistent, or wrong-type case;
- no request-ID generation for ineligible evidence;
- byte-for-byte correlation preservation and natural invalid-ID failure;
- exactly one factory call per eligible attempt, valid UUIDv4 acceptance,
  exact `brain-` plus lowercase 32-hex formatting, invalid output/version
  rejection, distinct IDs for distinct UUIDs, and absence of a caller request-ID
  parameter;
- exact static STRUCTURED_INFERENCE intent with no dynamic/caller intent;
- exact and empty data mapping, immutable snapshot behavior, invalid-data
  rejection, and no enrichment, prompt, instruction, timeout, or schema logic;
- optional/valid/invalid opaque provenance and no dereference;
- exact BrainInput/schema output with no wrapper;
- absence of CoreRouteResult/EventEnvelope/RequestContext embedding and routing
  injection; and
- static absence of receiver, invoker, provider, Ollama/httpx, database,
  Registry, Storage, filesystem/network, persistence, logging, Memory,
  Specialist, business, provider/model selection, and inference capabilities.

More durable cases within the same test path are allowed.

## Regression and verification matrix

Implementation verification must run, without inference:

- focused mapper tests;
- Stage 0.11 BrainInput tests;
- Stage 0.12 receiver tests;
- Stage 0.9 invoker tests;
- Stage 0.7 adapter tests;
- Stage 0.3 inference-contract tests;
- Core and Domain regressions;
- Stage 8 and Stage 9 gates;
- compile/static and dependency/import audits;
- prohibited-source audit;
- `git diff --check`; and
- exact two-path closed-world audit.

## Rollback and stop conditions

Rollback removes only the two authorized repository paths. There is no
runtime, VPS, database, or service rollback.

Stop before implementation or verification proceeds if a third path, contract
definition change, BrainInput/receiver/invoker change, EventEnvelope or
RequestContext input, Stage 8 expansion, dependency addition, database,
Registry, network, wiring, inference, or business semantics becomes necessary.

The later repository/mock integration
`Core boundary evidence → CoreToBrainMapper → BrainInput → BrainSemanticReceiver`
requires separate authority. Live Ollama is not authorized.
