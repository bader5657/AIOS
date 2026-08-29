# Stage 0.33B-V2P Distinct V2 Bundle, Nonce, and Identity

Date: 2026-08-29 (Asia/Jakarta)

## Source and historical separation

This package was cut from clean `main` at
`7066ad5bf3d68fe5499131f6ae7fa3e29ee7b5de`. The historical Stage V bundle is
`docs/intelligence/stage-0.33b-v-read-only-current-state-verification/03_STAGE_0_33B_V_EXACT_QUERY_BUNDLE.sql`,
exactly 15,808 raw bytes with SHA-256
`304fdf5fbf63bcea9c8e41ddb8e921831a9b4a01a1262acca2cfd09273e855f1`.
It remains byte-for-byte unchanged.

Original Stage V remains **FAILED** and its production authority remains
permanently **CONSUMED**. Migration 0005 remains **COMMITTED**. Historical
Stage D semantic evidence remains **PERMANENTLY INCOMPLETE**. Nothing in this
package reinterprets, replaces, or modifies those historical facts or records.

## Frozen V2 bundle identity

`STAGE_V2_FRAME_NONCE` is frozen once as
`b72accda-c7dc-49ba-bafb-6f0680d55910`. It is a canonical lowercase UUIDv4 and
differs from the historical Stage V nonce
`0fba8f0c-4c0b-4101-9ed6-e1a597402394`. It is a literal contract value, never a
runtime substitution.

The V2 bundle is
`03_STAGE_0_33B_V2_EXACT_QUERY_BUNDLE.sql`, exactly 15,808 raw bytes with
SHA-256 `afa22667313f2b199af78995b67b16257993cab8c124efb27f071238c32cf712`.
The old nonce occurs zero times. The new nonce occurs 27 times: one
non-executable header metadata occurrence and exactly 26 executable frame
string literals. The 26 ordered frame IDs are `T00,I01,I02,S01,F01,F02,F03,F04,O01,O02,O03,O04,O05,O06,O07,O08,R01,R02,R03,R04,V01,V02,V03,V04,V05,N01`.

The transaction remains exactly `BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE
READ READ ONLY;`, the five reviewed `SET LOCAL` statements, the ordered query
and frame stream, and `COMMIT`. The bundle contains 25 semantic queries plus
one control/session frame and 25 semantic frames.

## No authority

This package grants zero production sessions and creates no Stage V2
production authority. It does not authorize execution, production access,
candidate traffic, or any mutation. The actor-provenance operational gate
remains **OPEN** and candidate activation remains **NOT AUTHORIZED**.
