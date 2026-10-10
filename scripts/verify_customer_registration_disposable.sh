#!/usr/bin/env bash
# No production configuration or services. Preserve checkout and evidence.
set -euo pipefail
EXPECTED="${1:?usage: bash verify_customer_registration_disposable.sh EXACT_HEAD_SHA}"
[[ "$EXPECTED" =~ ^[0-9a-f]{40}$ ]] || exit 2
BASE=49bd23166556c13969814b65bb29092cb4f05b6d
WORK="$(mktemp -d /tmp/aios-business-p1.XXXXXX)"
CID=""
cleanup() {
    rc=$?
    if [[ -n "$CID" ]]; then docker rm -f "$CID" >/dev/null || true; fi
    printf 'VERIFICATION_EXIT_CODE=%s\nEVIDENCE=%s/verification.log\n' "$rc" "$WORK"
}
trap cleanup EXIT
exec > >(tee "$WORK/verification.log") 2>&1
git init -q "$WORK/repo"
cd "$WORK/repo"
git fetch --quiet https://github.com/bader5657/AIOS.git "$EXPECTED" "$BASE"
git checkout --detach "$EXPECTED"
[[ "$(git rev-parse HEAD)" == "$EXPECTED" ]]
printf 'HEAD=%s\nBASE=%s\n' "$(git rev-parse HEAD)" "$BASE"
git diff --stat "$BASE" HEAD
while IFS= read -r path; do
    committed="$(git rev-parse "HEAD:$path")"
    disk="$(git hash-object "$path")"
    printf '%s committed=%s disk=%s\n' "$path" "$committed" "$disk"
    [[ "$committed" == "$disk" ]]
done < <(git diff --name-only "$BASE" HEAD)
python3 -m venv "$WORK/venv"
PY="$WORK/venv/bin/python"
"$PY" -m pip install -r requirements.txt
DB="aios_customer_disposable_p1_$(date +%s)"
PASSWORD="$("$PY" -c 'import secrets; print(secrets.token_hex(24))')"
CID="$(docker run -d --rm -p 127.0.0.1::5432 -e POSTGRES_DB="$DB" -e POSTGRES_PASSWORD="$PASSWORD" postgres:16-alpine)"
for attempt in $(seq 1 60); do
    if docker exec "$CID" pg_isready -U postgres -d "$DB" >/dev/null; then break; fi
    sleep 1
done
docker exec "$CID" pg_isready -U postgres -d "$DB"
PORT="$(docker port "$CID" 5432/tcp | sed -n 's/^127\.0\.0\.1://p')"
[[ "$PORT" =~ ^[0-9]+$ ]] && [[ "$PORT" != 5432 ]]
unset AIOS_OWNER_BOOTSTRAP_DATABASE_URL AIOS_CUSTOMER_REGISTRATION_DATABASE_URL AIOS_CUSTOMER_REGISTRATION_ENABLED
export AIOS_CUSTOMER_DISPOSABLE_TESTS=1
export AIOS_CUSTOMER_TEST_DATABASE_URL="host=127.0.0.1 port=$PORT dbname=$DB user=postgres password=$PASSWORD sslmode=disable"
"$PY" --version
run_suite() {
    "$PY" - "$1" "$2" "$3" <<'PY'
import sys, unittest
label, directory, pattern = sys.argv[1:]
suite = unittest.defaultTestLoader.discover(directory, pattern=pattern)
count = suite.countTestCases()
print(f"SUITE={label} DISCOVERED={count}", flush=True)
if count == 0:
    raise SystemExit(2)
result = unittest.TextTestRunner(verbosity=2).run(suite)
code = 0 if result.wasSuccessful() and not result.skipped else 1
print(f"{label}_EXIT_CODE={code} SKIPPED={len(result.skipped)}", flush=True)
raise SystemExit(code)
PY
}
run_suite DOMAIN tests/unit/domain 'test_*.py'
run_suite APP tests/unit/app 'test_customer*.py'
run_suite ADAPTER tests/unit/adapters 'test_*customer*.py'
run_suite TELEGRAM_REGRESSION tests/unit/core_platform 'test_telegram*.py'
run_suite INTEGRATION tests/integration/customer 'test_*.py'
git diff --exit-code
