# Creation, Existing-Target, Validation, and Evidence Contract

After this authority activates, the operator may perform the equivalent of
exactly:

```text
install -d -o aiosadmin -g aiosadmin -m 0750 /opt/aios/runtime/intelligence/staging/level-b-sessions
```

Resolve and inspect the complete parent chain immediately before creation. No
component may unexpectedly redirect outside
`/opt/aios/runtime/intelligence/staging`; the parent real path must remain
exact. The target must be absent and must not be a symlink, file, or other
object. No sibling or alternate directory may be selected.

If the target already exists, do not run `install`, replace it, or repair it.
Inspect exact type, real path, owner, group, and mode. If it is the exact real
directory owned by `aiosadmin:aiosadmin` at mode `0750`, classify provisioning
as already satisfied. Otherwise stop and return to governance.

After creation, verify statically and read-only:

- path exists and type is directory;
- real path is exactly the authorized path;
- owner and group are `aiosadmin:aiosadmin`;
- mode is exactly `0750` and not world-writable;
- no path component or target is a symlink;
- parent identity, owner, group, mode, and inode are unchanged; and
- source, services, Docker/network/firewall, production configuration, and
  model state were not modified.

Do not create a write-probe, placeholder, lock, runtime flag, state file,
session ID, or session journal. This authority creates the root directory only.
It does not authorize rollback/removal after successful provisioning.

The provisioning operator must return one bounded, secret-free result in the
task record containing timestamp, path, frozen parent identity, pre-existence,
action, final owner/group/mode/real path, preservation results, and final
classification. Because this authority permits only one filesystem mutation,
it does not create a second runtime evidence file. A later governance-only
closure records that returned evidence at the proposed repository path:

`docs/intelligence/stage-0.21-level-b-session-journal-root-provisioning-final-closure/01_PROVISIONING_EVIDENCE.md`

Creation of that closure record is not part of operational provisioning and
requires its normal governance publication workflow.

The approved future journal contract remains:

`/opt/aios/runtime/intelligence/staging/level-b-sessions/<session_id>.jsonl`

with session ID
`stage-0.21-level-b-session-YYYYMMDDTHHMMSSffffffZ-<uuid4hex>`. Provisioning
does not create or reserve an ID. Future session journals remain
exclusive-create, append-only while active, flushed per governed event,
finalized once, hashed, and immutable after closure.
