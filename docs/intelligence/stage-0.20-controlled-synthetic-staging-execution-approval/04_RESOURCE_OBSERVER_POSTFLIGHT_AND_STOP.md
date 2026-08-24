# Resource Observer, Postflight, and Stop Controls

During the sole request, collect bounded observations without another provider
request: container CPU and memory, host MemAvailable and swap, load average,
staging disk, and container restart/OOM state.

Immediately after any result, exception, timeout, or cancellation, verify:

- AIOS remains active/running with the same MainPID and `NRestarts=0`;
- PostgreSQL remains healthy;
- exactly one Telegram poller remains;
- host responsiveness, safe memory/load, and swap growth at most 64 MiB;
- staging disk remains below 80% with at least 5 GiB free;
- the container remains running without OOM/restart and with unchanged limits;
- private network and exposure state remain unchanged; and
- source remains clean and unchanged.

Do not wait five minutes for model unload and do not force unload. Stage 0.6.4
already verified unload/recovery behavior.

Stop before inference if any mandatory preflight is failed or indeterminate.
After the request, classify FAIL and stop on timeout, second request,
retry/fallback, failed or invalid result, provider/runtime exception, OOM,
container or AIOS restart, unhealthy PostgreSQL, poller-count change, unsafe
RAM/swap/load/disk, exposure drift, runtime mutation, or source mutation. Do
not repair and rerun under this authority.

No model pull/change, firewall/network/Docker/resource-limit change, service
restart, PostgreSQL mutation, production modification, Memory, Specialist,
business action, persistence outside the single evidence record, or Level B
activation is authorized.
