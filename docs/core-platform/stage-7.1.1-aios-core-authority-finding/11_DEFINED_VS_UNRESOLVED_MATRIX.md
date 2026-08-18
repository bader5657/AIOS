# Defined-versus-Unresolved Matrix

| Concern | Active authority | Current runtime | Historical evidence | Status |
|---|---|---|---|---|
| Boundary position | Event Engine → Core → Brain boundary | absent | no conforming Core | DEFINED |
| Route ownership | AIOS Core | absent | command router is not Core | DEFINED |
| Route meaning | bounded responsibility/handoff only | absent | conflicting semantics | PARTIALLY DEFINED |
| Event Engine input | bounded event-delivery disposition; concrete value unspecified | absent | none | PARTIALLY DEFINED |
| Brain-facing output | bounded downstream disposition; concrete value unspecified | absent | none | PARTIALLY DEFINED |
| Runtime API | none | absent | non-authoritative APIs | UNRESOLVED |
| Input DTO | none | absent | none | UNRESOLVED |
| Output DTO | none | absent | none | UNRESOLVED |
| Valid/invalid behavior | none | absent | none | UNRESOLVED |
| Success/failure behavior | only downstream success not claimed after failure | absent | none | PARTIALLY DEFINED |
| Sync/async | none for Core | absent | irrelevant | UNRESOLVED |
| Dependency direction | bounded handoff and reverse-owner prohibitions | absent | conflicting | PARTIALLY DEFINED |
| Runtime state | none | absent | conversation state is unrelated | UNRESOLVED |
| Persistence | no authority | absent | conversation persistence unrelated | PROHIBITED |
| Retry | no authority | absent | none accepted | PROHIBITED |
| Memory | Brain-layer later work | absent | none accepted | LATER-STAGE |
| Specialist Router | explicitly not Route | absent | historical registry/router | LATER-STAGE |
| Brain relationship | downstream boundary only | absent | none authoritative | PARTIALLY DEFINED |
| Business-domain relationship | excluded | absent | historical specialist domain | PROHIBITED |
