# Lossless inventory reconstruction and verification

This is transport documentation, not execution authority. Do not import package modules, collect or run tests, or touch runtime. The two parts are byte ranges of one compressed representation of the single logical artifact `docs/intelligence/stage-0.33c-runtime-baseline-reconciliation-implementation/06_FAULT_CASES.json`; they are not independent semantic artifacts.

The original logical artifact is **7,189,807,313 bytes**, SHA-256 **`3a9b187ed86bce077dd89ac34f445f29c09ee33f44a1fb57dfd9babdc7628a95`**. Successful recovery must have precisely that length and digest, and compare byte-for-byte with the reviewed source when it is available. Never regenerate inventory or update reviewed identities to accommodate transport.

## Representation

Under this document's `transport-zstd/` directory, in this exact order:

| Part | Bytes | SHA-256 |
| --- | ---: | --- |
| `06_FAULT_CASES.json.zst.part-000` | 50331648 | `3f8f8c9d25c85a493868c030976737bef13bcf0d7369ea94d1b30c3c118d13e6` |
| `06_FAULT_CASES.json.zst.part-001` | 18009849 | `cbce8168cb2fa2254b6941dffd90db09db381dd0ae40acfb36848d29054d4641` |

Encoding: Zstandard CLI 1.5.5, level 10, two threads, windowLog 27. The stored stream has exactly one frame, a 134217728-byte window, dictionary ID zero (no dictionary), declared content size 7189807313, and XXH64 content checksum (low 32 bits `2e845d88`). Raw concatenation totals 68341497 bytes. Its SHA-256 is recorded in `02_ARTIFACT_TRANSPORT.json` and `06_TRANSPORT_VALIDATION.json`. Recovery uses the recorded bytes directly; compression settings must not be used to regenerate or substitute the reviewed artifact. Zstandard 1.5.5 was used for recovery; compatible decoders must support that frame and 128 MiB window.

## Exact procedure

1. Use a trusted checkout at the exact publication PR HEAD. Verify the SHA-256 of `07_TRANSPORT_BINDING.json` against the separately reported digest. Its `files` array binds every added Git file except the binding itself, with exact path, size and SHA-256. Verify these entries before recovery. The binding excludes itself to avoid a recursive digest.
2. Require exactly the two regular files listed above in `transport-zstd/`, with no duplicates, extras, missing entries, symlinks or executable bits. Reject absolute paths, `..` components, noncanonical paths and symlink components. Use the literal ordered names below, never a wildcard or a caller-supplied filename list. Verify both byte lengths and SHA-256 values. These checks reject truncation, missing, duplicate, reordered or substituted parts before decoding.
3. Create a new private temporary directory using `mktemp -d`, with `umask 077`. Use only fixed output filenames in that directory; never decode into runtime, the reviewed source, or an existing package. From the publication directory, concatenate and decode as follows, replacing `PRIVATE` with that newly created directory. Enable shell `set -e` and `set -C` (noclobber) first. Do not proceed after any nonzero command result.

   ```sh
   cat transport-zstd/06_FAULT_CASES.json.zst.part-000 transport-zstd/06_FAULT_CASES.json.zst.part-001 > PRIVATE/inventory.zst
   wc -c < PRIVATE/inventory.zst
   sha256sum PRIVATE/inventory.zst
   zstd -lv PRIVATE/inventory.zst
   zstd -d -c --long=27 PRIVATE/inventory.zst > PRIVATE/06_FAULT_CASES.json
   wc -c < PRIVATE/06_FAULT_CASES.json
   sha256sum PRIVATE/06_FAULT_CASES.json
   cmp -- REVIEWED_SOURCE/06_FAULT_CASES.json PRIVATE/06_FAULT_CASES.json
   ```

4. Require concatenated size/hash to equal the transport manifest; require exactly one complete Zstandard frame, no trailing data and the parameters above. Require decoder success, reconstructed length 7189807313, and reconstructed SHA-256 `3a9b187ed86bce077dd89ac34f445f29c09ee33f44a1fb57dfd9babdc7628a95`. Require `cmp` exit zero against the original reviewed source. A recipient without that source can verify the bound length/digest, but must not claim to have performed the independent source comparison. The pre-PR comparison is recorded in `06_TRANSPORT_VALIDATION.json`.
5. If a fully materialized logical package is needed for separately authorized review, copy the ten unchanged direct artifacts into a new private directory and place the verified inventory alongside them. Require exactly the eleven logical filenames in `02_ARTIFACT_TRANSPORT.json`; validate every original `09_PACKAGE_MANIFEST.json` file digest. Keep transport files outside that logical package. Do not execute any package Python file.

The original package manifest remains byte-for-byte unchanged, SHA-256 `0c968c7f3dac7b3db848ceedbbefd838042dfebc871cdb1d79124d86cb704419`. The detached logical package review remains unchanged, SHA-256 `7bea72816bce84c2642f1aae0bdfd2ee550185c445a5e35d9e3e0cbd15abbd47`. The separate transport binding covers the Git representation without replacing either reviewed identity. No executable transport wrapper, workflow, hook, adapter or runtime behavior is introduced.

Exact-HEAD publication review is next after PR preparation. No automatic merge is authorized.
