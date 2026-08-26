# Composition, Capability, Credential, and Integration Boundaries

## Approved future module boundary

Only these proposed modules are eligible for a later implementation authority:

- `core/app/material_receipts/review_use_cases.py`
- `core/app/material_receipts/ports.py`
- `core/app/material_receipts/results.py`
- `core/app/material_receipts/composition.py`

This stage does not authorize `confirmation_use_cases.py`,
`posting_use_cases.py`, or equivalents. Tests may define conceptual
confirmation capability only where necessary to prove separation; no such
capability may be composed or reachable.

## Candidate composition and credential boundary

Concrete candidate repository construction may occur only at the outermost
review composition root. Higher layers receive narrow interfaces. Passwords,
environment mappings, DSNs, Psycopg connections, repository factories, and raw
repositories where a narrower port suffices must never be passed upward.

Importing review composition must perform no database connection. Constructing
review composition without executing a use case must perform no database
mutation. All authorized composition tests must prove a posting repository
construction count of zero.

## Explicit confirmation exclusion

Capability B, CONFIRMATION, is deferred and unauthorized for composition. The
review facade must not expose `confirm_receipt` or any equivalent direct or
indirect capability. Actor context conveys no confirmation authority.

## Explicit posting exclusion

Capability C, POSTING, remains completely uncomposed and unreachable. The review
facade must not expose `post_confirmed_receipt` or any equivalent direct or
indirect capability. Review composition must never instantiate
`InventoryPostingRepository` or load `aios_material_inventory_posting_runtime`
credentials. Actor context conveys no posting authority.

## Brain boundary

Brain/LLM receives no database credential, repository, connection, confirmation
capability, posting capability, repository/service instance, or inference
authority through the review facade. OCR, Vision, LLM, and inference remain out
of scope.

## Telegram boundary

Existing Telegram integration remains unchanged. No behavior under
`core/adapters/telegram` may be rebuilt, modified, or reconfigured in this
stage. The eventual flow remains:

```text
existing Telegram
-> Universal Ingestion
-> retained source evidence
-> future candidate proposal/review integration
```

This package does not authorize that runtime connection.

## Universal Ingestion boundary

Universal Ingestion remains unchanged. Its retained manifest reference, stored
asset reference/path, Registry identity, and request context may inform the
typed source-context design. No candidate persistence is added to Universal
Ingestion, and the application facade must not independently mutate Universal
Ingestion or Registry.

## Production and non-activation boundary

During governance and under this approval:

- Production PostgreSQL contact is prohibited.
- Production mutation and production stock mutation are prohibited.
- Role/grant changes are prohibited.
- `runtime.env` mutation is prohibited.
- Runtime restart or activation is prohibited.
- Telegram mutation is prohibited.
- OCR/Vision/LLM invocation is prohibited.
- Credential creation or rotation is prohibited.
- Production data population and stock posting are prohibited.

Rollback for this package is documentation-only: close the governance PR or
revert its documentation commit. There is no runtime rollback because this
package performs and authorizes no activation.
