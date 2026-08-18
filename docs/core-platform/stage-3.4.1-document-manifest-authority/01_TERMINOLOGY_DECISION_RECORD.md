# Stage 3.4.1 Terminology Decision Record

## Decision

`Document Manifest` is the canonical concept and domain-object name.
`Manifest` is an allowed shorthand or alias only in lifecycle notation and
engineering conversation. The two terms must never identify separate domain
objects, schemas, stores, lifecycle artifacts, or semantic contracts.

There must be no semantic divergence between the canonical term and its alias.
Where normative text could be ambiguous, `Document Manifest` is used.

## Classification Boundary

Document Manifest is a downstream artifact representing an approved input after
successful metadata extraction. It is not an input/media type. The value
`media_type = manifest` is prohibited. A storage-class key or directory label
named `manifest` is only a storage routing label and does not make Manifest a
media type.

## Lifecycle Meaning

The existing lifecycle wording remains valid:

```text
Store Original → Extract Metadata → Create Manifest → Register
```

In this shorthand, `Create Manifest` means creation of exactly one conforming
Document Manifest artifact. It does not authorize Registry behavior.

## Consequences

- Code may retain an engineering identifier containing `manifest` when it
  denotes the canonical Document Manifest concept.
- No mapping, adapter, compatibility object, or second schema may create a
  distinct `Manifest` semantic type.
- Input recognition and Stage 3.3.1 metadata extraction must reject Manifest as
  a media type.
