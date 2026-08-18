# Stage 3.4.2 Schema and Runtime Conformance

| Verification | Result |
|---|---|
| Normative schema is valid Draft 2020-12 JSON Schema | **PASS** |
| Root is a closed object with explicit properties and required fields | **PASS** |
| `additionalProperties: false` rejects unknown fields | **PASS** |
| Runtime outputs validate against the normative schema | **PASS** |
| Exactly ten represented input classes are admitted | **PASS** |
| `manifest` is rejected as a represented media type | **PASS** |
| File-backed classes require path, exact size, and exact-byte SHA-256 | **PASS** |
| Non-file Text omits file-backed properties | **PASS** |
| Web Link and YouTube Link preserve exact `source_url` | **PASS** |
| Bounded successful Stage 3.3 metadata is preserved | **PASS** |
| Manifest performs no metadata re-extraction | **PASS** |
| UTC RFC 3339 timestamps are enforced | **PASS** |
| UTF-8 JSON round trip preserves approved primitives and meaning | **PASS** |
| No binary content is embedded | **PASS** |

The canonical runtime concept remains `Document Manifest`; `Manifest` is
shorthand only under the active Stage 3.4.1 authority and is not a media type.
No new contract or metadata field is introduced by this verification record.
