# Final Gate Verification

## Remediated blocker

Read-only enumeration of the isolated staging daemon returned exactly these
networks:

- `aios-ollama-runtime`;
- `host`;
- `none`.

An explicit inspection of `aios-ollama-acquisition` returned `network not
found`. The runtime network remains Docker-internal, and inspection shows the
staging container as its only attached container at `172.31.63.2/29`.

| Gate | Evidence | Result |
|---|---|---|
| Acquisition network has no containers before removal | operator remediation evidence | `PASS` |
| Acquisition network object removed | daemon enumeration plus explicit not-found inspection | `PASS` |
| Staging attachment | only `aios-ollama-runtime` | `PASS` |
| Runtime network | internal `172.31.63.0/29` bridge | `PASS` |
| Public/host port | `PortBindings={}`; `11434/tcp` unpublished; no host listener | `PASS` |
| Temporary acquisition firewall rules | operator evidence records no `AIOS_STAGE_0_6_3` rules remaining | `PASS` |

The verifier could not independently enumerate the nftables ruleset without an
interactive privileged credential. The firewall gate therefore uses the new
operator evidence, corroborated by the isolated daemon's
`--iptables=false --ip6tables=false --ip-forward=false --ip-masq=false
--userland-proxy=false` controls and the absence of a host listener on port
`11434`.

## Runtime, model, storage, and ceilings

| Control | Verified value | Result |
|---|---|---|
| Runtime | Ollama `0.32.13`, `linux/amd64` | `PASS` |
| Image digest | `sha256:268c47cdc4718ded54babcd842579a7295ad79fd8d5c2ea64d7ba2e76872de6b` | `PASS` |
| Model | `qwen2.5:1.5b-instruct-q4_K_M` | `PASS` |
| Manifest SHA-256 | `65ec06548149b04c096a120e4a6da9d4017ea809c91734ea5631e89f96ddc57b` | `PASS` |
| Primary blob SHA-256 | `183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4` | `PASS` |
| Primary blob size | `986,048,512 bytes` | `PASS` |
| Bounded filesystem | `/dev/loop0`, ext4, approximately `5.6G` used and `10G` available | `PASS` |
| Memory / swap | `3,221,225,472` / `3,221,225,472` bytes | `PASS` |
| CPU | `NanoCpus=1,000,000,000` | `PASS` |
| Concurrency | parallel `1`; queue `1`; loaded models `1` | `PASS` |
| Privilege controls | `Privileged=false`; all capabilities dropped; no-new-privileges | `PASS` |
| Lifecycle | restart policy `no`; restart count `0` | `PASS` |

The accepted provenance limitation remains unchanged:

`Canonical model family/repository verified; exact source revision of the Ollama conversion not independently attested.`
