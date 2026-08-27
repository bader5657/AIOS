# Test, Debt, Safety, Approval, and Next Action

## Required Stage 0.31A offline tests

A later implementation authorization must require unit and adversarial tests
proving at least:

1. Valid retained evidence plus valid trusted facts maps exactly.
2. Source reference comes only from retained evidence, and trusted facts expose
   no source-reference, manifest, or Registry field.
3. Valid Registry corroboration is preserved.
4. Registration failure/non-success with no Registry ID remains accepted when
   the manifest is retained successfully.
5. Every false registration-success/Registry-ID combination is rejected.
6. Invented and nonexistent manifests are rejected.
7. Invalid JSON, malformed content, and manifest schema failures are rejected.
8. Manifest filename/content UUID mismatch is rejected.
9. Symlinks, broken symlinks, directories, FIFOs, sockets, devices, alternate
   roots, traversal, and noncanonical UUID paths are rejected.
10. Forged evidence, trusted receipt facts, and item DTOs are rejected.
11. DTO subclasses are rejected wherever exact-type policy applies.
12. State forged with direct `object.__setattr__` is rejected at the public
    boundary.
13. Zero items and more than 500 items are rejected.
14. Duplicate line numbers and generated duplicate item IDs are rejected.
15. Non-UUID, non-v4, malformed, or otherwise bad ID-factory output is rejected.
16. Missing, blank, noncanonical, or over-128-character supplier name is
    rejected.
17. Blank, noncanonical, or over-128-character document number is rejected.
18. Blank, noncanonical, or over-512-character descriptive/material fields are
    rejected.
19. Negative quantities and zero total quantity are rejected.
20. Every approved lower and upper bound is tested, including 500 items,
    1,000,000 full colly, 1,000,000 per full colly, 1,000,000,000 partial, and
    1,000,000,000 total, with immediately out-of-bound values rejected.
21. Decimal scale greater than 6 and precision greater than 20 are rejected.
22. Float, NaN, infinity, and non-Decimal quantity values are rejected.
23. No rounding, truncation, quantization, or lossy coercion occurs.
24. Packaging mismatch is rejected.
25. Fractional applicable `sheet` quantities are rejected.
26. Invalid, aliased, or case-changed units are rejected.
27. Timezone-naive `received_at` is rejected.
28. Accepted exact Decimal values are preserved.
29. The resulting `ReceiptCandidateRequest` and its items are immutable.
30. Confirmation and posting APIs are absent and unreachable.
31. Candidate and posting repository construction counts remain zero.
32. Candidate and posting credential loading counts remain zero.
33. Importing and constructing the mapper/evidence boundary has zero side
    effects.

For every invalid input, tests must additionally assert zero repository
construction, database activity, candidate persistence, posting capability, and
confirmation capability.

All tests are offline. They must not contact production PostgreSQL, mutate
production data or stock, change roles/grants or `runtime.env`, restart or
activate a service, mutate Telegram or Universal Ingestion runtime, invoke OCR,
Vision, LLM, or Brain, or create credentials.

## Technical debt disposition

Governance approves the numeric ceilings but closes no technical debt by
itself. The proactive application numeric upper-bound debt becomes CLOSED only
after the separately authorized Stage 0.31A implementation and tests verify all
approved count, magnitude, precision, and scale bounds.

The following remain nonblocking because posting is unreachable:

- simultaneous successful-posting concurrency coverage;
- deeper `ALREADY_POSTED`/current-stock/history reconciliation;
- chained Psycopg traceback/cause hardening.

## Production safety and non-activation

During this governance task and under Stage 0.31A approval:

- Production PostgreSQL contact is prohibited.
- Production data and stock mutation are prohibited.
- Production role/grant mutation is prohibited.
- `runtime.env` mutation is prohibited.
- Runtime service restart or activation is prohibited.
- Telegram mutation is prohibited.
- Universal Ingestion runtime mutation is prohibited.
- OCR, Vision, LLM, and Brain invocation is prohibited.
- Credential creation is prohibited.
- Candidate creation/persistence, confirmation, posting, and movement creation
  are prohibited.

Rollback for this governance package is documentation-only: close the PR or
revert its documentation commit. No runtime rollback exists because this
package performs no runtime or production action.

## Project Owner approval

The Project Owner APPROVES this Stage 0.31 governance boundary and the frozen
decisions, contracts, exclusions, limits, and test requirements recorded across
this package. The approval authorizes no implementation in this governance PR.

## Next official action

1. Review and merge this documentation-only governance PR.
2. Verify the governance merge on a clean, synchronized `main`.
3. Issue a separate, narrow Stage 0.31A implementation authorization for the
   evidence handoff, immutable trusted-fact DTOs, mapper/validation operation,
   strong retained-manifest verification, and required offline tests.
4. Implement Stage 0.31A on a separate branch and PR with persistence,
   confirmation, posting, runtime composition, Telegram changes, and Universal
   Ingestion runtime changes absent and unreachable.
5. Govern Stage 0.31B runtime composition separately and only later.

`INTELLIGENCE STAGE 0.31 GOVERNANCE APPROVED — READY FOR STAGE 0.31A MAPPER/VALIDATION IMPLEMENTATION AUTHORIZATION`
