# Project Owner Approval, Activation, and Next Action

I, as Project Owner, authorize repository-only implementation of the Stage
0.17 text semantic projection contract.

The implementation may provide one pure deterministic function that accepts
one application-owned plain-text string, performs only the approved line-ending
normalization and outer trimming, enforces the approved
character/UTF-8/control bounds, and returns exactly:

`{"text": normalized_text}`

Stage 0.17 does not authorize Telegram metadata, provenance duplication,
correlation generation, business fields, secrets/config access, prompt
transformation, database/network/filesystem access, Memory, Specialist routing,
persistence, logging content, runtime wiring, live inference, or Level B
activation.

Only plain-text `InputType.TEXT` runtime content is intended for later
activation.

Activation of this governance package authorizes only a future two-path
repository implementation after normal publication to `main`. It does not
activate the capability in production. Schema binding, composition, and Level B
remain unresolved and unauthorized.

The next official action is to implement exactly the two approved paths, run
the complete non-live verification matrix, and return retained evidence for
final review.
