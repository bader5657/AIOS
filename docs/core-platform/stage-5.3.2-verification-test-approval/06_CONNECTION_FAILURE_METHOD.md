# Connection Failure Method

Minimum connection-failure evidence uses a test-only DSN targeting an
unavailable loopback endpoint with a bounded connection timeout.

The test must prove:

- one Registry call raises `RegistryPersistenceError`;
- no automatic reconnect/retry occurs;
- `AIOS_REGISTRY_DATABASE_URL` is not read or used; and
- no production fallback occurs.

The endpoint must be selected and proved unavailable inside the test
environment. No production hostname, credential, or DSN may appear.
Container/network interruption is not required.
