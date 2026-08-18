# Reusable and Prohibited Historical Evidence

## Reusable conceptually only

- Event Engine as an application/infrastructure component separate from
  Domain Foundation.
- Defensive copying/snapshot of consumer lists, if a later handler contract
  exists.
- Registration-order determinism as a question for later authority, not a
  current guarantee.
- Small focused tests as a style cue, not sufficient verification.

## Prohibited from returning

- historical generic `Event` or any competing canonical event model;
- mutable arbitrary payload as an Event Engine-owned semantic record;
- independently generated event identity, name, or timestamp;
- timezone-naive `datetime.utcnow()` occurrence time;
- bypassing or reconstructing `EventEnvelope`;
- built-in `ValueError` as the adopted domain/boundary contract;
- silent unknown-event success by historical default;
- synchronous-only policy, old handler callable API, or handler registry by
  historical inheritance;
- `None` as the assumed bounded Process disposition;
- inferred retry, persistence, broker, delivery, ordering, duplicate,
  idempotency, Brain, Specialist, or business behavior; and
- historical tests as sufficient current verification.
