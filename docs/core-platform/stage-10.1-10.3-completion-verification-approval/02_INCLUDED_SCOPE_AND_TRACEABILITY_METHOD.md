# Included Scope and Requirement Traceability Method

## Authoritative Included Scope

Stage 10.1.1 must enumerate every approved Core Platform requirement from the
Blueprint and the Frozen Execution Plan, including every applicable numbered
item from Stages 0–9. The included capability families are:

| Included family | Controlling requirement |
|---|---|
| Telegram input boundary and supported input classification | Existing interface boundary used by the Core Platform path |
| Universal Ingestion and Request Context | Receive and normalize approved inputs |
| Original-file Storage and Metadata Engine | Store original before processing and extract metadata |
| Document Manifest | Create the authoritative manifest/reference boundary |
| Asset Pipeline | Own the approved storage/metadata/manifest lifecycle |
| PostgreSQL Registry | Persist identity, metadata, relationships, status, and file location; exclude primary original binaries |
| AIOS Event Engine | Process registered pipeline output under accepted event contracts |
| AIOS Core | Route to the bounded downstream/Brain readiness boundary without executing Brain |
| Official lifecycle | `Receive → Store Original → Extract Metadata → Create Manifest → Register → Process → Route → Respond` |
| Dependency direction and failure invariants | Preserve accepted Core boundaries, ownership, transaction, and failure behavior |
| Domain Foundation regressions | Preserve the accepted foundation consumed by Core Platform |
| Operational alignment | Authoritative `aios.service`, reboot activation, one Telegram poller, systemctl/journalctl visibility |
| Source/runtime and protected-data separation | `/opt/aios-src` versus `/opt/aios`; protected runtime categories outside Git |
| Capability documentation | README/CHANGELOG claims remain limited to accepted current capability |

This family table is an anti-omission control, not the Stage 10.1.1 result.
Stage 10.1.1 must expand it into the complete requirement traceability matrix.

## Required matrix columns

Every requirement row must record:

- stable identifier, using the existing authority identifier where one exists
  and a deterministic source/section-derived identifier otherwise;
- source authority and exact requirement text or faithful summary;
- owning stage/sub-stage;
- implementation path(s), or an explicitly justified governance-only
  realization where implementation is genuinely inapplicable;
- test/evidence path(s) and exact accepted evidence;
- accepted closure reference;
- status on the frozen baseline.

The matrix must reconcile against the Execution Plan Stage/Step/Sub-step
counts and the accepted completion/capability matrices. A source requirement
that lacks a stable identifier must be assigned one; it must not be omitted.

## Coverage rule

A requirement is `COVERED` only when authoritative evidence links it to all
three applicable proof classes:

1. implementation, or an explicitly valid governance-only realization;
2. a test or accepted verification evidence; and
3. accepted stage closure.

Architecture intent alone, historical code alone, Roadmap intention alone, or
a documentation claim alone is insufficient. Missing or contradictory proof
is an open row, not a pass. Stage 10.1.1 passes only when every Included Scope
row is covered on the exact baseline and no row is silently omitted.
