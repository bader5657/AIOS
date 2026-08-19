# Token and Boundary Reconciliation

Token validation moved only from module import time to production `main()` so
the Adapter can be imported under fake-only tests. Production startup still
fails clearly when `TELEGRAM_BOT_TOKEN` is absent, before Application builder
use. There is no hard-coded token, test-token production fallback,
configuration change, or deployment change.

The obsolete Telegram boundary assertion was replaced by the stronger Active
authority assertion: the Adapter must not import or construct RequestContext,
and Universal Ingestion must remain its sole owner. Existing classifier,
Storage, reverse-dependency, and prohibited-capability checks were retained and
strengthened rather than weakened.
