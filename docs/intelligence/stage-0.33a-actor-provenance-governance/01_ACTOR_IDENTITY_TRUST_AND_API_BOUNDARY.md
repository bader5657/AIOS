# Actor Identity, Trust, and API Boundary

## Canonical actor reference

Exactly one actor-reference form is accepted in v1:

```text
operator:550e8400-e29b-41d4-a716-446655440000
```

An accepted value must have all of these properties:

- the exact ASCII prefix `operator:`;
- a canonical, hyphenated UUID textual representation;
- lowercase UUID characters only; and
- UUID version 4.

The initial permitted actor-class set is exactly `{operator}`. Values using `reviewer:`, `system:`, `automation:`, `telegram:`, `admin:`, `migration:`, or `unknown:` are rejected. Uppercase UUID text, non-v4 UUIDs, malformed UUIDs, alternate UUID spellings, and any other actor prefix are rejected.

This actor-class and representation rule is operation-specific to candidate creation. Stage 0.33A does not globally narrow or redefine the existing generic `ActorContext` contract. Generic `ActorContext` may continue to accept its already-governed broader grammar, including legitimate `operator:<id>` and `reviewer:<id>` values used by other operations.

The required validation sequence is conceptually:

```text
validate_actor_context(...)
→ generic ActorContext structural/trust validation

authorize_candidate_creation_actor(...)
→ Stage 0.33A operator/canonical-lowercase-UUIDv4 policy
```

Other `ActorContext` consumers remain unaffected unless separately governed.

The actor reference is non-secret identity metadata. It must never contain or persist a password, API token, Telegram bot token, session secret, database credential, or DSN.

## Trusted identity source

Actor identity comes only from an authenticated, trusted AIOS application identity boundary. The boundary produces an authenticated operator `ActorContext`; downstream candidate creation consumes that context and revalidates it.

None of the following may directly assert, supply, derive, override, or become creator authority:

- Telegram message content or captions;
- Telegram sender-supplied fields or arbitrary Telegram metadata;
- documents;
- OCR, Vision, LLM, or Brain output;
- supplier information;
- `IngestionResult` metadata;
- `TrustedReceiptFacts`;
- arbitrary dictionaries or JSON; or
- database login identity.

Future Telegram usage requires a separately governed chain:

```text
Telegram sender identity
→ trusted AIOS identity resolver
→ authenticated operator ActorContext
```

Stage 0.33A neither designs nor implements that resolver. A Telegram sender ID cannot directly become an actor reference.

## Frozen conceptual API

The future conceptual API is:

```python
create_review_candidate_from_ingestion(
    ingestion_result,
    trusted_receipt_facts,
    actor_context: ActorContext,
)
```

`ActorContext` remains a distinct argument and trust object. It must not be embedded in, accepted from, or conflated with `IngestionResult` or `TrustedReceiptFacts`. No public raw actor-string parameter is authorized.

Every governed candidate-creation boundary accepting an `ActorContext` must first revalidate its current generic structural/trust state and then apply the separate candidate-creation authorization policy. Construction-time validation alone is insufficient: forged dataclass/object state, mutation, reconstruction, deserialization, and subclassing must not bypass validation. Where the governed DTO policy requires exact types, subclassed or otherwise forged DTOs are rejected.

The candidate-specific policy distinguishes:

- `ACTOR_REQUIRED`: no `ActorContext` or actor identity was supplied where candidate creation requires one;
- `ACTOR_INVALID`: an actor input/object exists but fails generic structural/trust validity, including a forged or corrupted object, malformed or prohibited-shaped identity, invalid generic representation, or invalid exact DTO type where required;
- `ACTOR_UNAUTHORIZED`: a structurally valid, trusted generic `ActorContext` is not permitted by the candidate-creation policy; and
- authorized: exactly `operator:<canonical-lowercase-uuidv4>`.

Thus a generic-valid `reviewer:<id>` and a generic-valid legacy `operator:<non-UUID-id>` both deterministically produce `ACTOR_UNAUTHORIZED` for candidate creation. Neither becomes `ACTOR_INVALID` merely because it fails the narrower candidate policy. This operation-specific taxonomy does not redefine errors for unrelated generic `ActorContext` consumers.

The deterministic evaluation order is:

1. actor presence: missing produces `ACTOR_REQUIRED`;
2. generic `ActorContext` structural/trust revalidation: failure produces `ACTOR_INVALID`;
3. candidate-specific authorization: a generic-valid but candidate-disallowed actor produces `ACTOR_UNAUTHORIZED`; and
4. only an authorized candidate actor proceeds to mapper and candidate creation.

All three bounded actor failures occur before candidate persistence and must produce zero unauthorized database mutation. The Migration 0005 PostgreSQL `CHECK` validates the persisted candidate actor format; it does not determine the public application error taxonomy. Application/trust boundaries classify failures before database mutation wherever required, and database `CHECK` failures must not all be mapped generically to `ACTOR_UNAUTHORIZED`.
## Validation and bounded errors

Validation must reject, before mapper, capability, or database mutation:

- a missing actor context (`ACTOR_REQUIRED`) or a supplied blank identity (`ACTOR_INVALID`);
- an unknown actor prefix;
- a noncanonical, non-v4, uppercase, or malformed UUID;
- control characters or Unicode lookalikes;
- path-shaped or SQL-shaped values;
- DSN-shaped or credential-shaped values;
- overlength values; and
- forged or subclassed DTOs where the exact-type policy applies.

The frozen bounded actor errors are:

- `ACTOR_REQUIRED`
- `ACTOR_INVALID`
- `ACTOR_UNAUTHORIZED`

Stage 0.32 duplicate behavior continues to use `SOURCE_ACTIVE_RECEIPT_EXISTS`. V1 does not introduce `ACTOR_PROVENANCE_CONFLICT`; that error requires later implementation evidence of a distinct governed state.

Exceptions and logs must not leak credential or authentication internals. Duplicate responses must not disclose the creator of an existing receipt.

## Provenance non-exposure

Stage 0.33A authorizes no public provenance read API. `created_by_actor_reference` must not automatically propagate to:

- Brain inputs or LLM prompts/context;
- Telegram acknowledgements or replies;
- Universal Ingestion results or metadata;
- generic application logging or generic error output;
- duplicate-source responses;
- a generic provenance-query API; or
- a generic repository getter outside an explicitly approved review use case.

Future review or read exposure requires separate governance approval. Creator identity remains unavailable to OCR, Vision, LLM, Brain, Telegram, and Universal Ingestion both as an authority source and as an automatic output.
