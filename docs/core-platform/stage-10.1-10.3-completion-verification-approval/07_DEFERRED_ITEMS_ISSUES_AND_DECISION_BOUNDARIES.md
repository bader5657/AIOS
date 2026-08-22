# Deferred Items, Issues, Rollback, and Decision Boundaries

## Carried deferred-item ledger

No item is silently closed.

| Item | Stage 10 disposition |
|---|---|
| journald contextual Telegram metadata privacy hardening | `RELEASE-REVIEW ITEM`; non-blocking for Core Platform completion under accepted Stage 9 authority unless current audit finds prohibited secret/runtime-data exposure |
| PostgreSQL host UID/GID display observation (`70:70`, mode `0700`) | `NON-BLOCKING FOR CORE PLATFORM COMPLETION`; retain operational observation |
| rollback root mode observation (`0755`) | `RELEASE-REVIEW ITEM`; non-blocking unless current audit disproves the protected rollback boundary |
| document root mode observation (`0775`) | `RELEASE-REVIEW ITEM`; non-blocking unless current audit disproves protected original-file placement |
| predecessor/runtime rollback retention | `RELEASE-REVIEW ITEM`; retain existing evidence, make no retention change here |
| inherited bounded Stage 8 technical debt | `LATER-STAGE / CONTRACT-BOUNDED`; Telegram SDK coupling, accepted out-of-pipeline behavior, bounded cleanup limitation, and non-failing collection warnings remain explicit and non-blocking unless regression evidence contradicts acceptance |

If current evidence shows that any item violates an Included Scope requirement,
its classification becomes `COMPLETION-BLOCKING`; prior non-blocking wording
cannot override current proof.

## Open PR and issue policy

Required Stage 10 gates require zero unresolved blocking checks and zero open
completion/release-blocking issues relevant to the frozen baseline. Historical
or unrelated PRs may remain. Historical PR #1 is not a blocker unless evidence
shows direct relevance to the baseline or an Included Scope requirement.

## Rollback evidence retained

Completion verification must retain and cite:

- accepted source SHA;
- authoritative tracked and effective service artifact;
- service-local rollback boundary;
- protected PostgreSQL/database preservation model; and
- accepted runtime rollback evidence.

No distributed rollback capability is claimed.

## Completion decision boundary

Stage 10.3.1 may occur only after Stage 10.1.1, 10.1.2, 10.2.1, and 10.2.2
each record `PASS` on the exact baseline. The Project Owner then records
exactly `ACCEPTED COMPLETE` or `REJECTED / CORRECTION REQUIRED` for the Core
Platform milestone. This is evidence acceptance, not a release decision.

## Release, version, build, and artifact boundary

- Completion acceptance never implies a release request.
- Release review and release require a later, separate explicit Project Owner
  request and authority for Stage 10.4.
- `VERSION` remains `0.1.0-alpha`; disposition is `UNCHANGED`. Only separate
  Project Owner approval naming an exact value may authorize an edit.
- No authoritative production build number is active and none is created. If
  a build-number requirement is discovered, stop with
  `STAGE 10 BUILD AUTHORITY DECISION REQUIRED`.
- No source archive, checksum package, release artifact, release note, tag, or
  GitHub Release is required or authorized in Stage 10.1–10.3.
