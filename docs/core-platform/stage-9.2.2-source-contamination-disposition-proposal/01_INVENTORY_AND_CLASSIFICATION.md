# Inventory and Classification

The active predecessor remained `aios.service` MainPID `1141941`, using
`/opt/aios/runtime/.venv/bin/python` with `/opt/aios-src` as its working
directory. No second poller existed during inventory.

| Exact category | Entries | Approximate size | Class | Finding |
|---|---:|---:|---|---|
| `/opt/aios-src/.venv/` | 2477 | 55 MiB | C | Historical duplicate venv; directory, not symlink; no service, tracked-source, runtime-config, PID map, or PID FD reference found |
| `/opt/aios-src/.pytest_cache/` | 5 | 36 KiB | D | Regenerable pytest cache |
| 22 exact `__pycache__` directories listed in `02_EXACT_PATH_DISPOSITION.md` | 67 files | about 436 KiB | D | Regenerable CPython bytecode; historical-looking source paths contain cache only |
| `/opt/aios-src/AIOS.tar.gz` | 1 | 58,880 bytes | C | Small source backup/archive; no sensitive filename match in 117-entry metadata listing |
| `/opt/aios-src/AIOS.zip` | 1 | 52,105 bytes | C | Small source backup/archive; no sensitive filename match in 136-entry metadata listing |
| local `.gitignore` delta | 1 tracked modification | 226-byte patch | C | Preserved historical/operator evidence; must not be reapplied to hide contamination |

No ignored business data, database dumps, logs, backups directory, `.env`,
credential file, private key, build tree, or generated test-data directory was
identified by path-name audit. Certificate bundle filenames inside the old
venv are ordinary dependency content, not an observed production secret.

There are no class A, B, E, or F findings in the inventoried contamination.
The source venv is not the interpreter used by the active predecessor and is
therefore class C, not class A. Stage 9.2.3 retains permanent layout policy;
this proposal addresses only paths that prevent a clean exact checkout.

