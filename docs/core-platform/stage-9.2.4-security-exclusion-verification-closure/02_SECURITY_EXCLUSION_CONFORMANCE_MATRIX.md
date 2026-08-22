# Security / Exclusion Conformance Matrix

Structural separation is the primary control; `.gitignore` is defense in
depth. Every required category conforms.

| Category | Source/Git placement | Runtime placement | Protection/exclusion | Verification status | Remediation status |
|---|---|---|---|---|---|
| Secrets | No production secret found in current or historical repository scans; no secret file in source | `/opt/aios/runtime/config/runtime.env`, outside source | `root:aiosadmin`, mode `0640`; `.env`/`*.env` ignored; contents not disclosed | `PASS` | `NONE REQUIRED` |
| SSH private keys | No private SSH key under `/opt/aios-src` | `/home/aiosadmin/.ssh`, outside source | `.ssh` mode `0700`; `id_ed25519` mode `0600`; public key, `known_hosts`, and `authorized_keys` also outside source | `PASS` | `NONE REQUIRED` |
| PostgreSQL data | No database data in source | `/opt/aios/docker/postgres/data` bind-mounted to `/var/lib/postgresql/data` | Outside source; host numeric owner `70:70`, mode `0700`; database healthy; no contents inspected | `PASS` | `NONE REQUIRED`; numeric ownership recorded for later review |
| DB dumps/backups | No repository dump tracked; migration SQL remains legitimate source | No dump/backup returned by approved metadata-only runtime scan | Dump/backup ignore patterns active; no database content inspected | `PASS` | `NONE REQUIRED` |
| Logs | No tracked/runtime log in source | journald is authoritative | No authentication-secret pattern; matched values not disclosed | `PASS WITH DOCUMENTED PRIVACY FINDING` | `DOCUMENTED PRIVACY HARDENING DEFERRED` |
| Runtime cache | Source bytecode scan returned none | `/opt/aios/runtime/cache/pycache`, outside source; 614 `.pyc` files | `aiosadmin:aiosadmin`, mode `0750`; cache/bytecode ignore patterns active | `PASS` | `NONE REQUIRED` |
| Rollback artifacts | No rollback artifact in source | `/opt/aios/runtime/rollback`, outside source; Stage 9.2.2 and 9.2.3 artifacts present | Operational-only; contents not disclosed; rollback ignore patterns active | `PASS` | `NONE REQUIRED`; observed root mode `0755` recorded for later review |
| Original business files | No original business file found in source | `/opt/aios/data/documents/{images,voice,pdf,docs,links}`, outside source | Contents not inspected; counts only; root observed `aiosadmin:aiosadmin 0775` | `PASS` | `NONE REQUIRED`; root mode recorded for later review |
| Manifests | No runtime Manifest found in source | `/opt/aios/data/documents/manifests`, outside source | Runtime/business metadata; contents not inspected | `PASS` | `NONE REQUIRED` |
| Temporary downloads | No temporary download in source | Approved runtime locations scanned | `*.tmp`, `*.part`, and `*.download` scan returned none; ignore patterns active | `PASS` | `NONE REQUIRED` |
| Source contamination | `/opt/aios-src` at exact deployed HEAD with clean status; protected-file scan clean | Runtime/data/docker roots are separate | `/opt/aios/runtime`, `/opt/aios/data`, and `/opt/aios/docker` all outside source | `PASS` | `NONE REQUIRED` |

## Count evidence

| Runtime category | Count |
|---|---:|
| Original images | 21 |
| Original voice | 0 |
| Original PDF | 0 |
| Original docs | 0 |
| Original links | 0 |
| Manifests | 127 |
| Runtime `.pyc` cache files | 614 |
| Approved temporary residue matches | 0 |

Result: all eleven required categories satisfy Stage 9.2.4 placement and Git
exclusion requirements. The logs row carries a non-blocking, explicitly
deferred privacy-hardening finding, not a secret exposure.
