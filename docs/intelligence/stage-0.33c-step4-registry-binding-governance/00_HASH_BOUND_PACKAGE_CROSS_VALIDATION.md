# Stage 0.33C Step-4 Registry Binding Clarification

## Decision

This clarification resolves `CONTRACT_VERIFICATION_GAP` by adopting
**MODEL B — HASH-BOUND PACKAGE CROSS-VALIDATION** for `registry_record_id`
during filesystem-only Step-4 approved-package installation.

The executor validates the frozen package's internal consistency. It does not
independently re-prove external Registry or PostgreSQL state.

## Exact rule

```text
approval.package_payload.evidence.registry_record_id
==
approved_input.ingestion_result.registry_record_id
```

This equality uses exact JSON equality: no coercion, conversion, normalization,
or aliases.

When `registration_succeeded` is `false`, `registry_record_id` must be `null` in
the approved input and approval evidence. When it is `true`, the value must be a
positive integer within the repository bound and both locations must contain the
same integer.

`register_handoff_ready` is validated according to the Stage-3 contract and
does not imply successful registration.

## Binding and boundary

The equality check is accepted as package-consistency proof only after canonical
approved-input bytes, semantic and transport hashes, canonical approval payload,
package-payload hash, and all relevant bindings have passed.

This does not assert whether an external Registry contains a row. External
Registry truth requires a separate authority and is outside this filesystem-only
installation scope.

Production PostgreSQL contact and writes remain unauthorized. No database secret,
role, grant, or query is introduced.

## Failure and scope

Any equality or registration-state mismatch is `APPROVED_BYTES_INVALID` and
stops before claim. No authority consumption, retry, marker reset, or package
mutation is permitted.

This clarification applies only to Step-4 approved-package installation. It does
not alter later candidate, receipt, Registry, or database validation rules.

The approved package, Project Owner facts, hashes, executor, and PR #278 remain
unchanged. Step 4 remains open and Step 5 remains unauthorized.
