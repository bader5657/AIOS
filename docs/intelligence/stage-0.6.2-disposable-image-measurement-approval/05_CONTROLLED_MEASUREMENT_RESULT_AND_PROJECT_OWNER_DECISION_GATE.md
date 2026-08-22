# AIOS Intelligence Stage 0.6.2 Controlled Measurement Result

## Controlled result

| Field | Recorded result |
|---|---|
| Ollama version | `0.32.13` |
| Platform | `linux/amd64` |
| Digest | `sha256:268c47cdc4718ded54babcd842579a7295ad79fd8d5c2ea64d7ba2e76872de6b` |
| Measurement isolation | Isolated disposable Docker daemon on an isolated `6 GiB` ext4 loopback filesystem; production Docker store not used |
| Baseline filesystem used | `31,129,296 bytes` |
| Baseline filesystem free | `6,231,998,464 bytes` |
| Pull result | Exact pinned image pull started; compressed layers were pulled; extraction did not complete |
| Failure point | Extraction of the `3.195 GB` layer failed with `no space left on device` |
| Model downloaded | `NO` |
| Inference executed | `NO` |
| Container executed | `NO` |
| Disk fit | `FAIL` |
| Existing ceiling | `6 GiB` total runtime/model/temporary disk (`6,442,450,944 bytes`) |
| Ceiling changed | `NO` |
| Ollama + Qwen2.5 1.5B fit | `NO`; the pinned runtime image acquisition already failed before model acquisition |
| Production authority | `NONE` |

The failure is sufficient to classify the approved Ollama acquisition path as
`FAIL`: it cannot complete inside the hard ceiling even before adding the
verified `986,061,892-byte` model-side persistence and the approved
`134,217,728-byte` runtime allowance. No additional Qwen model measurement is
required to prove this disk conflict.

The measurement did not produce a completed extracted image, so completed-image
persistent bytes and a successful acquisition peak are unavailable. Those
unknowns cannot produce `PASS` under the Stage 0.6.2 classification contract and
do not weaken the observed fail-closed result.

## Bounded alternative analysis

### Option A — Retain Ollama, choose lighter reviewed model

`NOT SUFFICIENT`

A lighter model cannot repair a failure that occurs while acquiring and
extracting the pinned Ollama image before any model is acquired. Option A could
become sufficient only if separate evidence establishes a materially smaller,
reviewed Ollama image or runtime variant and its complete acquisition peak plus
model and temporary storage fits within `6 GiB`. That is not the option as
currently evidenced.

### Option B — Retain Qwen2.5 1.5B and evaluate llama.cpp runtime

`LIKELY SUFFICIENT — REQUIRES SEPARATE PINNING AND CONTROLLED MEASUREMENT`

llama.cpp is likely to reduce runtime disk materially because a minimal
CPU-only runtime can use a compact executable and the reviewed GGUF model
directly, without retaining the pinned Ollama image's large compressed and
extracted container layers. This is a technical expectation, not a disk-fit
approval. A later governance package must pin the exact llama.cpp artifact,
platform, provenance, and checksum and must prove the full acquisition and
persistent footprint within all existing ceilings:

- `3 GiB` RAM;
- `1 vCPU`;
- `2 GiB` model file;
- `6 GiB` runtime/model/temporary disk.

No llama.cpp implementation, download, installation, or execution is
authorized by this record.

### Option C — Request explicit resource-ceiling increase

`NOT RECOMMENDED AT THIS GATE`

An increase could preserve Ollama and reduce runtime-integration change, but
the failed extraction does not establish the minimum safe new ceiling. Raising
the ceiling now would therefore reserve an unquantified amount of storage while
the same deployment must protect an `8 GB` RAM / `2 vCPU` production VPS and
its existing services. It does not improve the fixed CPU or RAM margin, and it
increases host-capacity and acquisition-peak risk. The operational benefit does
not yet clearly justify that tradeoff. Any increase requires a separate Project
Owner decision backed by a quantified disk requirement and host-reserve review.

## Recommendation and decision gate

Recommended option: `OPTION B — RETAIN QWEN2.5 1.5B AND EVALUATE LLAMA.CPP RUNTIME`.

Option B best preserves stability, simplicity, and low cost: it keeps the
reviewed model candidate and existing hard ceilings, avoids consuming more of
the constrained production VPS, and tests the component directly implicated by
the failure. It introduces a runtime-governance and integration change, so it
remains evaluation-only until separately approved and measured.

The Project Owner must explicitly approve exactly one of:

- `OPTION A — RETAIN OLLAMA, CHOOSE LIGHTER REVIEWED MODEL` (`NOT SUFFICIENT` on current evidence);
- `OPTION B — RETAIN QWEN2.5 1.5B AND EVALUATE LLAMA.CPP RUNTIME` (recommended); or
- `OPTION C — REQUEST EXPLICIT RESOURCE-CEILING INCREASE`.

No choice is inferred by this recommendation. Until an explicit decision is
recorded, the runtime/model candidate is otherwise unchanged, all existing
resource ceilings remain unchanged, and production authority remains `NONE`.

## Cleanup and remaining blockers

Cleanup status: the supplied verified result confirms use of an isolated
disposable Docker daemon and filesystem and confirms that the production Docker
store was not used. Final cleanup completed successfully; disposable artifacts were removed and
the protected production services remained unaffected. No cleanup of
the production Docker store is authorized.

Remaining blockers:

1. explicit Project Owner selection of exactly one bounded option;
2. exact canonical Qwen revision to runtime artifact provenance reconciliation;
3. for Option B, separate llama.cpp identity/provenance governance and a
   controlled resource-fit measurement; or the corresponding separately
   approved evidence and governance required by Option A or Option C.

Next action: obtain the Project Owner's explicit decision on exactly one option.
Do not install a runtime, download a model, execute inference, change a ceiling,
or create production authority at this gate.

`INTELLIGENCE STAGE 0.6.2 DISK CEILING CONFLICT — PROJECT OWNER DECISION REQUIRED`
