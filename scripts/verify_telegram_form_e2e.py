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
BASELINE = "d945109b59129064d2f7d35db3e3d930c7dc138a"
EXPECTED_BOT = "AIOSTesting_bot"
CHALLENGE_SHA256 = "d41a08f9492bd532b3053186184ffa0ec2a8b39c8d1198fa621e624e7309216e"
FIXTURE = "Nama: Pelanggan Fiktif\nAlamat: Jalan Uji 123\nKota: Solo\nNo. Telp: 001234567\nKet:"
INVALID = "Nama:\nAlamat: Jalan Uji 123\nKota: Solo\nNo. Telp:\nKet:"
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
        for filename in ("0006_create_customers.up.sql", "0007_customer_registration.up.sql", "0008_customer_phone.up.sql"):
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
          and os.environ.get("GITHUB_REF") == "refs/heads/feat/customer-telegram-form-v1-20261012",
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
                    state, phase = "start", "real_form_start"
                    await bot.send_message(owner, "Enrollment uji berhasil. Salin seluruh pesan berikut lalu kirim kembali ke bot ini.")
                    await bot.send_message(owner, "catat pelanggan")
                elif message.from_user.id == owner:
                    expected = {"start": "catat pelanggan", "invalid": INVALID,
                                "draft_cancel": FIXTURE, "cancel": "batal pelanggan",
                                "cancel_confirm": expected_confirmation, "draft": FIXTURE,
                                "confirm": expected_confirmation, "retry": expected_confirmation}[state]
                    if message.text != expected:
                        await bot.send_message(owner, "Pesan belum cocok. Salin seluruh pesan berikut lalu kirim kembali ke bot ini:")
                        await bot.send_message(owner, expected)
                        continue
                    check(await handle_customer_registration(update, app), "REAL_" + state.upper() + "_HANDLED")
                    with psycopg.connect(**admin) as connection:
                        counts = tuple(connection.execute("SELECT count(*) FROM " + table).fetchone()[0]
                                       for table in ("customers", "customer_registration_audit"))
                        if state not in ("confirm", "retry"):
                            check(counts == (0, 0), "NO_WRITE_" + state.upper())
                        if state in ("draft_cancel", "draft"):
                            row = connection.execute("SELECT token,snapshot,expires_at-created_at FROM customer_confirmations WHERE state='pending'").fetchone()
                            check(row is not None and row[1] == dict(name="Pelanggan Fiktif",address="Jalan Uji 123",city="Solo",phone="001234567",notes=None)
                                  and row[2].total_seconds() == 600, "FORM_SNAPSHOT_" + state.upper())
                            expected_confirmation = "konfirmasi_pelanggan " + row[0]
                        if state == "cancel":
                            check(connection.execute("SELECT count(*) FROM customer_confirmations WHERE state='pending'").fetchone()[0] == 0, "CANCEL_INVALIDATES_PENDING")
                        if state in ("confirm", "retry"):
                            check(counts == (1, 1), "EXACTLY_ONE_CUSTOMER_AUDIT_" + state.upper())
                            expected_snapshot = dict(name="Pelanggan Fiktif",address="Jalan Uji 123",city="Solo",phone="001234567",notes=None)
                            snap_hash = hashlib.sha256(json.dumps(expected_snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
                            row = connection.execute("""SELECT c.name,c.address,c.city,c.phone,c.notes,f.state,a.snapshot_sha256,
                                a.owner_id=f.owner_id,a.chat_id=f.chat_id,a.customer_id=f.customer_id
                                FROM customers c JOIN customer_confirmations f ON f.customer_id=c.customer_id
                                JOIN customer_registration_audit a ON a.confirmation_token=f.token""").fetchone()
                            check(row == ("Pelanggan Fiktif","Jalan Uji 123","Solo","001234567",None,"consumed",snap_hash,True,True,True),
                                  "PERSISTENCE_AUDIT_MATCH_" + state.upper())
                    if state == "start":
                        state = "invalid"
                        instruction = "Uji input tidak valid. Kirim kembali template berikut dengan Nama kosong:"
                        next_text = INVALID
                    elif state == "invalid":
                        state = "draft_cancel"
                        instruction = "Input tidak valid ditolak tanpa penyimpanan. Kirim form sintetis berikut:"
                        next_text = FIXTURE
                    elif state == "draft_cancel":
                        state = "cancel"
                        instruction = "Untuk tahap ini JANGAN konfirmasi. Uji pembatalan dengan mengirim pesan berikut:"
                        next_text = "batal pelanggan"
                    elif state == "cancel":
                        state = "cancel_confirm"
                        instruction = "Uji bahwa konfirmasi lama ditolak. Kirim pesan berikut:"
                        next_text = expected_confirmation
                    elif state == "cancel_confirm":
                        state = "draft"
                        instruction = "Pembatalan terverifikasi tanpa penyimpanan. Kirim kembali form berikut untuk penyimpanan:"
                        next_text = FIXTURE
                    elif state == "draft":
                        state = "confirm"
                        instruction = "Sekarang konfirmasi penyimpanan dengan mengirim pesan berikut:"
                        next_text = expected_confirmation
                    elif state == "confirm":
                        report("CUSTOMER_PERSISTENCE", "PASS_REAL_FORM_TO_POSTGRESQL")
                        app = CustomerRegistration(PostgresCustomerRegistrationTransactions(runtime_dsn))
                        state = "retry"
                        instruction = "Data sintetis tersimpan. Kirim pesan berikut sekali lagi untuk uji idempotency setelah aplikasi dibuat ulang:"
                        next_text = expected_confirmation
                    else:
                        report("E2E_STATUS", "PASS")
                        await bot.send_message(owner, "E2E Telegram Form → PostgreSQL PASS: parsing, input tidak valid, pembatalan, konfirmasi, satu pelanggan, satu audit, retry tanpa duplikasi. Database dan enrollment uji akan dibuang.")
                        return
                    phase = "real_form_" + state
                    await bot.send_message(owner, instruction)
                    await bot.send_message(owner, next_text)
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
