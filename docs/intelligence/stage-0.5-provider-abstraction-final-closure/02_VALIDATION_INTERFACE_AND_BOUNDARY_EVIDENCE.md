# Validation, Interface, and Boundary Evidence

## InferenceProvider interface

`InferenceProvider` is a standard-library abstract base class. It declares:

- abstract, read-only `descriptor` property returning `ProviderDescriptor`;
- abstract async method
  `infer(self, request: InferenceRequest) -> InferenceResult`.

The invocation signature contains only `self` and `request`. It has no
provider/model/configuration/credential/endpoint/timeout/tool override,
variadic arguments, or default execution behavior.

## Descriptor closed schema

No endpoint/base URL, credential/API key, account/tenant, retry, timeout,
session, persistence, cache/history, concurrency, CPU/RAM/model-size, pricing,
tool, mutable configuration, or business field exists.

## Provider abstraction boundary

Final review confirms:

- provider/model selection and dynamic routing: absent;
- retry, fallback, persistence, credentials, and configuration leakage: absent;
- network, HTTP, socket, subprocess, model/local-runtime code: absent;
- provider response parsing, failure mapping, and schema validation: absent;
- provider SDK or provider-specific type/import: absent;
- provider-native object return path: absent; and
- default/background worker, queue, polling, or activation behavior: absent.

The implementation reuses, and does not duplicate or modify,
`InferenceRequest`, `InferenceResult`, and `InferenceCapability`.

LOCAL and REMOTE descriptors are constructible as metadata only. Neither grants
runtime, network, installation, model download, process startup, credential,
or model invocation authority.
