# Stage 0.33B-VR Evidence Identity Reconciliation

Date: 2026-08-29 (Asia/Jakarta)

## Scope and safety boundary

This is an offline review of the finalized Stage 0.33B-V session
`stage-0.33b-v-current-state-20260829T093247Z-6143ee79-b0da-4a00-a2ec-3f7a5b5f2fe8`.
It made no PostgreSQL connection, executed no SQL, retried no authority, and
performed no production or finalized-evidence mutation. Stage V authority
remains permanently consumed; its transaction outcome remains `ROLLBACK`.

## Final artifact identities

The files remain regular non-symlinks owned by `aiosadmin:aiosadmin`, mode
`0440`.

| Artifact | SHA-256 | Bytes | JSONL records | Inode | Final mtime (+07:00) |
|---|---|---:|---:|---:|---|
| `execution.jsonl` | `e42ffd1cfad42b69d1d90de9f0b98cb4e1ddee566a393a5dbd08a9a5d88933af` | 6514 | 7 | 2887924 | `2026-08-29 16:33:58.505752436` |
| `semantic-results.jsonl` | `ddab170e5bafaced9423a6f623d560e5d3e7d239d5a66eeb28f0428c8c8c949c` | 25199 | 18 | 2887925 | `2026-08-29 16:33:58.450752400` |
| `manifest.json` | `464b964b85c06c2871a71d01518dd1bb595baf8bbdb8a5d252ba5fa9ace26161` | 1376 | n/a | 2887272 | `2026-08-29 16:33:58.507752437` |

The manifest independently binds `semantic-results.jsonl` to the same SHA,
25199 bytes, 18 records, and coverage `18/25`. The original Stage V command
completion and final report also recorded that same identity. The finalized
bytes, final manifest, and original execution/finalization record therefore
agree.

The earlier forensic prompt supplied
`ddab170e5bafaced94023a6f623d560e5d3e7d239d5a66eeb28f0428c8c9f49c`.
That value exists only in that prompt and does not identify the finalized
artifact. The prior `STAGE 0.33B-VR R03 DISPOSITION INCONCLUSIVE` stopped before
R03 inspection, exactly as its gate required. Its mismatch is classified
`INCORRECT_FORENSIC_PROMPT_EXPECTATION`, not evidence drift. This corrected
review supersedes that result for analytical purposes without rewriting it.

## Semantic coverage derived from final evidence

| Query IDs | Classification |
|---|---|
| `I01`, `I02`, `S01`, `F01`-`F04`, `O01`-`O08`, `R01`, `R02` | `COMPLETE_RETAINED_PAYLOAD` |
| `R03` | `FAIL_PAYLOAD_RETAINED` |
| `R04`, `V01`-`V05`, `N01` | `NOT_REACHED` |
| none | `MISSING` |

The first 17 semantic PASS observations remain valid bounded observations from
the one repeatable-read snapshot. They do not make Stage V an overall PASS.

