# Failure and Rollback Ownership Audit

The Active transaction authority begins only at the future PostgreSQL Registry
persistence boundary and does not span Storage, Metadata, or Document Manifest.

| Failure/rollback condition | Required boundary | Result |
|---|---|---|
| Registry rollback deletes original | Prohibited | PASS |
| Registry error modifies or relocates original | Prohibited | PASS |
| Transaction result changes Storage ownership | Prohibited | PASS |
| PostgreSQL success required for original preservation | Prohibited | PASS |
| Completed Manifest deleted by Registry rollback | Prohibited | PASS |
| Registry row may remain partially successful | Prohibited by atomic transaction design | PASS |

This audit verifies authority/design only. Future implementation must prove
these behaviors with exact implementation evidence.
