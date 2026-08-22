# Service, Lifecycle, Reboot, and Single-Poller Evidence

## Authoritative service contract and artifact

- tracked artifact: `deploy/systemd/aios.service`;
- installed production unit: `/etc/systemd/system/aios.service`;
- runtime identity: `User=aiosadmin`, `Group=aiosadmin`;
- working directory: `/opt/aios-src`;
- interpreter/entrypoint:
  `/opt/aios/runtime/venv/bin/python -m core.adapters.telegram.main`;
- environment file: `/opt/aios/runtime/config/runtime.env`;
- restart policy: `Restart=on-failure`, `RestartSec=10s`;
- process containment: `KillMode=control-group`;
- exactly one `ExecStart`; and
- systemd is the sole production process owner.

## Accepted lifecycle evidence

| Criterion | Result |
|---|---|
| Unit installed and effective artifact reconciled | `PASS` |
| Service enabled and active | `PASS` |
| Initial start | `PASS` |
| Controlled clean stop/start | `PASS` |
| Automatic activation after controlled reboot | `PASS` |
| MainPID established after start/reboot | `PASS` |
| Stable restart state | `NRestarts=0`; no restart loop observed |
| Orphan/predecessor/alternate poller after cutover | `NONE` |

## Single-poller invariant

The controlled predecessor-to-systemd transition was exactly `1 → 0 → 1`:
one predecessor poller, a proven zero-poller gate, then exactly one
systemd-owned poller. Normal operation, clean restart, reboot, and the
source/runtime separation cutover retained exactly one production poller.

Concurrent or intentionally duplicated production polling: `NONE`.
