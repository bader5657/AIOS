# Authoritative Metadata and Mapping Evidence

## Frozen identities

| Field | Verified value |
|---|---|
| Canonical owner/model | `Qwen/Qwen2.5-1.5B-Instruct` |
| Recorded revision supplied to this gate | `989aa7980e4cf806f80c7fef2b1addb7bc71aa306` |
| Canonical repository revision observed | `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` |
| Ollama identifier | `qwen2.5:1.5b-instruct-q4_K_M` |
| Ollama manifest | `sha256:65ec06548149b04c096a120e4a6da9d4017ea809c91734ea5631e89f96ddc57b` |
| Ollama model blob | `sha256:183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4` |
| Blob size | `986,048,512 bytes` |
| Quantization | `Q4_K_M` |
| License | Apache License 2.0 |

The supplied recorded revision contains an additional `d` and is rejected by
the canonical repository as `RevisionNotFound`. It is retained here exactly as
supplied and is not silently replaced. The repository revision independently
observed from canonical metadata is recorded separately, but the exact source
revision used by the Ollama conversion remains unattested.

## Official Ollama metadata

The official manifest and blob page establish:

- immutable manifest and model-blob digests;
- family `qwen2`, parameter class `1.54B`, and `Q4_K_M`;
- architecture dimensions: 28 layers, hidden size 1536, feed-forward size
  8960, 12 attention heads, 2 KV heads, context 32768, RMS epsilon `1e-6`,
  rope base `1e6`, and vocabulary size 151936;
- tokenizer family `qwen2`, GPT-2 vocabulary encoding, BOS disabled, and token
  identifiers consistent with the canonical publication;
- Qwen/Alibaba system identity, Apache-2.0 license, and official Qwen GitHub,
  blog, and Hugging Face collection references.

Ollama metadata does not publish source repository, source revision, converter
revision, conversion command, or revision-to-blob attestation.

## Canonical Qwen metadata and official GGUF

The canonical config independently matches every listed architectural value.
Qwen also publishes an official `Qwen/Qwen2.5-1.5B-Instruct-GGUF` repository.
Its Q4_K_M file is `1,117,320,736 bytes` with SHA-256
`6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e`.
It is therefore not the `986,048,512-byte` Ollama blob and cannot supply the
missing direct hash bridge.

Authoritative sources:

- `https://ollama.com/library/qwen2.5:1.5b-instruct-q4_K_M`;
- `https://ollama.com/library/qwen2.5:1.5b-instruct-q4_K_M/blobs/183715c43589`;
- `https://registry.ollama.ai/v2/library/qwen2.5/manifests/1.5b-instruct-q4_K_M`;
- `https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct`;
- `https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF`.
