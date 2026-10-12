"""One-shot nonproduction Telegram-to-PostgreSQL verification. No production DSN."""
import asyncio
from datetime import datetime, timezone
import hashlib
import hmac
import json
import logging
import os
from pathlib import Path
import secrets
import subprocess
import time

logging.disable(logging.CRITICAL)
BASELINE = "1cdd11c229a2409c72a0d68b4bc94d536b0eebaf"
EXPECTED_BOT = "AIOSTesting_bot"
CHALLENGE_SHA256 = "5ba015f4fe1568b2ed039ca4d387b77d455171662f72bde7f3862223474c1f67"
FIXTURE = 'catat_pelanggan {"name":"AIOS E2E Synthetic","address":"Disposable test address","city":"Test City","notes":"nonproduction-e2e"}'
evidence = dict(baseline=BASELINE, E2E_STATUS="RUNNING", TELEGRAM_CONNECTION="NOT_RUN",
                OWNER_ENROLLMENT="NOT_RUN", CUSTOMER_PERSISTENCE="NOT_RUN",
                TEST_PASS=0, TEST_FAIL=0, ACTUAL_BLOCKER="NONE",
                OWNER_APPROVAL_REQUIRED=False)
container = None
phase = "preflight"

def report(key, value):
    evidence[key] = value
    print(key + "=" + json.dumps(value, separators=(",", ":")), flush=True)

def check(value, label):
    if not value:
        evidence["TEST_FAIL"] += 1
        raise RuntimeError(label)
    evidence["TEST_PASS"] += 1
    report(label, "PASS")

def docker(*args, env=None):
    return subprocess.run(["docker", *args], env=env, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                          text=True).stdout.strip()

def setup_database():
    global container
    import psycopg
    from psycopg import conninfo, sql
    password = secrets.token_hex(32)
    env = dict(os.environ, POSTGRES_PASSWORD=password)
    # Do not pass the Telegram credential to Docker or any child process.
    env.pop("AIOS_E2E_TELEGRAM_BOT_TOKEN", None)
    name = "aios-telegram-e2e-" + os.environ["GITHUB_RUN_ID"]
    container = name
    docker("run", "-d", "--rm", "--name", name,
           "--label", "aios.disposable.telegram-e2e=true",
           "-p", "127.0.0.1::5432", "-e", "POSTGRES_PASSWORD",
           "-e", "POSTGRES_DB=aios_customer_disposable_telegram_e2e",
           "postgres:16-alpine", env=env)
    port = docker("port", name, "5432/tcp")
    check(port.startswith("127.0.0.1:"), "DATABASE_LOOPBACK_ONLY")
    port = int(port.rsplit(":", 1)[1])
    check(port != 5432, "DATABASE_RANDOM_PORT")
    values = dict(host="127.0.0.1", port=port,
                  dbname="aios_customer_disposable_telegram_e2e",
                  user="postgres", password=password, sslmode="disable",
                  connect_timeout=5)
    for _ in range(60):
        try:
            with psycopg.connect(**values):
                break
        except psycopg.OperationalError:
            time.sleep(1)
    else:
        raise RuntimeError("database_start_timeout")
    role_password = secrets.token_hex(32)
    with psycopg.connect(**values) as connection:
        for filename in ("0006_create_customers.up.sql", "0007_customer_registration.up.sql"):
            connection.execute((Path(os.environ["BASELINE_ROOT"]) / "migrations/postgres" / filename).read_text())
        connection.execute("REVOKE CREATE ON SCHEMA public FROM PUBLIC")
        connection.execute(sql.SQL("CREATE ROLE aios_e2e_runtime LOGIN PASSWORD {} NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS").format(sql.Literal(role_password)))
        connection.execute("ALTER ROLE aios_e2e_runtime SET search_path = public")
        for grant in (
            "USAGE ON SCHEMA public",
            "SELECT, INSERT, UPDATE ON customers",
            "SELECT, UPDATE(last_draft_message_id) ON business_owner",
            "SELECT, INSERT, UPDATE ON customer_confirmations",
            "SELECT, INSERT ON customer_registration_audit",
        ):
            connection.execute("GRANT " + grant + " TO aios_e2e_runtime")
    return values, conninfo.make_conninfo(**dict(values, user="aios_e2e_runtime", password=role_password))

