# Resource, Special-Test, and Production-Safety Evidence

## Resource evidence

| Gate | Evidence | Result |
|---|---|---|
| Loaded container RAM | approximately `1.70 GiB / 3 GiB` | `PASS` |
| Idle/recovered container RAM | approximately `687 MiB`; baseline approximately `685 MiB` | `PASS` |
| Host swap | approximately `524288 bytes`; no meaningful growth | `PASS` |
| CPU | bounded at `1 vCPU`; host responsive | `PASS` |
| Staging filesystem | approximately `36%` used; approximately `10.7 GiB` free | `PASS` |

## Timeout boundary

At the approved `1 ms` client deadline, curl exited with code `28` after
approximately `15 ms`. `TIMEOUT_BOUNDARY` passed. The runtime remained healthy,
the model remained unloaded after the timeout, and production remained stable.
The expected future adapter mapping is `FailureCode.TIMEOUT`; no adapter exists
or is activated by this record.

## Malformed-output containment

The special test returned HTTP `200` in `6191 ms` with
`{"category":"normal","confidence":100}`. Schema validity was `0`, and the
invalid output was rejected before downstream acceptance. Containment passed;
runtime and production remained healthy. The expected future adapter mapping
is `FailureCode.MALFORMED_OUTPUT`; no adapter exists or is activated here.

## Unload and memory recovery

The model was initially loaded at approximately `1.698 GiB` container RAM. It
unloaded after `241 seconds`, within the approved `420-second` maximum. Container
RAM recovered to `687.3 MiB`, against an approximately `685 MiB` baseline and
the approved baseline-plus-`256 MiB` threshold. Final `/api/ps` was
`{"models":[]}`. Host swap remained stable.

`MODEL_UNLOAD_WINDOW: PASS`

`MEMORY_RECOVERY: PASS`

## Production safety

Throughout the benchmark and final recovery observation:

- AIOS remained `active/running`, with `MainPID=15845` and `NRestarts=0`;
- PostgreSQL remained healthy;
- the Telegram poller count remained exactly one;
- the host remained responsive; and
- no production instability occurred.

Production safety is `PASS`. These observations do not authorize production
inference or any production mutation.
