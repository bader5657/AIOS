# Runtime Correction and Stop Conditions

No runtime edit is pre-authorized. If the focused test exposes a concrete
authority defect, implementation must stop and report:

`STAGE 8.1.2 RUNTIME CORRECTION APPROVAL REQUIRED`

The report must identify the exact failing authority rule, exact runtime file,
and smallest possible correction scope. Runtime must not be patched under this
test-only approval.

Any unauthorized path, API change, schema/metadata/storage change, Registry
execution, external service, retry, or scope ambiguity is a stop condition.
