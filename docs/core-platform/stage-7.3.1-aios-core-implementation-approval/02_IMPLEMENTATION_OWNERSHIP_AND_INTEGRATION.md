# Implementation Ownership and Integration Boundary

Stage 7.3.1 owns only a fresh, contract-first AIOS Core runtime and focused unit
tests. It creates the identifiable Route boundary required by the Execution
Plan and stops at `AIOS_BRAIN_BOUNDARY`.

Integration is **not included**. Execution Plan Stage 8.1.4 separately owns
Event Engine → AIOS Core → downstream-boundary integration. Stage 7.3.2 owns a
non-Intelligence test consumer/boundary fixture only if later needed.

Stage 7.3.1 must not change or wire Universal Ingestion, Registry, Event Engine,
Brain, Memory, Specialist Router, business behavior, or infrastructure.
