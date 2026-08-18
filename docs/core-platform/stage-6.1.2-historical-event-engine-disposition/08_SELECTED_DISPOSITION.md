# Selected Disposition

## REPLACE

Exactly one disposition is selected: **REPLACE**.

Decision basis:

- zero substantive historical module implements the active minimal Process
  contract;
- the historical Event model is obsolete and conflicts with canonical
  DomainEvent/EventEnvelope authority;
- the other substantive modules implement handler registration and dispatch,
  which remain unauthorized until Stage 6.2.1;
- silent unknown handling and `None` output do not satisfy the bounded
  success/failure contract; and
- preserving the old API would make a complete rewrite appear to be reuse.

REPLACE does not authorize a replacement implementation now. It closes only
the historical disposition and makes Stage 6.2.1 eligible for its separately
controlled runtime-contract workflow.
