# Authority, Baseline, Scope, and Ownership

The active authority is the Stage 8.2.1 verification approval published through
PR #67. Test PR #68 merged the single authorized test at commit
`2f5080be897bc70c2fbd898f6ce6782dbf5a84d1`. At that closure baseline, `HEAD`,
local `main`, and `origin/main` resolved identically and the worktree was clean.

The authoritative ownership matrix is:

| Action | Semantic owner | Orchestration boundary |
|---|---|---|
| Receive | Telegram Adapter owns transport receipt | Universal Ingestion owns receiving-side acceptance and orchestration |
| RequestContext | Universal Ingestion | Constructed once before Asset Pipeline |
| Store Original | Storage capability | Asset Pipeline requests storage where applicable |
| Extract Metadata | Metadata Engine | Asset Pipeline invokes the capability |
| Create Manifest | Document Manifest capability | Asset Pipeline invokes it after metadata |
| Register | PostgreSQL Registry | Universal Ingestion owns the bounded invocation and handoff |
| Process | Event Engine | Universal Ingestion gates invocation after Registry commit |
| Route | AIOS Core | Universal Ingestion gates the same-envelope handoff after Event success |
| Respond | Telegram Adapter | Transport receipt/readiness acknowledgement after delegated ingestion returns |

Orchestration does not transfer semantic authority. Review found no component
assuming another component's classification, storage, persistence, event,
routing, or response semantics.
