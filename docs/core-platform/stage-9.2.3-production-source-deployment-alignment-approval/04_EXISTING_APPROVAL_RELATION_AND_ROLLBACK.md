# Existing Approval Relationship and Rollback

## Preserved execution authority

This package corrects only the production source deployment baseline. It does
not duplicate, replace, or expand the active package at
`stage-9.2.3-controlled-vps-separation-approval`.

After source alignment succeeds, that existing approval remains authoritative
for runtime-cache creation, installed-unit backup, the `1 → 0 → 1` polling
transition, corrected-unit installation, daemon reload, effective
`PYTHONPYCACHEPREFIX` and `ReadOnlyPaths` checks, source-clean verification,
and runtime-cache bytecode evidence.

## Failure and rollback

If the new source deployment or corrected service fails:

1. keep the exact prior source SHA and all rollback evidence;
2. stop and prove zero pollers before any further source or unit switch;
3. restore the approved Stage 9.2.2 service-unit backup;
4. if predecessor compatibility requires it, return `/opt/aios-src` to exact
   commit `4168e098612c930215a49028d4ca9fc200d21cfd`;
5. run `systemctl daemon-reload`;
6. start the service once; and
7. prove exactly one systemd-owned poller.

Rollback authorizes no database, configuration, Docker, Storage, or business
data change. Unknown source residue remains a stop condition, not cleanup
authority.
