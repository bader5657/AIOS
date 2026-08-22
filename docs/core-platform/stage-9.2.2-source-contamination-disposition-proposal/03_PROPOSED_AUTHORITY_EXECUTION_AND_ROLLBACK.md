# Proposed Authority, Execution Order, and Rollback

If separately accepted and activated, authority is limited to the exact moves
listed in `02_EXACT_PATH_DISPOSITION.md`, creation of their exact destination
directories, preservation of metadata/hash manifests, and the already-approved
exact source checkout. No wildcard move or deletion is authorized.

Future execution order:

1. verify `aios.service`, predecessor MainPID, and exactly one poller;
2. verify predecessor SHA and preserved `.gitignore` patch;
3. record the exact contamination manifest and hashes;
4. create only the enumerated rollback/quarantine destinations;
5. move the three exact class C paths;
6. move the 23 exact class D cache paths, preserving relative paths;
7. confirm predecessor MainPID and single poller remain unchanged;
8. prove no untracked or ignored contamination remains in `/opt/aios-src`;
9. retry detached checkout of exact SHA
   `4168e098612c930215a49028d4ca9fc200d21cfd`;
10. verify exact SHA, clean worktree, entrypoint, requirements, and service
    artifact Git hash `ace763735417d196f3841fb526d76b4e593fbbc3`;
11. verify the predecessor process remains unchanged and do not claim the new
    source is active;
12. hand off later runtime/venv reconciliation without starting it.

Rollback restores moved paths to their exact original locations using the
manifest, but only if those paths remain absent and restoration cannot
overwrite new data. A failed source checkout returns to predecessor SHA and
restores the preserved `.gitignore` patch if required. Rollback never restarts
the service and never changes configuration, secrets, PostgreSQL, Storage,
runtime data, or database state.

This proposal prohibits `git clean`, `git reset --hard`, recursive or wildcard
deletion, service/systemd mutation, poller changes, package installation,
virtualenv creation, migrations, and Stage 9.2.3 execution. Stage 9.2.3 retains
formal `/opt/aios-src` versus `/opt/aios` layout governance.

Proposed approval state, not yet active:

`STAGE 9.2.2 SOURCE CONTAMINATION DISPOSITION APPROVAL REQUIRED`
