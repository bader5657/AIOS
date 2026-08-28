# Stage 0.33B-DS Stream Assembly, Hash, and Static Validation

## Frozen inputs and outputs

| Artifact | SHA-256 |
|---|---|
| Exact SQL template | `53847f0bfb9b5e6595b25f83035726a2f10f0c3568baca2b863bea8f2961c693` |
| Migration 0005 UP | `7de76e82cb26863cd3c14abc4394cb036936ed0f1c6c64819f03094cf9069293` |
| Migration 0005 DOWN, identity only | `c210305a14399b4826abc46fad75c138bc8e698d9b85380eba893a01c1501b16` |
| Assembled candidate success stream | `bb11d884e9238fadb7537e32c18eb24df2e6ab1978b35e11af31dbbc2157c530` |

The template is
`docs/intelligence/stage-0.33b-d-exact-sql-stream/01_STAGE_0_33B_D_EXACT_SQL_STREAM.sql`.
The UP artifact is
`migrations/postgres/0005_add_material_receipt_creator_provenance.up.sql`.

## Exact assembly method

Treat both inputs as raw bytes. Require the template to contain exactly one
complete byte sequence:

```text
-- AIOS_MIGRATION_0005_UP_EXACT_ARTIFACT_INSERTION_POINT
```

Require the template and UP hashes above. Replace that exact marker, excluding
its terminating newline, with the complete exact UP artifact bytes. Preserve
the marker line's original terminating newline after the inserted artifact.
Perform no newline conversion, trimming, encoding conversion, interpolation,
additional substitution, or trailing-byte normalization. The assembled stream
is `21928` bytes and must hash exactly to the assembled candidate SHA above.

The future executor may implement this byte operation in reviewed code, but may
not generate or transform SQL. Before launch, `execution.jsonl` must durably
record the three hashes, marker count `1`, assembled byte size `21928`, statement
count `57`, and exact assembly PASS.

## Statement order and count

The frozen order is T01-T07, L01-L04, I01-I02, M01-M02, S01, Z01, F01-F04,
O01-O08, R01-R04, X01, V01-V05, PF01-PF04, PO01-PO08, PR01-PR04, C01.
The assembled success stream contains exactly 57 semicolon-terminated SQL
statements: one `BEGIN`, six `SET LOCAL`, four locks, 22 pre-DDL `SELECT`
statements, the two exact Migration 0005 statements, five new
post-UP verifiers, 16 repeated preservation `SELECT` statements, and one final
`COMMIT`.

The four PF statement bodies are byte-for-byte copies of F01-F04. The eight PO
and four PR statement bodies are byte-for-byte copies of O01-O08 and R01-R04.
All 22 prior I/M/S/Z/F/O/R statement bodies are byte-for-byte copies of the
reviewed canonical Stage 0.33B-P bundle.

## Static safety result

Mechanical audit of the assembled candidate returned:

| Control | Result |
|---|---:|
| Statements | `57` |
| `BEGIN` | `1` |
| success `COMMIT` | `1` |
| governed locks | `4` |
| Migration `ALTER TABLE` | `1` |
| approved Migration column `GRANT INSERT` | `1` |
| Migration 0005 marker replacement | `1` |
| Migration 0005 DOWN / REVOKE / DROP | `0` |
| Migration 0004 execution | `0` |
| business `INSERT` | `0` |
| business `UPDATE` | `0` |
| business `DELETE` | `0` |
| `COPY` | `0` |
| ownership mutation | `0` |
| role creation/alteration | `0` |
| membership mutation | `0` |
| ungoverned `GRANT` | `0` |
| `psql` meta-command | `0` |
| shell command | `0` |
| dynamic SQL | `0` |

The template contains no unconditional `ROLLBACK`. Failure handling is
executor-side in the same already-open session, as frozen in `00_...md` and PR
#249. There is no SQL after C01 `COMMIT;`.
