# Runtime, Preflight, Resource, Postflight, and Preservation Evidence

## Frozen staging identity

| Control | Verified value |
|---|---|
| Docker socket | `unix:///opt/aios/runtime/intelligence/staging/ollama/mnt/docker.sock` |
| Endpoint | `http://172.31.63.2:11434` |
| Ollama | `0.32.13` |
| Model | `qwen2.5:1.5b-instruct-q4_K_M` |
| Network / IP | `aios-ollama-runtime / 172.31.63.2` |
| Memory / memory-swap | `3221225472 / 3221225472` bytes |
| NanoCpus | `1000000000` |

Fresh preflight passed: AIOS was active/running at MainPID `15845` with
`NRestarts=0`; PostgreSQL was healthy; exactly one Telegram poller existed;
MemAvailable was `6964129792` bytes; swap use was `524288` bytes; one-minute
load was `0.17919921875` across two available CPUs; and the staging filesystem
was 27% used with `74195292160` bytes free. The container was running, not
restarting or OOM-killed, at restart count zero and the exact frozen ceilings.
The model was naturally unloaded.

Network preflight and postflight found no published port, host listener on
11434, acquisition network, or visible exposure drift. The separate privileged
firewall/NAT evidence remained applicable and immutable.

During the sole request, peak observed container memory was `1979979923`
bytes, below the approved ceiling. No OOM or restart occurred.

Immediate postflight passed: AIOS retained MainPID `15845`, active/running
state, and `NRestarts=0`; PostgreSQL remained healthy; and the Telegram poller
count remained exactly one. MemAvailable was `5749280768` bytes; swap remained
`524288` bytes with zero growth; one-minute load was `0.97119140625` across two
CPUs; and disk remained 27% used with `74195107840` bytes free. Container
state, resource ceilings, private network identity, and exposure state were
unchanged.

The source remained clean and unchanged. No runtime, service, PostgreSQL,
network, firewall, model, configuration, or production-startup mutation was
performed. Production safety and availability were preserved.
