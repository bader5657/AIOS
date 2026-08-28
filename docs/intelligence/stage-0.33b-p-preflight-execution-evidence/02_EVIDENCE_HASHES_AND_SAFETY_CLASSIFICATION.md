# Stage 0.33B-P Evidence Hashes and Safety Classification

## Immutable provenance values

| Evidence unit | SHA-256 |
|---|---|
| Complete original Codex JSONL source | `0d2ebc28adcdb8b4bab16ec65f9e1fd7627ef3cf5a93ba94d8d1a57fc4a16354` |
| Exact bounded relevant-record set, concatenated in source order | `7143a431691c0fcf8371abd8dbdfc840d92bbe1e1c16a88369bd7dcbf3663dc4` |
| Complete execution stdout from ordinal 1040 | `73c83cd8e22af2b22a6eac2636f06cf003ee00d845c32c0b4f7687bf5fe5b203` |
| Authorized canonical SQL bundle | `64435ab0193ceb454569496f954a9c6788355f035834d7a6b095222b5154d6f3` |
| Retained SQL transport stream | `0e196fc188498bc6b74dc191b33f8b74bbfe96d1ae7f7280c72d93c7fb82dafa` |
| Migration 0005 UP | `7de76e82cb26863cd3c14abc4394cb036936ed0f1c6c64819f03094cf9069293` |
| Migration 0005 DOWN, identity only | `c210305a14399b4826abc46fad75c138bc8e698d9b85380eba893a01c1501b16` |

The bounded relevant-record set comprises ordinals `983`, `984`, `990`, `991`,
`997`, `998`, `1004`, `1005`, `1011`, `1012`, `1018`, `1019`, `1025`, `1026`,
`1034`, `1035`, `1039`, `1040`, `1048`, and `1055` (JSONL lines `984`, `985`,
`991`, `992`, `998`, `999`, `1005`, `1006`, `1012`, `1013`, `1019`, `1020`,
`1026`, `1027`, `1035`, `1036`, `1040`, `1041`, `1049`, and `1056`).

The relevant-record-set hash is over the complete original JSONL bytes of those
records, including their terminating newlines, concatenated in ascending source
order. The stdout hash is over the UTF-8 bytes of the ordinal `1040` `stdout`
field after JSON decoding.

## Secret-safe publication decision

The original 9 MB session is not suitable for wholesale repository publication
because it includes unrelated session context. It remains hashable provenance.
This package exposes only bounded identifiers, hashes, non-secret command
identity, safe catalog/fingerprint results, counts, and safety classification.
It publishes no password, token, private key, credential-bearing DSN,
`DATABASE_URL`, `runtime.env` content, Telegram secret, or raw business row.

The successful execution's own retained secret scan passed, stdout contained no
raw business rows, and stderr was explicitly empty. Evidence extraction is
therefore **SAFE AS BOUNDED ABOVE**; the complete JSONL must remain uncommitted.

## Governance disposition

Evidence quality: **A. ORIGINAL EXECUTION EVIDENCE — SUFFICIENT**.

The original source provides actual execution/tool records, unambiguous session
correlation, actual production outputs, timestamps/order, exit/result state,
and a complete-file hash. No production rerun is required for evidence recovery.
This package requires independent forensic/governance review and merge before a
new Stage 0.33B-A publication may bind to it.

PR #247 authority remains consumed. Stage 0.33B-A is not published here.
Migration 0005 execution, Migration 0005 DOWN, retry, production activation,
and runtime/integration changes remain unauthorized.

## Evidence-retention technical debt

Every future production preflight, deployment, and post-verification session
must create its immutable, secret-safe evidence manifest during execution—not
afterward. It must retain session identity, timestamp, source/main commit,
authority identity, query/artifact hashes, exact command identity, bounded
stdout/result manifest, final classification, and evidence SHA before the
governed session completes.

## Recovery-audit production safety

| Control | Result |
|---|---|
| Production PostgreSQL contacted | NO |
| Production SELECT | NO |
| Production mutation | NONE |
| Migration 0005 / Migration 0004 | NOT EXECUTED |
| Ownership / roles / grants | UNCHANGED |
| `runtime.env` / service | UNCHANGED |
| Telegram / Universal Ingestion | UNCHANGED |
| Candidate activation | NO |
