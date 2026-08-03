# Core Platform Stage 3.1.1 Input Capability Matrix

## Record

| Field | Value |
|---|---|
| Execution Plan position | Stage 3 — Main Step 3.1 — Sub Step 3.1.1 |
| Mapping baseline | `fdee68455f365d83355d3c4863573295a4237b4c` (`main`) |
| Blueprint scope | Text, Image, Voice, Audio, Video, PDF, DOC/DOCX, Spreadsheet, Web link, and YouTube link |
| Current boundary | Telegram classifier → Universal Ingestion → current storage/metadata/manifest calls |
| Mapping date | `2026-08-03` |
| Result | **PASS with capability and authority gaps recorded** |

This matrix maps exactly the ten Blueprint input forms to current repository
handling. It does not define lifecycle ownership, add media types, change
runtime behavior, or represent partial transport acceptance as complete
Blueprint handling.

## Status Definitions

| Status | Meaning |
|---|---|
| `PRESENT` | Current handling is identifiable and aligned for the mapped scope |
| `PARTIAL` | Some handling exists, but one or more explicit Blueprint-facing gaps remain |
| `MISSING` | No distinct current handling exists beyond a more generic transport path |

These statuses are current-baseline findings, not Roadmap progress updates or
implementation decisions for Sub Step 3.1.3.

## Approved Input Capability Matrix

| Blueprint input | Telegram evidence | Classifier result | Current ingestion/storage path | Metadata/manifest evidence | Status |
|---|---|---|---|---|---|
| Text | `message.text` | `TEXT` | Returned as ingestion text; attachment storage is skipped | No file metadata or manifest, consistent with current non-file path | `PRESENT` for plain text receipt |
| Image | `message.photo` | `IMAGE` | Downloads highest-resolution photo as `.jpg`; `save_file()` writes to image root | Basic image/file metadata and `image` manifest are created after save | `PRESENT` for current Telegram image path |
| Voice | `message.voice` | `VOICE` | Downloads as `.ogg`, but generic `save_file()` writes it under image root with an `IMG-` name | Basic file metadata and `voice` manifest are created | `PARTIAL` — wrong storage class/naming |
| Audio | `message.audio` | `AUDIO` | Downloads using filename suffix or `.mp3`, but writes under image root with an `IMG-` name | Basic file metadata and `audio` manifest are created | `PARTIAL` — wrong/unresolved storage class |
| Video | `message.video` | `VIDEO` | Downloads as `.mp4`, but writes under image root with an `IMG-` name | Basic file metadata and `video` manifest are created | `PARTIAL` — wrong/unresolved storage class |
| PDF | `message.document` | `DOCUMENT` | Downloads with original suffix, but writes under image root and remains generic `document` | Basic file metadata and `document` manifest are created | `PARTIAL` — no PDF distinction and wrong storage class |
| DOC/DOCX | `message.document` | `DOCUMENT` | Downloads with `.doc`/`.docx` suffix, but writes under image root and remains generic `document` | Basic file metadata and `document` manifest are created | `PARTIAL` — no DOC/DOCX distinction and wrong storage class |
| Spreadsheet | `message.document` | `DOCUMENT` | Downloads with supplied suffix, but writes under image root and remains generic `document` | Basic file metadata and `document` manifest are created | `PARTIAL` — no spreadsheet distinction and wrong storage class |
| Web link | URL text in `message.text` | `TEXT` | Returned only as generic text; text path skips attachment/link storage | No link detection, metadata, or manifest | `MISSING` distinct Web-link handling |
| YouTube link | YouTube URL text in `message.text` | `TEXT` | Returned only as generic text; text path skips attachment/link storage | No YouTube detection, metadata, or manifest | `MISSING` distinct YouTube-link handling |

All ten Blueprint inputs are accounted for. The matrix approves no input
beyond those ten.

## Current Call-Path Findings

### Classification

The classifier exposes `TEXT`, `IMAGE`, `VOICE`, `DOCUMENT`, `VIDEO`, `AUDIO`,
and `UNKNOWN`. Telegram-native photo, voice, audio, video, document, and text
forms are recognized. PDF, DOC/DOCX, and Spreadsheet converge on
`DOCUMENT`; Web link and YouTube link converge on `TEXT`.

This transport convergence was verified in Sub Step 1.4.1. It is insufficient
by itself to establish distinct handling for all ten Blueprint inputs.

### Ingestion

Universal Ingestion:

