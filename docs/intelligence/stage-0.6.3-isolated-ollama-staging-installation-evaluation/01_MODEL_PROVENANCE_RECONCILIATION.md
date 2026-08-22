# Model Provenance Reconciliation

## Verified endpoints and identities

| Field | Verified value |
|---|---|
| Canonical owner/repository | `Qwen/Qwen2.5-1.5B-Instruct` |
| Canonical revision observed | `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` |
| Canonical license | Apache License 2.0 (`apache-2.0`) |
| Ollama identifier | `qwen2.5:1.5b-instruct-q4_K_M` |
| Ollama manifest digest | `sha256:65ec06548149b04c096a120e4a6da9d4017ea809c91734ea5631e89f96ddc57b` |
| Ollama model blob digest | `sha256:183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4` |
| Ollama model blob size | `986,048,512 bytes` |
| Model format/family/type | `gguf` / `qwen2` / `1.5B` |
| Quantization | `Q4_K_M` |
| Ollama license-layer digest | `sha256:832dd9e00a68dd83b3c3fb9f5588dad7dcf337a0db50f7d9483f310cd292e92e` |

The Ollama registry manifest was retrieved as metadata only and hashed exactly;
the model blob was not retrieved. Its config independently records `gguf`,
`qwen2`, `1.5B`, and `Q4_K_M`. The official Ollama library entry agrees on the
manifest prefix, size, context class, and quantization. The canonical Qwen
repository metadata identifies owner, model, revision, and Apache-2.0 license.

## Unresolved mapping

The Ollama manifest and config do not record:

- the canonical source repository;
- the exact canonical source revision;
- the converter and converter revision;
- conversion parameters; or
- a signed or reproducible attestation mapping the canonical source files to
  model blob `sha256:183715c4...a5b4`.

Matching family, parameter class, quantization, size, template, and license is
strong identity evidence but is not proof that this GGUF blob was derived from
canonical revision `989aa798...aa306`. The exact canonical revision-to-blob
chain therefore remains ambiguous.

Disposition:

`INTELLIGENCE STAGE 0.6.3 MODEL PROVENANCE BLOCKED`

Installation, model acquisition, and inference must not be authorized until a
trusted upstream attestation or a reproducible conversion record closes this
exact mapping.
