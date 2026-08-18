# Stage 5.1.1 Comparison

| Active Stage 5.1.1 responsibility | Historical coverage | Finding |
|---|---|---|
| Identity | `id` name only | Partial conceptual evidence; no approved identity semantics |
| Metadata | `media_type` only | Incomplete; no general approved metadata persistence contract |
| Relationships | absent | Missing |
| Status | absent | Missing |
| File location/reference | `storage_path` and `manifest_path` names | Partial conceptual evidence; no approved fields or persistence |
| Original binary excluded | no binary field | Compatible absence; insufficient for implementation conformance |
| Register handoff boundary | absent | No lifecycle integration |
| PostgreSQL intended technology | absent | No PostgreSQL behavior |

Stage 5.1.1 strengthens the prior `REJECT`: it supplies an Active closed
responsibility contract against which the historical component is demonstrably
partial and non-operational. It does not approve the historical object, fields,
package, API, test, or behavior and therefore does not reverse or soften the
component disposition.

Stage 5.1.1 remains unchanged by this reconciliation.
