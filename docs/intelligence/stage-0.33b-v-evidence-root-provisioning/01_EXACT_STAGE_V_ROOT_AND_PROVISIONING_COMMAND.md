# Stage 0.33B-V-FP Exact Root and Provisioning Command

Date: 2026-08-29 (Asia/Jakarta)

## Frozen parent contract

Immediately before future provisioning, the operator must verify without
mutation that the existing parent is exactly:

| Property | Required value |
|---|---|
| Path | `/opt/aios/runtime/intelligence/production-execution-evidence` |
| Type | real directory |
| Symlink | no |
| Owner/group | `root:root` |
| Mode | `0755` |

If any property differs, stop. Do not follow a symlink, repair the parent, or
run privileged remediation. The authority below does not extend beyond the
exact child-creation command.

## Frozen Stage V root contract

The sole target is:

```text
/opt/aios/runtime/intelligence/production-execution-evidence/stage-0.33b-v
```

Its required final state is a real directory, not a symlink, owned by
`aiosadmin:aiosadmin`, with mode `0750`.

Before provisioning:

- If the target is absent, it is eligible for the exact command below.
- If it is already present and exactly a real, non-symlink directory owned by
  `aiosadmin:aiosadmin` with mode `0750`, do not recreate it; proceed only to
  the separately governed verification.
- If it is present with any different property, stop. Do not follow, chmod,
  chown, delete, move, replace, or recreate it.

## Sole privileged command

Exactly one privileged command is authorized, and only for an authenticated
human Project Owner or explicitly authorized VPS operator:

```text
/usr/bin/sudo /usr/bin/install \
  -d \
  -o aiosadmin \
  -g aiosadmin \
  -m 0750 \
  /opt/aios/runtime/intelligence/production-execution-evidence/stage-0.33b-v
```

No bare or PATH-dependent `sudo`/`install`, alternate command, extra option,
additional target, shell wrapper, recursive operation, repair, or second
privileged command is authorized. A password prompt is handled only by the
human directly in the VPS terminal; it is never exposed to Codex or automation.

## Fail-closed outcome

Any parent drift, target conflict, symlink, unexpected owner/group/mode/type,
authentication failure, or command failure stops provisioning. There is no
automatic repair or substitution. PostgreSQL must not be contacted and Stage
0.33B-V authority remains unconsumed.
