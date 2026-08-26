# Test, Debt, Implementation Authority, and Next Action

## Required offline tests

A later review-only implementation authority must require offline tests proving:

1. The review facade exposes only create, revise, and get-for-review.
2. Confirmation is unreachable.
3. Posting is unreachable.
4. Review composition never constructs `InventoryPostingRepository`.
5. Review composition never loads posting credentials.
6. No generic repository getter exists.
7. No SQL, DSN, connection, or environment mapping enters use-case requests.
8. `SourceContext` requires a valid retained manifest/source identity.
9. Missing or malformed source identity fails closed.
10. `ActorContext` carries only bounded audit identity.
11. Importing review composition performs no database connection.
12. Constructing review composition without executing a use case performs no
    database mutation.
13. Brain and Telegram objects cannot receive repository/service instances
    through the review facade.
14. Existing candidate/posting/reader privilege isolation remains unchanged.
15. Existing candidate/posting tests remain regression gates.

Tests must be offline and must not contact production PostgreSQL, change
production data or stock, modify roles/grants or `runtime.env`, restart or
activate services, mutate Telegram, invoke OCR/Vision/LLM, or create/rotate
credentials.

## Existing regression gates

The PR #227 candidate, posting, reader privilege-isolation, unit, disposable
PostgreSQL integration, and security-boundary tests remain unchanged regression
gates. The future review layer may delegate only to the approved candidate
boundary and must not weaken those contracts.

## Technical debt retained without resolution

- simultaneous successful-posting concurrency coverage;
- deeper `ALREADY_POSTED`/current-stock/history reconciliation;
- proactive application numeric upper bounds;
- chained Psycopg traceback/cause hardening.

Application numeric upper bounds MUST be revisited before untrusted extraction
output is authorized to create candidates.

## Implementation authority boundary

This documentation PR records approval but implements no application code. Only
after this governance PR is reviewed, merged, and its clean merged baseline is
verified may the Project Owner issue a separate implementation authority for
the four enumerated review application modules and their offline tests.

That future authority must not include confirmation or posting use cases,
production activation, production data population, stock posting, credential
provisioning, runtime service changes, Telegram changes, Universal Ingestion
runtime changes, OCR/Vision/LLM/inference, role/grant changes, or `runtime.env`
changes. Path or capability expansion requires new governance.

## Next official action

1. Review and merge this documentation-only governance PR.
2. Verify the governance merge on a clean, synchronized `main`.
3. Issue a separate, narrow implementation authority for REVIEW-only
   application orchestration and the required offline tests.
4. Implement on a separate branch and PR with confirmation and posting still
   uncomposed and unreachable.
5. Perform no production activation.

`AIOS REVIEW-ONLY APPLICATION ORCHESTRATION GOVERNANCE APPROVED — READY FOR IMPLEMENTATION AUTHORIZATION`
