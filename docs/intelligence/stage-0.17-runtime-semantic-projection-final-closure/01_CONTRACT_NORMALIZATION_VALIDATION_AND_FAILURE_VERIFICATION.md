# Contract, Normalization, Validation, and Failure Verification

`core.ingestion.semantic_projection.project_text_semantics` is the sole public
projection function. It accepts one string and returns a newly allocated normal
dictionary containing exactly `{"text": normalized_text}`. It has no DTO,
context, configuration, or mutable result singleton.

The implementation performs exactly two ordered line-ending replacements—CRLF
to LF and remaining CR to LF—followed by one outer `strip()`. It does not
collapse internal whitespace, change case, summarize, transform prompts,
rewrite URL/Markdown content, normalize Unicode, or transliterate.

Non-string input raises TypeError. Normalized empty text raises ValueError. The
inclusive limits are 4,096 Unicode code points and 16,384 UTF-8 bytes, with no
truncation. TAB and LF are allowed; all other ASCII C0 controls and DEL are
rejected without removal.

Four thousand ninety-six four-byte Unicode code points reach exactly 16,384
UTF-8 bytes and pass. Since valid Unicode UTF-8 uses no more than four bytes per
code point, independent byte overflow within the character ceiling is
mathematically impossible. The explicit byte guard remains verified as defense
in depth.

Unicode code points, including multilingual text, emoji, and composed or
combining sequences, remain exact after only the approved line-ending and outer
trim operations. Results are fresh and deterministic.
