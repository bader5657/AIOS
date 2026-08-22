# Pinned Identity and Measurement Environment

## Exact image identity

| Property | Approved value |
|---|---|
| Runtime | Ollama `0.32.13` |
| Registry image | `docker.io/ollama/ollama:0.32.13` |
| Platform | `linux/amd64` |
| Platform manifest digest | `sha256:268c47cdc4718ded54babcd842579a7295ad79fd8d5c2ea64d7ba2e76872de6b` |
| Known compressed layers | `3,343,645,843 bytes` total |

The measurement must resolve the platform manifest and verify this digest
before retrieving any layer. A mismatch requires immediate stop with:

`STAGE 0.6.2 OLLAMA IMAGE IDENTITY MISMATCH`

Floating tags and alternate architectures are prohibited.

## Approved environment order

Use the first practical option in this order:

1. isolated disposable Docker data-root with a temporary daemon;
2. disposable registry/image-layout tool that retrieves the exact layers;
3. isolated temporary host or container environment;
4. the current VPS only after separately proving production-workload isolation,
   hard quota enforcement, and host reserve protection.

The existing production Docker image store must not be used by default. The
measurement record must identify the host, filesystem, tool/runtime version,
Docker storage backend (`overlay2`, containerd image store, or other), quota
mechanism, and whether compressed content is retained with extracted snapshots.

No production runtime location, service unit, compose topology, or AIOS runtime
directory is created by this approval.
