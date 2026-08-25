# AIOS Intelligence Stage 0.24 — Material Stock Reader Role Approval

| Control | Approved value |
|---|---|
| Approval baseline | `8e273c1ce0c392e4c456b484de9019c6bfdb6314` |
| Production schema | `public.material_stock`; deployed and verified empty |
| Proposed role | `aios_material_stock_reader` |
| Role model | dedicated `LOGIN` role |
| Provisioning during publication | `PROHIBITED` |
| Data population | `PROHIBITED` |
| Retrieval implementation/execution | `PROHIBITED` |
| Inference | `NONE` |

The dedicated `LOGIN` model is selected. The existing application database login
observed during review is broad and unsuitable for governed read-only retrieval.
A `NOLOGIN` privilege role would still require a second, separately governed
dedicated login and membership, adding complexity without reducing privilege for
this single-table use case. The proposed role itself is therefore the future
runtime login and receives no role memberships.

This approval is governance only. It does not create or alter any role, grant or
revoke any privilege, change ownership or default privileges, populate data,
implement retrieval, connect Brain to PostgreSQL, or execute inference.

Future provisioning is single-purpose: allow the dedicated identity to connect
to database `aios`, use schema `public`, and select from exactly
`public.material_stock`. It grants database transport permission only and does
not authorize a business-context request.
