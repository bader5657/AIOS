# Exact Verification Baseline

At verification start, `HEAD`, local `main`, and `origin/main` all resolved to
`8154318ee647f66e1239beb22ad484834fbf06df`; the worktree was clean. That commit
is the Stage 6.2.1 merge commit and exact Stage 6.2.2 baseline.

Git-resolved baseline objects:

| Scope | Object ID |
|---|---|
| `core/domain/` tree | `0cfd9fe0b1887007fad06199e427806f92837da9` |
| `tests/unit/domain/` tree | `53c45747fa5e9abd9c5f16e961b2aa1fcf8cf9fc` |
| `config/event-engine.schema.json` blob | `b1c1e8365f6ce8beadca520f471991893474bcae` |
| Stage 6.2.1 contract tree | `dcbabc9564d186fb72eb31a7e87e57eefb1a143f` |

Open PR #1 is a dirty historical branch unrelated to this exact baseline and
does not block governance closure.
