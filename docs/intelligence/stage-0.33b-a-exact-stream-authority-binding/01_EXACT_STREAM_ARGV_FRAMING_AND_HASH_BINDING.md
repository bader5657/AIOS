# Stage 0.33B-AB Exact Stream Identity and Protocol Binding

The bound template is `docs/intelligence/stage-0.33b-d-exact-sql-stream/01_STAGE_0_33B_D_EXACT_SQL_STREAM.sql` with SHA-256 `bc9860db9bebb8be5dea5bea2c316d2e99cd3e5e1dccda6d6fd4adc3cbb42fb3`. Migration 0005 UP SHA is `7de76e82cb26863cd3c14abc4394cb036936ed0f1c6c64819f03094cf9069293`; DOWN SHA is `c210305a14399b4826abc46fad75c138bc8e698d9b85380eba893a01c1501b16` and DOWN is not authorized.

Raw-byte assembly has exactly one marker, 26558 bytes, and SHA-256 `ce89b4c357e7b0bb52316b363163d8342afbf9cb1e3eaafb98fad8fca5a49799`; no normalization, interpolation, or runtime SQL invention is permitted. Counts are semantic 57, framing 49, physical 106, frames 49, chunks 49.

`FRAME_NONCE` is immutable `a3e1a015-c078-44b4-a618-f6c7f49831f7`. The exact argv is `/usr/bin/docker exec -i aios-postgres /usr/local/bin/psql -X -v ON_ERROR_STOP=1 --csv -t -q -P pager=off -U aios -d aios`. stdout is CSV only and stderr is a separate bounded diagnostic channel. Parsing is strict Python standard-library `csv.reader` over UTF-8 with `newline=''`, delimiter `,`, quotechar `"`, `doublequote=True`; no line/regex parser is allowed.

Each exact frame is `["AIOS_FRAME", SECTION_ID, FRAME_NONCE]`; all 49 IDs occur once in the reviewed PR #251 order. Execution is one psql process, one PostgreSQL session, one transaction, and 49 incremental chunks. Full-stream bulk submission is not authorized. Each next chunk waits for its exact frame and semantic PASS. Zero records plus matching frame proves a zero-row query; missing frame fails. Semantic mismatch sends exactly `ROLLBACK;` on the same live session. ON_ERROR_STOP termination permits no retry or second connection and is fail-closed through connection rollback semantics.

The reviewed result manifest, V01–V05 widths (4/3/2/7/6), exact PO01/PO02/R04 tuples, owner-derived rows, cross-checks, and field-level comparison algorithm are bound without reinterpretation. Any pre-launch drift in files, hashes, nonce, argv, counts, frames, parser, or delta algorithm blocks activation and leaves authority unconsumed.
