# README Claim-Correction Policy

## Required semantic taxonomy

Future README prose must distinguish these meanings even when the internal
labels are not shown to readers:

- `VERIFIED_CURRENT`: accepted current capability, including production
  verification only where production evidence exists;
- `VERIFIED_WITH_LIMITATION`: implemented or tested capability whose accepted
  boundary and exclusions remain explicit; and
- `ROADMAP_ONLY`: architecture or later-stage intent that is not an active
  current capability.

Architecture, tests, historical branches, or planned roadmap items cannot be
promoted into current capability evidence.

## Approved current Stage 9 statement

README may state conceptually:

> Stage 9 operational alignment has verified the systemd-managed Telegram/Core
> Platform runtime foundation, single-poller operation, reboot activation,
> source/runtime separation, and security/exclusion boundaries.

Equivalent concise wording is allowed if it preserves the same scope. It must
not imply a fully production-ready or fully autonomous AIOS.

## Broad completion labels

| Current wording | Required disposition |
|---|---|
| `Foundation Completed` | Remove or narrow to an exact accepted foundation scope; do not claim whole-product completion |
| `Asset Pipeline Completed` | Replace with bounded component-stage wording such as `Component foundation verified within its accepted scope` |
| `Mission Control Completed` | Replace with its verified formatter/status/inventory boundary or omit |
| `Next Milestone: AI Pipeline / Brain / Specialist Router / Business Specialists` | Remove or replace with wording derived from the active execution plan; do not invent stage order |

README must distinguish component verification from product completion,
test-only evidence from production verification, and roadmap intent from
runtime capability.
