# Historical Conformance Matrix

| Historical concept | Classification | Stage 5.1.2 finding |
|---|---|---|
| `RegistryRecord` | **UNAUTHORIZED** | Concrete record implies the unresolved Registry Entry/representation |
| `id` / identity | **CONFORMS CONCEPTUALLY / EVIDENCE ONLY** | Overlaps identity category; field name, value, and strategy are unapproved |
| `media_type` | **CONFORMS CONCEPTUALLY / EVIDENCE ONLY** | Overlaps represented identity/metadata; exact field is unapproved |
| `storage_path` | **CONFORMS CONCEPTUALLY / EVIDENCE ONLY** | Overlaps file-location category; representation is unapproved |
| `manifest_path` | **CONFORMS CONCEPTUALLY / EVIDENCE ONLY** | Overlaps permitted Manifest reference; representation is unapproved |
| General metadata | **CONFLICTS** | Required responsibility is incomplete |
| Relationships | **CONFLICTS** | Required category is absent |
| Status | **CONFLICTS** | Required category is absent |
| File location | **CONFORMS CONCEPTUALLY / EVIDENCE ONLY** | Names overlap only; no persistence behavior exists |
| `Registry.save()` | **OBSOLETE** | Pass-through performs no registration or persistence |
| PostgreSQL behavior | **CONFLICTS** | Entirely absent from a claimed PostgreSQL Registry implementation |
| CRUD/read/update behavior | **OBSOLETE** | No such behavior exists; pass-through `save` is insufficient |
| Schema assumptions from dataclass | **UNAUTHORIZED** | Runtime dataclass cannot establish database or contract shape |
| Original-binary absence | **CONFORMS CONCEPTUALLY / EVIDENCE ONLY** | Compatible with exclusion but insufficient by itself |
| Equality-only historical test | **OBSOLETE** | Verifies no required Registry behavior |
| Historical package boundary | **PREMATURE** | No approved package/module boundary existed |

Conceptual conformance never promotes a historical field, object, API, path,
or implementation into current authority.
