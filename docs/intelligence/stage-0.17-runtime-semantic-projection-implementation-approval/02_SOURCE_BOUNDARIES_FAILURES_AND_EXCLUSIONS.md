# Source Boundaries, Failures, and Exclusions

The pure function is independent of Telegram, RequestContext, and InputType.
Future runtime eligibility is restricted to the application-owned
`RequestContext.text` snapshot when `recognized_input_type is InputType.TEXT`.
That check belongs to a later governed activation layer and is not implemented
under Stage 0.17 authority.

Stage 0.17 v1 excludes image captions, image, voice, audio, video, PDF,
DOC/DOCX, spreadsheet, web-link, YouTube-link, URL-classified text, OCR, and
other extracted content.

The projection contains no Telegram identity or SDK object, transport state,
file path, provenance/reference, asset/Manifest/Registry identity, correlation
ID, business field, provider/model configuration, prompt/instruction, timeout,
output-schema reference, route state, secret/configuration enrichment, or
arbitrary extension field.

The function performs no environment/config lookup, heuristic secret scanning,
database or Registry access, filesystem or network I/O, Memory retrieval,
provider call, logging, persistence, Specialist routing, Mapper/Receiver call,
correlation or request-ID generation, or business action.

Wrong source type raises `TypeError`. Empty, whitespace-only, oversized,
forbidden-control, or otherwise contract-invalid text raises `ValueError`.
There is no provider FailureCode and no unnecessary exception rewriting.

The returned fresh dictionary is intentionally mutable as a local value;
BrainInput remains authoritative for recursive immutable snapshotting during a
future separately authorized continuation.
