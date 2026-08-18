# Historical Registry Evidence Disposition

## Evidence Baseline

Commit `d58c1c341e6a27dd40de63baf004505fcc3094e2` introduced an empty package,
four-field `RegistryRecord`, pass-through `Registry.save()`, and one equality
test. Active Stage 1.2.2 authority disposition is **REJECT** as a PostgreSQL
Registry implementation. No file is restored.

| Historical concept | Classification | Reason/future treatment |
|---|---|---|
| `core/registry/` package location | Premature | Package boundary was never approved; a later implementation may assess location separately |
| `Registry` class name | Compatible evidence only | Resembles permitted shorthand but creates no terminology authority |
| `RegistryRecord` object | Unauthorized | Would imply the unresolved Registry Entry/record representation |
| `id` | Reusable conceptually later | Overlaps identity category; exact field and example `DOC-001` are not approved |
| `media_type` | Reusable conceptually later | Overlaps approved metadata/represented identity; no field contract is adopted |
| `storage_path` | Reusable conceptually later | Overlaps file-location category; exact field is not adopted |
| `manifest_path` | Reusable conceptually later | Overlaps Manifest-reference category; exact field is not adopted |
| Four-field completeness | Obsolete | Omits required responsibility categories relationships and status and does not carry general metadata |
| `save()` pass-through | Obsolete | Performs no registration or persistence |
| Equality-only unit test | Obsolete | Proves only pass-through identity, not Registry behavior |
| Absence of original binary | Compatible evidence | Does not contradict the binary exclusion but is insufficient by itself |
| PostgreSQL/schema/transaction absence | Compatible with governance-only scope, incompatible with claimed historical implementation | Confirms the historical component was not PostgreSQL Registry runtime |

Historical names may be reconsidered only under later explicit authority. This
package accepts none as a runtime, schema, object, or API contract.
