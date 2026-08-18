# Authority Trace

| Requirement | Active authority | Approved implementation consequence |
|---|---|---|
| Five Registry responsibility categories | Blueprint; Stage 5.1.1 | Runtime carries only approved fields |
| Historical Registry rejected | Stage 5.1.2 | New code only; no cherry-pick |
| Database-local table/schema/transaction design | Stage 5.2.1 | Exact migration realization |
| Original binary exclusion and future re-verification | Stage 5.2.2 | Mandatory static/schema/runtime gates |
| Register/read/update implementation | Frozen Execution Plan 5.3.1 | Exact minimum operation set; delete excluded |
| Isolation/failure verification | Frozen Execution Plan 5.3.2 | Comprehensive matrix remains later |
| Document Manifest caller integration | Frozen Execution Plan 5.4.1 | No caller wiring now |
| Registry Entry unresolved | Canonical Model; Stage 5.1.x/5.2.x | DTOs remain non-canonical |

The Project Owner decisions supply the exact dependency, runtime, migration,
configuration, test, and isolated-execution scope required before code work.
