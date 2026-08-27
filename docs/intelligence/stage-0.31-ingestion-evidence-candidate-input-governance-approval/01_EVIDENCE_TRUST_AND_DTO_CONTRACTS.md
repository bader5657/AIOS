# Evidence, Trust, and DTO Contracts

## Ingestion evidence handoff

Stage 0.31A governs an internal evidence handoff/factory that consumes the
current exact `IngestionResult` contract in an offline/application-layer manner.
It must accept only a valid current `IngestionResult`, revalidate exact DTO type
and current values at every public boundary, and fail closed for forged Python
instances, subclasses, incomplete state, or state altered through
`object.__setattr__`.

The handoff must establish all of the following before producing evidence:

- the ingestion result represents successful canonical-manifest creation and
  retention;
- `manifest_path` is present, non-empty, canonical, and satisfies the existing
  Stage 0.30 `SourceContext` invariants;
- `registry_record_id` is carried only when registration actually succeeded;
- registration failure or non-success cannot carry a Registry ID;
- registration success cannot be represented without its valid positive
  Registry ID;
- successful manifest retention with no successful Registry registration is
  valid and carries no Registry ID;
- no caller may substitute an arbitrary source reference.

The resulting evidence context reuses the canonical Stage 0.30 `SourceContext`
contract; no second source-path grammar is authorized. It contains only the
canonical manifest reference and optional corroborating Registry record ID. It
must contain no arbitrary metadata dictionary, Telegram object, text/caption,
document binary, OCR text, Vision result, Brain result, credential, repository,
connection, SQL, or DSN.

## Strong retained-manifest verification

The verifier must use `SourceContext` canonical pathname invariants and the
existing Document Manifest reader/parser and `validate_manifest` contract. It
must not invent or fork the manifest grammar. Verification requires:

1. The path is the canonical absolute manifest path under the established
   manifest root and has the canonical lowercase UUID `.json` filename.
2. The target exists.
3. The target itself is a regular file.
4. The target is not a symlink; symlinks are rejected even when their targets
   are regular files.
5. Existing JSON reading/parsing and manifest validation complete successfully.
6. The validated manifest's `manifest_id` equals the UUID encoded in the
   canonical filename exactly.

The verifier fails closed for a nonexistent or invented manifest, malformed or
invalid JSON, schema validation failure, filename/content UUID mismatch,
symlink, broken symlink, directory, FIFO, socket, device, alternate root,
traversal, or noncanonical UUID path. No arbitrary filesystem-read API is
exposed.

## Trust classification

Authorized receipt fact sources in Stage 0.31A are limited to explicitly
trusted structured/operator-supplied facts and deterministic offline test data.

The following are not authorized receipt facts: Telegram caption or text,
Telegram document metadata, Universal Ingestion arbitrary metadata, OCR,
Vision, LLM or Brain results, heuristic parsing, and fuzzy material matching.
Raw transport or extraction values cannot silently cross the trusted boundary.

Any future extraction output is **UNTRUSTED PROPOSAL data**. It cannot become
candidate facts until a separately governed extraction boundary validates it
against all Stage 0.31 limits. OCR, Vision, LLM, and Brain have no receipt-fact
authority under this approval.

## Trusted receipt facts DTO

`TrustedReceiptFacts` must be an immutable, slotted, typed DTO containing only:

- `supplier_name`;
- optional `document_number`;
- optional `document_date`;
- timezone-aware `received_at`;
- an immutable tuple of trusted item facts.

It must not contain `receipt_id`, `source_asset_reference`, manifest path or
identity, or Registry ID. Those values remain application/evidence authority.

## Trusted item facts DTO

The trusted item facts value must be an immutable, slotted, typed DTO containing
only:

- `line_number`;
- optional `candidate_material_description`;
- optional `canonical_display_name`;
- optional `size_description`;
- optional `specification`;
- optional `material_id`;
- `full_colly_count`;
- `qty_per_full_colly`;
- `partial_qty`;
- `total_qty`;
- `unit`.

It must not contain `receipt_item_id`; that identifier is application-generated.
Public boundaries must require exact DTO types and revalidate current fields so
forged instances, subclasses, incomplete state, and post-construction mutation
fail closed before any capability can be used.