def private_message(update, start):
    message = update.message
    return (message is not None and message.from_user is not None
            and not message.from_user.is_bot and message.chat.type == "private"
            and message.chat.id == message.from_user.id
            and not message.forward_origin and not message.sender_chat
            and not message.via_bot and message.date.timestamp() >= start)

async def main():
    global phase
    import psycopg
    from telegram import Bot
    from scripts.bootstrap_business_owner import enroll
    from core.adapters.telegram.customer_registration import handle_customer_registration
    from core.app.customer_registration import CustomerRegistration
    from core.adapters.postgres_customer_registration import PostgresCustomerRegistrationTransactions
    check(os.environ.get("GITHUB_REPOSITORY") == "bader5657/AIOS"
          and os.environ.get("GITHUB_REF") == "refs/heads/test/telegram-e2e-20261012",
          "TRUSTED_BRANCH")
    check(os.environ.get("APP_BASELINE_SHA") == BASELINE, "PINNED_BASELINE")
    token = os.environ.pop("AIOS_E2E_TELEGRAM_BOT_TOKEN", "")
    check(bool(token.strip()), "SECRET_AVAILABLE")
    phase = "telegram_identity"
    async with Bot(token=token) as bot:
        me = await bot.get_me()
        check(me.is_bot and me.username == EXPECTED_BOT, "NONPRODUCTION_BOT_MATCH")
        webhook = await bot.get_webhook_info()
        check(not webhook.url, "NO_EXISTING_WEBHOOK")
        report("TELEGRAM_CONNECTION", "PASS_GETME_EXPECTED_NONPRODUCTION_BOT")
        phase = "database"
        admin, runtime_dsn = setup_database()
        app = CustomerRegistration(PostgresCustomerRegistrationTransactions(runtime_dsn))
        start = int(time.time())
        deadline = time.monotonic() + 1200
        offset = None
        owner = None
        state = "challenge"
        expected_confirmation = None
        fixture_update = None
        report("AWAITING_TELEGRAM", "PRIVATE_CHALLENGE_THEN_FOLLOW_BOT_PROMPTS")
        phase = "challenge"
        while time.monotonic() < deadline:
            updates = await bot.get_updates(offset=offset, timeout=20,
                                            allowed_updates=["message", "edited_message"],
                                            read_timeout=30)
            for update in updates:
                offset = update.update_id + 1
                if not private_message(update, start):
                    continue
                message = update.message
                if state == "challenge":
                    text = message.text or ""
                    prefix = "aios_e2e_enroll "
                    if not text.startswith(prefix):
                        continue
                    digest = hashlib.sha256(text[len(prefix):].encode()).hexdigest()
                    if not hmac.compare_digest(digest, CHALLENGE_SHA256):
                        continue
                    owner = message.from_user.id
                    check(type(owner) is int and 0 < owner < 2**63, "VERIFIED_NUMERIC_ID")
                    # Hash the real Bot API update; never log raw identity, nonce or update.
                    receipt = hashlib.sha256(update.to_json().encode()).hexdigest()
                    ref = "github-actions:" + os.environ["GITHUB_RUN_ID"] + ":telegram-update-sha256:" + receipt
                    with psycopg.connect(**admin) as connection:
                        enroll(connection, owner, ref,
                               "user-approved-nonproduction-e2e:2026-10-12")
                    report("ENROLLMENT_EVIDENCE_SHA256", receipt)
                    report("ENROLLMENT_VERIFIED_AT", datetime.now(timezone.utc).isoformat())
                    report("OWNER_ENROLLMENT", "PASS_FRESH_PRIVATE_CHALLENGE_NUMERIC_ID")
                    await bot.send_message(owner, "Enrollment uji berhasil. Kirim teks berikut persis (data sintetis):\n" + FIXTURE)
                    state, phase = "draft", "real_telegram_draft"
                elif message.from_user.id == owner:
                    if state == "draft" and message.text == FIXTURE:
                        fixture_update = update
                        handled = await handle_customer_registration(update, app)
                        check(handled, "REAL_TELEGRAM_DRAFT_HANDLED")
                        with psycopg.connect(**admin) as connection:
                            check(connection.execute("SELECT count(*) FROM customers").fetchone()[0] == 0,
                                  "NO_CUSTOMER_BEFORE_CONFIRMATION")
                            row = connection.execute("SELECT token, expires_at-created_at FROM customer_confirmations WHERE state='pending'").fetchone()
                            check(row is not None and row[1].total_seconds() == 600, "PERSISTED_CONFIRMATION_TTL")
                            expected_confirmation = "konfirmasi_pelanggan " + row[0]
                        state, phase = "confirm", "real_telegram_confirmation"
                    elif state == "confirm" and message.text == expected_confirmation:
                        check(await handle_customer_registration(update, app), "REAL_TELEGRAM_CONFIRMATION_HANDLED")
                        with psycopg.connect(**admin) as connection:
                            row = connection.execute("""SELECT c.name,c.address,c.city,c.notes,f.state,
                                a.snapshot_sha256,a.owner_id=f.owner_id,a.chat_id=f.chat_id,
                                a.customer_id=f.customer_id
                                FROM customers c JOIN customer_confirmations f ON f.customer_id=c.customer_id
                                JOIN customer_registration_audit a ON a.confirmation_token=f.token""").fetchone()
                            expected = json.loads(FIXTURE.partition(" ")[2])
                            snap_hash = hashlib.sha256(json.dumps(expected, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
                            check(row == ("AIOS E2E Synthetic", "Disposable test address", "Test City",
                                          "nonproduction-e2e", "consumed", snap_hash, True, True, True),
                                  "POSTGRES_CUSTOMER_CONFIRMATION_AUDIT_MATCH")
                            for table in ("customers", "customer_registration_audit"):
                                check(connection.execute("SELECT count(*) FROM " + table).fetchone()[0] == 1,
                                      table.upper() + "_EXACTLY_ONE")
                        report("CUSTOMER_PERSISTENCE", "PASS_REAL_TELEGRAM_TO_POSTGRESQL")
                        # Recreate application and connection factory; receipt comes from durable DB.
                        app = CustomerRegistration(PostgresCustomerRegistrationTransactions(runtime_dsn))
                        await bot.send_message(owner, "Data sintetis tersimpan. Untuk uji idempotency setelah aplikasi dibuat ulang, kirim ulang pesan konfirmasi yang sama satu kali.")
                        state, phase = "retry", "real_telegram_retry"
                    elif state == "retry" and message.text == expected_confirmation:
                        check(await handle_customer_registration(update, app), "REAL_TELEGRAM_RETRY_HANDLED")
                        with psycopg.connect(**admin) as connection:
                            for table in ("customers", "customer_registration_audit"):
                                check(connection.execute("SELECT count(*) FROM " + table).fetchone()[0] == 1,
                                      "RESTART_RETRY_" + table.upper() + "_EXACTLY_ONE")
                        report("E2E_STATUS", "PASS")
                        await bot.send_message(owner, "E2E Telegram → PostgreSQL PASS: satu pelanggan sintetis, satu audit, retry tanpa duplikasi. Database dan enrollment uji akan dibuang.")
                        return
                    else:
                        # Only a challenge-verified private sender receives guidance.
                        # Do not silently discard mistyped or partial commands.
                        report("OWNER_MESSAGE_NEEDS_CORRECTION", state)
                        instruction = FIXTURE if state == "draft" else expected_confirmation
                        await bot.send_message(owner, "Pesan belum cocok. Salin dan kirim SATU BARIS LENGKAP berikut, termasuk kata perintah di awal:\n" + instruction)
        raise TimeoutError("telegram_interaction_timeout")

if __name__ == "__main__":
    code = 0
    try:
        asyncio.run(main())
    except Exception as exc:
        code = 1
        report("E2E_STATUS", "BLOCKED" if isinstance(exc, TimeoutError) else "FAIL")
        # Exception text and tracebacks may contain URLs, tokens, identity or DSNs.
        report("ACTUAL_BLOCKER", phase + ":" + type(exc).__name__)
    finally:
        if container:
            try:
                docker("rm", "-f", container)
                report("DISPOSABLE_DATABASE_REMOVED", True)
            except Exception:
                code = 1
                report("DISPOSABLE_DATABASE_REMOVED", False)
        report("NEXT_SINGLE_ACTION", "REVIEW_EVIDENCE" if code == 0 else "RESOLVE_REPORTED_PHASE")
        Path("telegram-e2e-evidence.json").write_text(json.dumps(evidence, indent=2))
        summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary:
            with open(summary, "a") as stream:
                stream.write("## Nonproduction Telegram E2E\n\n" + "\n".join("- **" + k + "**: " + str(v) for k,v in evidence.items()) + "\n")
    raise SystemExit(code)
