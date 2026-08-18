# Stage 3.4.1 Current Conformance Matrix

## Audit Basis

Assessment is against accepted baseline
`290470b5ba5206ec6d8132e44d7a4872867f2978`. Runtime, schema, and tests are
evidence only; they do not override this authority.

| Contract area | Current evidence | Result | Required future reconciliation |
|---|---|---|---|
| Canonical object | `DocumentManifest` exists in `core/storage/document_manifest.py` | Partial | Preserve one object; align fields and semantics |
| Manifest not media type | Metadata authority/tests reject `manifest`; storage map uses it only as a path class | Pass | Preserve rejection and distinguish storage label |
| Universal identity | Runtime emits `document_id` | Fail | Emit `manifest_id` as opaque creation-boundary identity |
| Represented type | Runtime emits legacy `media_type`; ingestion passes `input_type.value` | Fail | Emit `represented_media_type` using recognized Stage 3.3 identity |
| Received time | Runtime creates UTC aware `datetime.now(timezone.utc).isoformat()` at manifest creation | Partial | Accept/preserve actual received UTC RFC 3339; do not substitute creation time |
| Status | Runtime default is `status = "stored"` | Fail | Emit `manifest_status = "created"` |
| Metadata result | Extraction precedes creation but is not passed to Manifest | Fail | Pass and serialize bounded validated `metadata` without re-extraction |
| File reference | Runtime serializes `storage_path` | Pass for current single-file path | Preserve accepted stored-original reference |
| File size | Runtime derives `path.stat().st_size` | Pass for current single-file path | Validate conditional requiredness |
| SHA-256 | Runtime hashes bytes at `storage_path` | Pass for current single-file path | Prove exact stored-original byte semantics |
| Text applicability | Runtime extracts metadata but never creates Manifest | Fail | Create conforming non-file-backed Manifest after Metadata |
| Web/YouTube applicability | Exact URL reaches metadata; Manifest is never created | Fail | Pass exact `source_url`; create without network activity |
| All file-backed types | Single-file path creates; legacy type loses PDF/DOC/Spreadsheet identity | Partial/Fail | Cover all approved identities using recognized type |
| Multi-original input | Lifecycle deliberately stops at aggregate storage readiness | Not resolved by current runtime | Future implementation must remain within minimum scope; if contract needs another file or design authority, stop for expansion |
| Optional source IDs | Telegram IDs are always required and missing user becomes synthetic `0` | Fail | Make only deterministic available context fields optional; omit unavailable values |
| Unknown fields | Dataclass has a fixed shape, but no normative validator | Partial | Closed schema and runtime validation with unknown rejection |
| JSON UTF-8 | Runtime writes UTF-8 JSON without binary | Pass | Add round-trip/type/schema proof |
| Normative schema | `config/ingestion-manifest.schema.json` is an example instance without `$schema`, object type, properties, required, or policy | Fail | Replace with valid closed normative JSON Schema |
| Storage boundary | Runtime and storage contract use `/opt/aios/data/documents/manifests` | Pass | Reuse boundary; invent no root |
| Lifecycle ordering | Focused tests prove Store → Metadata → Manifest and metadata/storage stop behavior | Pass/Partial | Add Manifest-failure stop-before-Register and partial-artifact safety tests |
| Register | Runtime exposes readiness only and implements no Registry | Pass | Preserve boundary; do not implement Registry |
| Schema-focused tests | No Document Manifest schema/runtime validation suite | Fail | Add focused contract, conditional, rejection, and serialization tests |
| Capability matrix | Recognizes all approved inputs; does not prove Manifest creation for Text/links | Partial | Prove applicability for all ten classes |

## Conformance Conclusion

Current runtime is not conformant to the active Stage 3.4.1 contract and the
current schema file is not normative JSON Schema. These are known implementation
gaps, not blockers to authority activation. They must remain unchanged in this
governance task and require separate implementation approval.
