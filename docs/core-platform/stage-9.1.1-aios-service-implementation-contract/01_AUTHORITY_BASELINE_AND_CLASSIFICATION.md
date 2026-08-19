# Authority, Baseline, and Classification

Authority is applied in this order: Blueprint, Frozen Roadmap, frozen Core Platform Execution Plan, Authority Hierarchy, Layer Architecture, and accepted Stage 8 closure.

The Blueprint requires:

- source repository at `/opt/aios-src`;
- runtime at `/opt/aios`;
- one systemd service named `aios.service`;
- automatic activation after reboot;
- exactly one Telegram polling instance; and
- observability through `systemctl` and `journalctl`.

Execution Plan 9.1.1 requires an authoritative implementation contract because the repository contains no service artifact while README/CHANGELOG claims systemd capability. Stage 8 is closed at merge `ff118f9d6ff3785eea2951ceae85a9543a9df7c5`, making 9.1.1 eligible.

`STAGE 9.1.1 = GOVERNANCE / SERVICE CONTRACT DEFINITION ONLY`

This sub-step may establish service purpose, topology, ownership, boundaries, required principles, and later acceptance criteria. Exact unit policy belongs to 9.1.2. Implementation, installation, VPS access, polling, restart, and deployment are prohibited here.
