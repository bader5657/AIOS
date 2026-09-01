# Stage 0.33C-P4R Genuine Source Eligibility and Acquisition Boundary

## Authority and current state

Steps 1–3 and Step 4 governance are `CLOSED / VERIFIED` at repository baseline
`5d8398059d7511b51246b156bbf725e26242dd7f`. Read-only discovery examined 441
retained manifests: 427 were current-schema and identifier coherent, 14 legacy
file-backed records failed current `DocumentManifest`/`SourceContext` rules, and
zero eligible material-receipt sources were found.

This package governs only later ordinary retention of one genuine production
business source. It performs no ingestion, database contact, runtime mutation,
approval-package creation, harness invocation, candidate creation, or Step 5
action.

## Genuine-source eligibility

The one source must be authentic evidence of received business materials, such
as a supplier invoice, purchase receipt, delivery note, material receipt note,
or an original photo/scan of one of those documents. Synthetic invoices, test
documents, generated evidence, edited or fabricated first-write evidence, and
documents unrelated to received materials are ineligible.

Prefer one supplier, one document, 1–3 material lines, clear quantities, a
simple allowed unit (`sheet`, `pcs`, `kg`, `roll`, or `pack`), a clear document
date when present, and minimal unrelated personal information. Complicated
packaging, ambiguous lines, unsupported units, and unusual edge cases should be
avoided for the first source. Acquisition retains evidence only; it does not
resolve or approve final business facts.

## Legacy boundary

The 14 legacy file-backed manifests remain preserved historical evidence. This
package grants no authority to repair, migrate, rename, reinterpret, re-ingest,
promote, or otherwise change them or their stored originals. Compatibility work
requires separate governance.

The new source must enter through the current normal retention path. Manual
manifest construction, forged `SourceContext`, direct filesystem copying,
special staging, schema exceptions, and first-write shortcuts are prohibited.

## Privacy and Git boundary

Retain only a business-purpose source. Do not intentionally submit credentials,
passwords, tokens, authentication or bank credentials, unrelated personal
documents, unrelated notes, or unrelated Telegram metadata. Ordinary supplier
and business information naturally present in a genuine original is permitted;
the original must not be altered or selectively rewritten under this package.
Any separate legal/privacy redaction requirement stops acquisition for its own
governance.

Raw document bytes, OCR text, supplier/document/item/quantity values, Telegram
identifiers, and other real values are prohibited from Git and governance
reports. Git contains policy only. Runtime retention owns the exact original.
OCR or LLM output may later assist a human review but is never authoritative and
cannot silently establish a trusted fact.

Project Owner action after unchanged governance merge is limited to providing
one genuine eligible document through the normal path. It is not package
approval, duplicate approval, candidate authority, or Step 5 authority.
