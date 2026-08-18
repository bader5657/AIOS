# Authority Trace

| Requirement | Active authority | Verification consequence |
|---|---|---|
| Original file stored before processing | Blueprint | Storage ownership precedes Registry |
| Original binary not primarily stored in PostgreSQL | Blueprint | Binding exclusion |
| PostgreSQL stores structured identity, metadata, relationships, status, and file location | Blueprint; Stage 5.1.1 | Registry remains structured-information/reference-only |
| Historical Registry rejected | Stage 5.1.2 | Historical model supplies no current authority |
| Database-local table contains no binary concept | Stage 5.2.1 | Audit all nine approved concepts |
| Storage and Manifest ownership preserved | Stage 3 authority; Stage 5.2.1 | References do not transfer ownership |
| Stage 5.2.2 permits tests/audit evidence | Frozen Execution Plan | Design audit is applicable before Stage 5.3 implementation |

No new binary-storage policy is created. This package verifies existing Active
authority and records the mandatory future implementation gate.
