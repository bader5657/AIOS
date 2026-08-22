# `.gitignore` Audit and Exact Hardening Authority

## Existing rule disposition

| Current rule | Classification | Disposition |
|---|---|---|
| `.env` | `REQUIRED` | Preserve exact production/local secret-file defense |
| `*.env` | `REQUIRED DEFENSE-IN-DEPTH` | Preserve; no tracked environment example currently conflicts |
| `docker/postgres/data/` | `REQUIRED` | Preserve local Compose data exclusion |
| `docker/postgres/backups/` | `REQUIRED` | Preserve local Compose backup exclusion |
| `logs/` | `USEFUL DEFENSE-IN-DEPTH` | Preserve; logging remains structurally outside source |
| `backup/` | `USEFUL DEFENSE-IN-DEPTH` | Preserve operational backup protection |
| `*.log` | `REQUIRED DEFENSE-IN-DEPTH` | Preserve tracked-log exclusion |
| `.vscode/`, `.idea/` | `USEFUL NON-SECURITY HYGIENE` | Preserve |

No current rule is proven stale. No current rule requires removal. `*.env` is
broader than `.env`, but its security purpose is accepted and no authorized
tracked fixture is hidden by it at the approval baseline.

## Exact authorized additions

The future implementation may modify `.gitignore` only and may add only the
following reviewed patterns, grouped and commented clearly:

```gitignore
.venv/
venv/
__pycache__/
*.pyc
.pytest_cache/

AIOS.zip
*.tar.gz
*.tgz
*.7z
backups/
rollback/
rollbacks/

*.dump
*.backup
*.pgdump
*.sql.gz

.tmp/
tmp/
temp/
*.tmp
*.part
*.download
```

`AIOS.zip` is authorized because that exact production-local archive was
previously observed. A broad `*.zip` rule is not authorized because future
synthetic source fixtures must not be silently hidden. Broad `*.sql`,
`runtime/`, `data/`, `documents/`, media-extension, or source-extension rules
are prohibited.

If implementation requires any path other than `.gitignore`, execution must
stop with:

`STAGE 9.2.4 GITIGNORE SCOPE EXPANSION REQUIRED`

## Required closed-world verification

The implementation PR must prove:

- exactly `.gitignore` changed;
- both legitimate migration SQL files remain tracked and are not ignored;
- every authorized protected pattern has a positive `git check-ignore` case;
- representative source, tests, docs, migration SQL, and a synthetic `.zip`
  fixture name remain non-ignored;
- no pre-existing tracked protected-data file exists;
- no additional ignore rule was added; and
- the PR is clean and mergeable.

No speculative ignore pattern is authorized.
