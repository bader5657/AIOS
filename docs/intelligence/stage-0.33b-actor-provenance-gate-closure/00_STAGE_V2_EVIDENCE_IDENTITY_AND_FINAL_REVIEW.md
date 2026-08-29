# Stage 0.33B-VC Stage V2 Evidence Identity and Final Review

Date: 2026-08-29 (Asia/Jakarta)

## Corrected evidence identity

The finalized Stage V2 session is
`stage-0.33b-v2-current-state-20260829T105807Z-efabd6cf-836f-4bc7-918e-e31c0535ed64`
under the persistent evidence root
`/opt/aios/runtime/intelligence/production-execution-evidence/stage-0.33b-v`.
Offline recomputation directly from immutable final bytes established:

| Artifact | SHA-256 | Bytes | Records | Owner/group | Mode |
|---|---|---:|---:|---|---:|
| `execution.jsonl` | `9f172f22a6dc540cc16b1c3068c00eec59200b7a008ccfe4456674bd9074d302` | 3452 | 4 | `aiosadmin:aiosadmin` | `0440` |
| `semantic-results.jsonl` | `5dce359d288e3adae0dea397b4b698aa83fd0ae0cc9a01e3149d111b785954e7` | 58268 | 25 | `aiosadmin:aiosadmin` | `0440` |
| `manifest.json` | `0dee70b124132beaa9e7e73964c3cefd8a2e3d79a172e6827f45dbfcea2110f0` | 1243 | n/a | `aiosadmin:aiosadmin` | `0440` |

All three are regular non-symlink files. Their bytes match Stage V2
finalization and remain unchanged. The earlier closure prompt supplied malformed
manifest expectation `0dee70b124132beaa9e7e73964c3cefd8a2e3d79a177e6827f415dbfcea2110f0`, classified
`CLOSURE_REVIEW_INSTRUCTION_HASH_EXPECTATION_DEFECT`, not evidence corruption,
execution failure, or production drift. That blocked publication did not
invalidate the completed Stage V2 PASS.

## Session, bundle, and authority binding

The manifest binds stage `0.33B-V2`, the exact session, PR #259 authority head
`a00f074874a169a9ce7093ce091e40fcb0c5f1a5`, PR #258 head
`7a2361637f3d45b1a322f040c2b063a8fbf6d33e`, PR #257 head
`c2509b7f487dca27fc3a7fc1ef9c890d6370772a`, merged/verified PR #256, and
current main `a12ab61a0067afab16a888f618be91fa38cc6122`.

It binds the 15,808-byte V2 bundle SHA-256
`afa22667313f2b199af78995b67b16257993cab8c124efb27f071238c32cf712`,
frame nonce `b72accda-c7dc-49ba-bafb-6f0680d55910`, 25 semantic queries, and 26
frames. Authority accounting is `authorized=1, consumed=1, remaining=0`, with
consumption timestamp `2026-08-29T10:58:33.559294Z`. Retry, a second
connection, and residual authority are absent.

The retained execution sequence shows one governed launch attempt, permanent
consumption, one PostgreSQL session, repeatable-read/read-only bundle identity,
`COMMIT`, no rollback, psql exit 0, empty stderr, and no production mutation.
