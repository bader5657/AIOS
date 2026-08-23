# Exact Edge, Default-Deny Boundary, and Verification

## Sole exception

Permit only this source-to-target edge:

`core/core_to_brain_mapper.py → core.brain.input_contracts`

The permitted imported symbols are exactly:

- `BRAIN_INPUT_SCHEMA_VERSION`;
- `BrainInput`; and
- `BrainIntent`.

If the audit can enforce only module-edge granularity, its exception must still
name the exact source file and exact target module. The focused mapper audit
must enforce the exact symbol set. No wildcard, package-wide, `core/*`, or
`core.brain.*` permission is authorized.

## Boundary meaning and retained protections

This is not an ordinary reverse runtime dependency. `CoreToBrainMapper` is the
explicitly approved neutral integration boundary whose sole Brain dependency
is the immutable semantic input contract it constructs.

Default-deny remains intact. The audit must continue rejecting AIOSCore,
Domain, and arbitrary Core modules importing Brain; any import of receiver,
invoker, provider, adapter, orchestration, runtime/configuration, Memory, or
Specialist code; and provider/runtime leakage or reverse runtime dependencies.
Future Core-to-Brain imports require separate governance.

AIOS_BRAIN_BOUNDARY meaning and architecture remain unchanged. Mapper behavior
must not change to accommodate the former audit rule: exact eligibility,
correlation preservation, one UUIDv4 request ID, static STRUCTURED_INFERENCE,
BrainInput construction, and zero downstream inference remain frozen.

## Required verification after activation

On the same implementation branch, modify only the newly authorized policy
test as required, then rerun the focused mapper, BrainInput, receiver, invoker,
adapter, inference-contract, Core, Domain, Stage 8, Stage 9, and full repository
suites; compile/static, dependency/import, and prohibited-source audits;
`git diff --check`; and the exact three-path closed-world audit. Zero unresolved
failures are required before publication.

Rollback of the expansion reverts only the eventual change to
`tests/unit/brain/test_inference_contracts.py`. It requires no runtime, VPS,
database, or service rollback.