1. classifies the message;
2. skips attachment storage only for `TEXT`;
3. asks Telegram storage to save every other classified form;
4. extracts basic metadata only when a stored path is returned;
5. creates a manifest only when a stored path is returned; and
6. returns message text or caption.

This is a current call inventory only. Receive/Store/Extract/Create/Register/
Process/Route/Respond ownership and sequence decisions belong exclusively to
Sub Step 3.1.2 and are not made here.

### Storage

Telegram storage can download Image, Voice, Document, Video, and Audio forms,
but every successful download is passed to one generic `save_file()` function.
That function always uses `/opt/aios/data/documents/images` and image-style
`IMG-` names regardless of media type.

The Blueprint publishes image, voice, PDF, docs, links, and manifests roots.
Current runtime has only image and manifest roots. Storage-path contracts and
migration/non-migration decisions remain reserved for Sub Step 3.2.1.

### Metadata and manifest

The Metadata Engine emits filename, extension, size, and MIME type for any
stored file, plus dimensions/format for detected images. The manifest receives
the broad classifier value, uses the hard-coded original filename `telegram`,
and is created only after a stored path exists.

Required per-media metadata belongs to Sub Step 3.3.1. Runtime/schema manifest
reconciliation belongs to Sub Step 3.4.1. This matrix neither approves those
current shapes nor changes them.

## Capability Gaps

1. Voice, Audio, Video, PDF, DOC/DOCX, and Spreadsheet files are written to
   the image root and receive image-style stored names.
2. PDF, DOC/DOCX, and Spreadsheet are not distinguished from generic Telegram
   documents after classification.
3. Web and YouTube URLs are not identified as distinct input capabilities and
   do not use link storage, metadata, or manifests.
4. Current storage does not implement the published voice, PDF, docs, or links
   roots.
5. Current source has no distinct Audio or Video storage destination.
6. The original Telegram filename is not preserved in the manifest; the
   literal `telegram` is supplied instead.
7. No current test executes Universal Ingestion handling for the complete
   ten-input matrix. Such capability-matrix tests accompany implementation in
   Sub Step 3.1.3 and are not created early here.

No gap is silently deferred from the Stage 3 exit gate. This record maps the
gaps for the later frozen-plan steps that own their contracts and changes.

## Authority Findings

The Blueprint does not specify:

- the storage destination for Audio or Video;
- whether Audio shares the voice root or Video shares another published root;
- extension/MIME rules that distinguish PDF, DOC/DOCX, and Spreadsheet;
- supported spreadsheet extensions or MIME types;
- URL recognition, normalization, or YouTube matching rules;
- whether link originals are stored as URL text, a file, or another form; or
- handling for mixed Telegram messages that expose more than one input form.

These gaps prohibit inventing detailed handling in this Sub Step. They do not
stop creation of the capability matrix and do not create new architecture or
authority. Any implementation requiring those decisions must use the
applicable later contract step and Project Owner authority.

## Validation Plan

Validation consists of:

- a read-only source audit covering classifier, ingestion, Telegram storage,
  file storage, metadata, and manifest modules;
- the existing explicit-input classifier tests from Sub Step 1.4.1;
- the complete Core Platform focused regression suite; and
- the accepted repository-root Domain Foundation regression command.

No new test is required for this mapping-only Sub Step. Full ten-input runtime
capability tests are explicitly required with implementation in Sub Step
3.1.3.

Observed results:

```text
Source modules audited: 6/6
Classifier categories mapped: 7/7
Attachment download branches mapped: 5/5
Generic image-root storage: CONFIRMED
Text storage skip: CONFIRMED
Explicit-input focused suite: Ran 7 tests in 0.003s — OK
Core Platform focused suite: Ran 16 tests in 0.008s — OK
Official repository-root suite: Ran 212 tests in 0.036s — OK
```

## Scope Boundaries and Result

The only created artifact is this ten-input capability matrix. No existing
runtime, Request Context contract, schema, test, dependency, configuration, or
behavior is changed. No Blueprint, Roadmap, Governance, `VERSION`, Domain
Foundation, Execution Plan, freeze document, milestone, source, deployment,
service, architecture, authority, or workflow artifact is changed.

**Sub Step 3.1.1 result: PASS with gaps recorded**

Main Step 3.1 remains in progress. The next frozen-plan position is Stage 3,
Main Step 3.1, Sub Step 3.1.2. That Sub Step is not started by this record.
