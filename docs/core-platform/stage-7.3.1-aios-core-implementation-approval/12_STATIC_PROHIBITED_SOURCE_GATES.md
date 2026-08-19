# Static Prohibited-Source Gates

The later implementation review must inspect all four authorized files and
fail on evidence of:

- imports from `core.event`, `core.registry`, `core.storage`, ingestion,
  pipeline, adapters, Brain, Memory, Router, Specialist, or business packages;
- `EventEngine`, `EventDeliveryResult`, or `EventDeliveryFailureCode`;
- payload/event-name branching, routing maps, whitelists, intent or business
  vocabulary used for decisions;
- `create_task`, `gather`, worker/thread/process, retry/backoff, sleep, random,
  clock-driven routing, mutable module decision state, history, session, cache,
  database, file persistence, socket, HTTP, broker, queue, or external client;
- Brain/model/prompt/LLM/provider invocation or response handling; or
- historical conversation, command-router, specialist-router, orchestration,
  or business-router APIs.

The audit must also positively verify one target enum member, one failure-code
enum member, frozen/slotted four-field result shape, exact bounded reason, and
an async `route` as the sole AIOSCore public method.
