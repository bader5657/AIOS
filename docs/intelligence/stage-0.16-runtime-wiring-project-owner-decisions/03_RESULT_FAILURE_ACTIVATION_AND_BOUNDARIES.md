# Result, Failure, Activation, and Boundaries

## Result destination and meaning

The first wiring returns the exact `InferenceResult` unchanged to the
application/orchestration caller that initiated the continuation. No result DTO
is added. The caller may observe the object only. Success means bounded
inference success under the existing inference contract; it does not mean
business success, workflow completion, acknowledgement, or authorization to
act.

Mapper and receiver `TypeError`/`ValueError`, failed `InferenceResult`,
unexpected exceptions, and cancellation preserve their existing identities and
propagation. They are not collapsed, translated, retried, or converted to
fallback/success.

No Telegram response, persistence, Registry update, transaction, inventory
change, business action, logging of content, Memory, Specialist routing, or
provider/runtime lifecycle is authorized.

## Activation model

| Level | Decision |
|---|---|
| A — inactive repository wiring | `ELIGIBLE FOR A FRESH IMPLEMENTATION-APPROVAL EVALUATION`; injected fakes and synthetic semantics only |
| B — controlled staging | separate future authority; requires schema binding, staging composition, isolated Ollama/Qwen, synthetic data, and safety gates |
| C — production | `PROHIBITED` |

Production schema binding and a production composition root are activation
prerequisites, not Level A implementation prerequisites. Level A supplies no
production receiver/provider assembly and performs no inference. Real
Telegram/user/business semantic inference remains unauthorized at every level
until separately approved.
