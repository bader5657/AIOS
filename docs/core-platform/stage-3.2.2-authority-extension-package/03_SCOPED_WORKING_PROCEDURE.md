# Stage 3.2.2 Scoped Working Procedure

| Control | Value |
|---|---|
| Lifecycle | **REVIEWED — PASS** |
| Runtime-data policy | Synthetic temporary paths only; production data NO TOUCH |

1. Confirm this entire package is Approved, Published, and Active in accepted
   `main` history.
2. Confirm implementation starts from the package Activation baseline with a
   clean tree and exact ancestry.
3. Modify only the two allowed source and three allowed test files.
4. Preserve the Active Stage 3.2.1 storage implementation unchanged.
5. Implement only deterministic enumeration of all recognized file originals,
   exactly-once Storage requests, the all-success barrier, bounded partial
   failure, and downstream stop. Preserve the existing single-file continuation;
   mixed/multiple success stops at aggregate storage readiness with no new
   output schema or downstream multi-member processing.
6. Use mocks and synthetic temporary data; never access `/opt/aios/data`,
   production services, PostgreSQL, Event Engine, AIOS Core, Brain, Router, or
   Specialists.
7. Run the complete Verification Matrix and changed-file gate.
8. Stop for Project Owner review. Do not deploy, migrate, activate runtime, or
   begin Stage 3.3.
