# Implementation Ownership and Stage Boundary

Stage 6.3.1 owns a fresh, focused Event Engine runtime implementation only. It
supplies the official Process capability using the active Stage 6.2.1 behavior
contract.

Stage 6.3.1 does not own:

- Integration/Application publisher construction;
- Registry output → Event Engine input wiring;
- Stage 5 or PostgreSQL behavior;
- AIOS Core, Brain, Memory, Specialist Router, or business consumers; or
- broker, persistence, retry, deployment, or later Stage 6 work.

Execution Plan Stage 6.3.2 separately owns Registry/publisher → Event Engine
integration. Unit tests in 6.3.1 use test-local async handlers only.
