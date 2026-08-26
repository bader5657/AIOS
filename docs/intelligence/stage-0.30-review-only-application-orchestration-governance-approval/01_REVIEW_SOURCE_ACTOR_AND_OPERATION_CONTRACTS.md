# Review, Source, Actor, and Operation Contracts

## Review capability

Capability A, REVIEW, is the only capability eligible for implementation in the
next stage. It is a transport-independent application facade that delegates
only to the approved candidate boundary and exposes exactly:

```text
create_candidate(request, source_context)

revise_candidate(
    request,
    expected_version,
    actor_context
)

get_candidate_for_review(
    receipt_id,
    actor_context
)
```

The facade must not expose a generic repository method, repository getter,
arbitrary query facility, confirmation operation, posting operation, or an
equivalent indirect capability. Its requests must not carry SQL, a DSN,
connection state, environment mappings, credentials, repositories, or generic
execution authority.

## SourceContext contract

`SourceContext` is a typed, immutable DTO containing only the minimum identity
and evidence references needed to bind candidate creation to retained Universal
Ingestion evidence:

- required primary identity: manifest reference;
- optional associated identity: Registry record ID.

The manifest reference must be valid and identify retained ingestion evidence.
Missing or malformed required source identity fails closed. The application
facade does not independently mutate Universal Ingestion or Registry.

`SourceContext` must not contain a document binary, OCR text, arbitrary metadata
dictionary, credential, DSN, SQL, repository, database connection, Brain object,
or Telegram object. A stored asset reference/path and request context remain
owned by the retained Universal Ingestion evidence; this DTO binds by identity
rather than copying those broader records upward.

## ActorContext contract

`ActorContext` is a narrow, typed, trusted, immutable DTO suitable for future
authenticated review actions. It may contain only bounded actor/audit identity.
The exact future authentication mechanism is not authorized by this stage.

It must not contain credentials, passwords, tokens, DSNs, SQL, repositories,
connections, generic execution capability, confirmation authority, or posting
authority. Possession of an `ActorContext` grants neither confirmation nor
posting authority.

## Result and reader boundary

Review results are narrow typed application results for candidate creation,
revision, and retrieval. They must not leak a raw repository, connection,
repository factory, environment mapping, SQL/DSN detail, credential, or a
confirmation/posting service.

Retrieval for review delegates to the approved candidate reader operation only.
It does not broaden the existing separately read-only material-stock reader,
its role, its grants, or any candidate/posting privilege. No generic reader or
repository getter is authorized.

## Quantity decision

Application-level maximum quantity bounds are deferred. Current exact `Decimal`
semantics and PostgreSQL constraints remain unchanged. Application numeric upper
bounds MUST be revisited and explicitly governed before untrusted extraction
output is authorized to create candidates.
