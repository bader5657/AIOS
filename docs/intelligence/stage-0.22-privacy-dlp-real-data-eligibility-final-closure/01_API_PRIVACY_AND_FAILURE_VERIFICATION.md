# API, Privacy, and Failure Verification

The verified provider-neutral public boundary is:

```python
evaluate_real_data_eligibility(
    data,
    *,
    explicitly_authorized,
) -> EligibilityResult
```

`EligibilityResult` is frozen and slotted. It contains the governed concepts
`allowed`, `classification`, `reason_code`, and `minimized_data`. Allowed data
is a fresh immutable mapping; denied results retain no matched secret,
credential, or raw rejected content.

Only literal explicit authorization and the exact semantic shape
`{"text": <str>}` can be allowed. Authorization is never inferred from
content. The implementation reuses the Stage 0.17 normalization and exact
bounds of 4,096 Unicode code points and 16,384 UTF-8 bytes. Empty or
whitespace-only input is denied as `EMPTY_CONTENT`.

Deterministic whole-request rejection covers authorization/bearer and common
API/bot tokens, private-key markers, password/session/cookie assignments, PIN,
OTP, CVV/CVC, and card/account authentication credentials. No category uses
redaction-and-continue.

The conservative v1 PII policy rejects deterministic email, telephone,
customer-identifier, and supported explicit address forms as
`PII_REQUIRES_EXPLICIT_SCOPE`. No PII scope is active. Telegram user ID, chat
ID, message ID, username, Update objects, bot credentials, and governed
transport/session metadata are prohibited from semantic data.

Allowed output contains only the normalized text. The implementation does not
mutate input or perform business enrichment, provenance dereferencing,
database, Registry, network, filesystem, environment/config, logging,
persistence, Memory, Specialist, mapper, Brain, provider, or inference work.
It introduces no dependency and uses only the standard library plus the
existing local Stage 0.17 projection relationship.

All normal policy denials return a denied result before `CoreToBrainMapper`,
`BrainInput`, Brain, provider, or inference activity. Mapper, Brain, and
provider call counts are each zero on rejection. Programmer type misuse may
raise `TypeError`; provider failure codes are unchanged.
