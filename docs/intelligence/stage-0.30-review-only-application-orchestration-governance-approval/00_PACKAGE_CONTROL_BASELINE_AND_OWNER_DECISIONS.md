# AIOS Intelligence Stage 0.30 Package Control, Baseline, and Owner Decisions

Date: 2026-08-26 (Asia/Jakarta)

## Baseline

This documentation-only governance package is based on merged and verified PR
#227 at `main` commit `f89e5a5cb7e404147149616d8e832ee2fa378790`.
PR #227 is the implemented candidate/posting repository baseline. The Next
Integration Boundary Evaluation recommended Option B: a narrow,
transport-independent internal business orchestration layer with REVIEW-ONLY
composition.

No application module is implemented by this package. No production system,
database, configuration, service, Telegram behavior, inference path, or
credential is contacted or changed.

## Project Owner decisions

The following decisions are recorded exactly as approved:

1. Review-only application orchestration is APPROVED as the next integration stage.

2. Canonical source identity:
   - manifest reference is the primary source identity
   - Registry record ID may be carried as an optional associated identity
   - source identity must refer to retained ingestion evidence
   - malformed or missing required source identity fails closed

3. Actor context:
   - define a narrow typed/trusted actor-context contract
   - actor context may support review/audit semantics
   - this stage grants NO confirmation authority
   - this stage grants NO posting authority
   - no caller-supplied credential, SQL, DSN, repository, connection, or generic
     execution authority may be carried through actor context

4. Quantity bounds:
   - application-level maximum quantity bounds are DEFERRED in this stage
   - they MUST be explicitly governed before accepting untrusted extraction output
     into candidate creation
   - current exact Decimal and PostgreSQL constraints remain unchanged

5. Confirmation composition is explicitly DEFERRED.

6. Posting composition is explicitly DEFERRED.

7. Existing Telegram integration remains UNCHANGED.

8. Existing Universal Ingestion runtime flow remains UNCHANGED.

9. OCR/Vision/LLM/inference remains OUT OF SCOPE.

10. Production activation, production data population, stock posting, credential
    provisioning, and runtime service changes remain OUT OF SCOPE.

## Approval effect

This package approves the review-only application boundary for a later,
separately authorized implementation PR. It does not itself authorize or
implement that boundary. Confirmation and posting application composition are
not authorized.
