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

Every boundary accepting an `ActorContext` must fail closed and revalidate its exact governed values. Construction-time validation alone is insufficient: forged dataclass/object state, mutation, reconstruction, deserialization, and subclassing must not bypass validation. Where the governed DTO policy requires exact types, subclassed or otherwise forged DTOs are rejected.

## Validation and bounded errors

Validation must reject, before mapper, capability, or database mutation:

- a missing or blank actor;
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
