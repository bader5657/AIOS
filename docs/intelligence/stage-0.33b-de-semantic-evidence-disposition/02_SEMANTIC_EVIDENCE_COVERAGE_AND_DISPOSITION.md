# Stage 0.33B-DE Semantic Evidence Coverage and Disposition

Date: 2026-08-29 (Asia/Jakarta)

## Classification key

- **A** — complete semantic payload retained.
- **B** — only PASS, frame, process, or status retained.
- **C** — no relevant retained evidence.
- **D** — not applicable.

A is never inferred from PASS. No governed ID qualifies as A.

## Finalized evidence coverage matrix

| IDs | Class | Durable content | Payload required for independent proof but absent |
|---|---|---|---|
| T01-T07 | B | One grouped `T01-T07` frame PASS plus transaction completion | Exact transaction/control execution attribution; no separate T01-T07 records |
| L01-L04 | B | One frame PASS per lock section | Exact successful lock statement attribution beyond frame/status |
| I01 | B | Frame PASS | One observed 4-field database/user/schema/version tuple |
| I02 | B | Frame PASS | One observed 7-field database/schema/relation identity and owner tuple |
| M01-M02 | B | Frame PASS | Zero observed data records for each query plus its matching frame |
| S01 | B | Frame PASS | One observed 7-field index metadata tuple: name, valid, ready, unique, key count, first-key definition, predicate |
| Z01 | B | Frame PASS | Observed one-field `COUNT(*)` result |
| F01-F04 | B | Frame PASS | Each observed 2-field row-count/digest tuple |
| O01 | B | Frame PASS | Complete ordered 6-field column metadata tuple list |
| O02 | B | Frame PASS | Complete ordered 4-field constraint tuple list |
| O03 | B | Frame PASS | Complete ordered 7-field index tuple list |
| O04-O05 | B | Frame PASS | Complete ordered 3-field owner/ACL and trigger tuple lists |
| O06 | B | Frame PASS | Complete ordered 5-field trigger-function tuple list, preserving multiline CSV fields |
| O07-O08 | B | Frame PASS | Complete ordered 3-field schema/ACL and extension tuple lists |
| R01 | B | Frame PASS | Complete ordered 8-field role-attribute tuple list |
| R02 | B | Frame PASS | Complete ordered 3-field membership tuple list |
| R03 | B | Frame PASS | Complete ordered 5-field table-privilege tuple list |
| R04 | B | Frame PASS | Complete ordered 6-field column-privilege tuple list |
| X01 | B | Frame PASS; assembled/Migration hashes and later commit retained | Migration execution/result boundary has status only; hash identity is not a semantic result tuple |
| V01 | B | Frame PASS | One observed 4-field creator-column structural tuple |
| V02 | B | Frame PASS | One observed 3-field creator-CHECK tuple |
| V03 | B | Frame PASS | Zero observed 2-field index records plus matching frame |
| V04 | B | Frame PASS | One observed 7-field preserved-index tuple |
| V05 | B | Frame PASS | One observed 6-field creator-column privilege tuple |
| PF01-PF04 | B | Frame PASS | Each observed 2-field post-UP row-count/digest tuple |
| PO01-PO08 | B | Frame PASS | Complete ordered post-UP tuple lists with the same respective 6/4/7/3/3/5/3/3 widths |
| PR01-PR04 | B | Frame PASS | Complete ordered post-UP role tuple lists with respective 8/3/5/6 widths |
| C01 | B | Exit zero, 49 frames, manifest transaction outcome `COMMITTED` | Commit/process completion is retained; no C01-specific frame exists by contract |

## Exact comparison evidence required

Independent replay required the original ordered tuples, not governance
expectations. It would have compared each PF tuple byte-for-byte with F; PO03-08
with O03-08; PR01-03 with R01-03; and applied the reviewed exact one-row deltas
to O01/PO01 and O02/PO02 and exact five-row delta to R04/PR04. V01, V02, and V05
would cross-check those deltas. Field count, row cardinality, ordering,
multiplicity, UTF-8/CSV decoding, NULL treatment, definitions, and every field
had to remain available. None of those observed inputs was retained.

Expected values and disposable-validation examples in PR #251 are
`EXPECTED_GOVERNANCE_VALUE`, not production observations. Recreating tuples
from them would be `POST_HOC_RECONSTRUCTION` and is prohibited.

## Replay conclusions

Frame replay from original stdout is **not possible** because the original
stdout bytes were not retained. The finalized frame-status sequence reports 49
unique sections in the expected order, but that is an executor record, not a
reparse of original CSV.

Semantic offline replay is **not possible**. Therefore I01/I02, M01/M02, S01,
Z01, F/PF, O/PO, R/PR, V01-V05, and the exact-delta comparison are all
**NOT ESTABLISHED FROM RETAINED SEMANTIC PAYLOAD**. Gaps are not backfilled.

## Governance disposition

Supplemental evidence quality is **C — ORIGINAL SEMANTIC PAYLOAD NOT
RETAINED**. The historical execution evidence is permanently incomplete. This
package records no recovered semantic artifact and does not append to or amend
the finalized evidence.

Stage 0.33B-D disposition:

> MIGRATION COMMITTED — EXECUTION SEMANTIC PAYLOAD NOT RETAINED — STAGE
> 0.33B-D EVIDENCE DEFECT PERMANENT

The next official action is independent governance review of this permanent
defect, followed only by separately authorized Stage 0.33B-V read-only
current-state verification. Stage 0.33B-D must not be upgraded to full evidence
PASS from the available record. The actor-provenance operational gate remains
OPEN and production candidate activation remains NOT AUTHORIZED.

## Terminal statement

STAGE 0.33B-DE PERMANENT EXECUTION-EVIDENCE DEFECT RECORDED
— MIGRATION 0005 REMAINS COMMITTED
— ONE-SHOT AUTHORITY REMAINS CONSUMED
— NO RERUN OR DOWN PERMITTED
— MISSING HISTORICAL SEMANTIC PAYLOAD WILL NOT BE FABRICATED
— READY FOR GOVERNANCE REVIEW AND SEPARATE STAGE 0.33B-V AUTHORIZATION
— PRODUCTION CANDIDATE ACTIVATION NOT AUTHORIZED
