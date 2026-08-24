# Function, Normalization, and Bounds Contract

Implement exactly one public function in
`core/ingestion/semantic_projection.py`:

`project_text_semantics(text: str) -> dict[str, object]`

The function accepts one string and returns a fresh normal dictionary with
exactly `{"text": normalized_text}`. There is no DTO, optional configuration,
extension mapping, runtime state, or context object. Non-string values are not
coerced and raise `TypeError`.

The exact normalization order is:

1. replace CRLF with LF;
2. replace remaining CR with LF;
3. trim leading and trailing whitespace once; and
4. perform no other normalization.

After normalization, empty or whitespace-only content raises `ValueError`.
The text must contain at most 4,096 Unicode code points and at most 16,384 UTF-8
bytes. Both limits are inclusive and neither permits truncation.

TAB and LF are allowed. Every other ASCII C0 control from U+0000 through
U+001F and DEL U+007F raises `ValueError`; controls are never silently removed.
CR cannot remain after the ordered line-ending conversion.

All other Unicode code points are preserved exactly. There is no NFC/NFKC,
transliteration, case folding, whitespace collapse, summarization, prompt or
markdown transformation, URL normalization, or semantic rewriting.
