# Environment, Dependency, and Network Authority

The following verification-only resources are authorized:

| Resource | Exact authority |
|---|---|
| Detached source checkout | `/opt/aios/runtime/verification/stage-0.15-src` |
| Python | `/usr/bin/python3`, version `3.12.3` |
| Virtual environment | `/opt/aios/runtime/verification/stage-0.15-venv` |
| Repository dependencies | exact pins in authoritative-source `requirements.txt` |
| Test tool | `pytest==8.4.2` |
| Test-tool classification | `TEST_ONLY_VERIFICATION_TOOL` |
| Additional test tooling | `NONE` |
| Raw evidence | `/opt/aios/runtime/verification/stage-0.15-evidence` |

The source checkout must remain clean, disposable, separate from
`/opt/aios-src`, absent from production `PYTHONPATH`, unused by production
services, and unmodified. The venv must use the existing standard-library
`venv` module and must not upgrade system Python or modify
`/opt/aios/runtime/venv`.

`pytest==8.4.2` is explicitly frozen by Project Owner authority because no
historical pytest pin is retained. It is not an AIOS runtime or production
dependency and must not be added to `requirements.txt` or installed in the
production venv.

TLS-verified package acquisition from the standard project-consistent Python
package index is authorized only for the exact repository requirements and
`pytest==8.4.2`. No arbitrary mirror, untrusted URL, direct unknown archive, or
additional package is authorized. This network authority ends immediately
after installation. Ollama/model, provider, Telegram, production API, and
business-data network access remain prohibited.

If an undeclared test package is required, stop with:

`STAGE 0.15 ADDITIONAL TEST TOOLING AUTHORITY REQUIRED`
