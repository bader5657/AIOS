# API, Policy, and Failure Contract

## Public surface

The production module exposes one function semantically equivalent to:

```python
evaluate_real_data_eligibility(
    data: Mapping[str, object],
    *,
    explicitly_authorized: bool,
) -> EligibilityResult
```

Final names may follow repository conventions, but no semantic expansion is
permitted. `explicitly_authorized` is a trusted out-of-band argument and must
never be inferred from or accepted inside semantic content.

`EligibilityResult` is a frozen, slotted, provider-neutral standard-library
DTO with exactly the governed concepts `allowed`, `classification`,
`reason_code`, and `minimized_data`. Classification and reason code use bounded
immutable values. Denied results contain no raw rejected content, matched
substring, secret, or credential. Allowed `minimized_data` is an immutable or
detached snapshot and exists only for allowed input.

The bounded reason-code vocabulary is:

- `ALLOWED`
- `REAL_DATA_NOT_AUTHORIZED`
- `EMPTY_CONTENT`
- `SECRET_DETECTED`
- `CREDENTIAL_FIELD`
- `PII_REQUIRES_EXPLICIT_SCOPE`
- `UNSUPPORTED_MODALITY`
- `OVERSIZED_CONTENT`
- `PROHIBITED_METADATA`
- `UNSUPPORTED_STRUCTURE`

Provider `FailureCode` is unchanged.

## Eligible input

Only an explicitly authorized, already-minimized, operator-authored plain-text
candidate with the exact mapping key set `{"text"}` may be allowed. Successful
output is a fresh minimized mapping containing only the exact text accepted
under the existing Stage 0.17 normalization contract.

The exact Stage 0.17 bounds are reused: at most 4,096 Unicode code points and
16,384 UTF-8 bytes. Empty or whitespace-only text is denied as
`EMPTY_CONTENT`; oversized text is denied as `OVERSIZED_CONTENT`. No second
normalization or size policy may be invented.

Additional keys, nested objects, transport metadata, business records,
Registry payloads, configuration, credentials, or arbitrary structures are
denied deterministically as `PROHIBITED_METADATA`, `UNSUPPORTED_MODALITY`, or
`UNSUPPORTED_STRUCTURE`, according to the frozen category.

Images, voice, audio, video, PDF, DOC/DOCX, spreadsheets, URL-fetch candidates,
binary data, and arbitrary document objects are unsupported. The module must
not fetch, open, or extract them.

## Privacy and DLP policy

Secrets, credentials, and financial authentication data are never eligible.
The entire request is denied; semantic text is never silently redacted and
continued. Deterministic standard-library checks cover at least:

- authorization and bearer token forms;
- common API-key and bot-token forms;
- PEM, RSA, and OpenSSH private-key markers;
- password, passwd, secret, token, API-key, and authorization assignments;
- cookie and session credential forms; and
- PIN, OTP, CVV/CVC, card-login, and financial authentication fields.

Recognizable high-confidence email, telephone, explicit postal-address, and
customer-identifier forms are denied as `PII_REQUIRES_EXPLICIT_SCOPE`. Names
and ordinary business terms are not automatically enriched or claimed to be
perfectly detectable. Residual risk is controlled by operator minimization,
exact input shape, and the absence of automatic context expansion.

Telegram user ID, chat ID, message ID, username, Update objects, bot tokens,
session state, and transport state are prohibited semantic metadata. Opaque
provenance stays outside this module and is never dereferenced.

## Failure and side-effect contract

Normal authorization, policy, content, shape, modality, size, secret, and PII
denials return `EligibilityResult(allowed=False, ...)`. Wrong API argument
types are programmer misuse and may raise `TypeError`. Denial must occur before
mapper, `BrainInput`, Brain boundary, invoker, provider, or inference activity;
mapper, Brain, and provider calls are each exactly zero on rejection.

The module performs no input mutation, logging, persistence, content hashing,
journal writing, database or Registry access, network access, filesystem
access or scanning, environment/config lookup, business enrichment, provider
call, or provenance lookup. It uses the standard library only.
