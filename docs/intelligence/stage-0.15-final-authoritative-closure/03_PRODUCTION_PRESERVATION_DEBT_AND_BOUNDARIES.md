# Production Preservation, Debt, and Boundaries

Production remained outside verification authority and was preserved exactly:

| Control | Pre/post result |
|---|---|
| `/opt/aios-src` SHA | `2c44dc84cb38dc51778f8a65f12a6e59683c74c9` — unchanged |
| `aios.service` MainPID | `15845` — unchanged |
| `NRestarts` | `0` — unchanged |
| `ActiveState` | `active` |
| `SubState` | `running` |
| Runtime/service mutation | `NONE` |
| Live inference | `NONE` |

No Ollama invocation, provider network call, model load, production API call,
service restart, Core runtime wiring, or VPS/runtime mutation occurred.

Stage 0.15 intentionally leaves these debts unresolved and unauthorized:

1. Core-to-Brain runtime wiring;
2. production output-schema resolver/validator binding; and
3. production composition of provider configuration, provider, invoker,
   receiver, and Core handoff.

Memory, Specialist routing, business semantics, and production activation also
remain outside Stage 0.15. None is a blocker to this repository-test closure;
all require separate future authority.
