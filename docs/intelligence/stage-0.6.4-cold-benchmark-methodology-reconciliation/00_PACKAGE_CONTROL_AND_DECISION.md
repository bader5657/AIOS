# AIOS Intelligence Stage 0.6.4 — Cold Benchmark Methodology Reconciliation

| Control | Decision |
|---|---|
| Work type | `GOVERNANCE / METHODOLOGY RECONCILIATION` |
| Prior benchmark state | `GOVERNANCE HOLD / UNCLASSIFIED` |
| First cold execution | retained as `CONTAINED_INVALID_RESULT` |
| Rerun authority | exactly one corrected cold rerun |
| Warm authority | `NONE` in this activation |
| Production authority | `NONE` |

The first cold request completed at the runtime and HTTP layers in `5953 ms`
but returned `{"category":"normal","confidence":100}`. The validator
correctly rejected `confidence=100` against the numeric `0.0` through `1.0`
contract. The value must not be coerced, repaired, or reinterpreted as `1.0`.

The first cold request and its raw evidence are permanent. This package does
not erase, replace, or reclassify that observation as valid.

The Project Owner approves one methodology correction: the natural-language
prompt may explicitly state the confidence scale already enforced by the
schema. Runtime, model, synthetic record, schema, deterministic settings,
concurrency, resource ceilings, and failure controls remain fixed.

This package reconciles the execution contract used by the first cold request
(`normal | warning`) with the earlier package text that described
`below | at_or_above`. For this benchmark record and its single corrected
rerun, the controlling schema is the unchanged schema actually used and
validated during the first cold execution: category `normal | warning`,
confidence numeric `0.0..1.0`, and no additional properties. This is an
authority correction; it does not permit changing the rerun schema.

`STAGE 0.6.4 ONE COLD RERUN APPROVED — SAFETY-GATED ACTIVATION`
