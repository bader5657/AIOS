# Installation Sequence, Stop Conditions, and Rollback

## Approved future sequence

1. capture production read-only precheck evidence;
2. verify host free space, safety reserve, Docker capacity, swap, and protected
   service stability;
3. create the hard-bounded 16 GiB staging filesystem;
4. create the exact root-owned staging runtime, model, and config directories;
5. acquire only the exact pinned Ollama image;
6. verify `linux/amd64` and the full runtime digest;
7. create the isolated staging container with all resource, mount, privilege,
   lifecycle, and network controls;
8. start the Ollama runtime only;
9. perform the runtime-only health check;
10. acquire only the exact approved Qwen model;
11. verify the model manifest, blob, size, quantization, license, and accepted
    provenance limitation;
12. confirm no model is preloaded unless a later benchmark explicitly requests
    it;
13. stop the runtime or unload the model if the benchmark is not beginning;
14. verify AIOS, PostgreSQL, Telegram, production Docker, and host state are
    unchanged and stable;
15. record complete installation, disk, resource, network, identity, and
    cleanup-ready evidence.

This package approves future controlled execution of the sequence. It does not
execute any step in this governance task.

## Hard stop conditions

Stop on runtime or model digest mismatch; material provenance contradiction;
inability to preserve the host reserve or production Docker safety; inability
to enforce the 16 GiB disk, 3 GiB RAM, or one-vCPU ceilings; required public
exposure; required production secret or service modification; required second
model; required provider adapter; or failure to maintain the approved privilege
and isolation boundaries.

## AIOS and production boundary

Integration with AIOS Core, Brain orchestration, `InferenceProvider`, Telegram,
Registry, and Event Engine is `NONE`. No `aios.service` modification, systemd
integration, auto-start, production traffic, production readiness claim, or
production activation is authorized.

## Rollback

Rollback removes only the named staging container, staging-only network,
bounded staging model/runtime/config filesystem, and temporary acquisition
metadata created by the controlled installation. It must not prune, delete,
restart, reconfigure, or otherwise touch production containers, images,
volumes, networks, data, services, source, or secrets.

## Benchmark handoff

After successful installation evidence is accepted, the next stage is:

`Intelligence Stage 0.6.4 — Ollama/Qwen Isolated Staging Benchmark`

It must measure startup; idle, peak, and steady RAM; CPU; swap; disk; p50/p95
latency; timeout behavior; structured-output reliability; malformed-output
containment; failure mapping; and service isolation. Production activation is
prohibited until benchmark acceptance and later explicit production authority.
