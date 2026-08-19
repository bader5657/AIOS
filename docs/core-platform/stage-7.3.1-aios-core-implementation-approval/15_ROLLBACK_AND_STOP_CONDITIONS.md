# Rollback and Stop Conditions

Implementation must stop and remain unapproved if:

- the EventEnvelope contract or any Domain Foundation path must change;
- any Stage 5 or Stage 6 path must change;
- Brain implementation or Event Engine/Registry runtime dependency is needed;
- another target, failure code, dependency, or fifth path is needed;
- payload/business semantics, state, persistence, retry, broker/network,
  Memory, Specialist Router, or historical runtime appears;
- a mandatory test or regression fails; or
- static, dependency, whitespace, prohibited-source, or closed-world audit
  fails.

No corrective expansion is implicit. A different runtime path or any listed
scope increase requires the exact stop:

`STAGE 7.3.1 SCOPE EXPANSION REQUIRED`
