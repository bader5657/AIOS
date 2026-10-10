"""Administrative enrollment only; never exposed through Telegram.

The administrator verifies identity through trusted Telegram evidence BEFORE
calling this command. References preserve provenance; they are not validators.
No username, PR approval, Receipt, or caller-supplied flag proves identity.
"""
import argparse
import os

import psycopg

def enroll(connection, telegram_user_id, verification_evidence, approval_reference):
    if type(telegram_user_id) is not int or not 0 < telegram_user_id < 2**63:
        raise ValueError("positive Telegram numeric user ID is required")
    for value in (verification_evidence, approval_reference):
        if type(value) is not str or not value.strip() or len(value) > 2000:
            raise ValueError("explicit evidence and approval references are required")
    # No upsert: an existing enrollment cannot be replaced or reactivated here.
    connection.execute(
        """INSERT INTO business_owner
           (telegram_user_id, verification_evidence, approval_reference)
           VALUES (%s,%s,%s)""",
        (telegram_user_id, verification_evidence, approval_reference),
    )

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--telegram-user-id", type=int, required=True)
    parser.add_argument("--verification-evidence", required=True)
    parser.add_argument("--approval-reference", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.apply:
        print("DRY_RUN: no database access. Verify identity and obtain environment-specific activation approval before --apply.")
        return
    dsn = os.environ.get("AIOS_OWNER_BOOTSTRAP_DATABASE_URL")
    if not dsn:
        raise RuntimeError("explicit administrative database DSN required")
    with psycopg.connect(dsn, autocommit=False) as connection, connection.transaction():
        enroll(connection, args.telegram_user_id, args.verification_evidence, args.approval_reference)
    print("OWNER_ENROLLED: transaction committed; business capability configuration is a separate gate.")

if __name__ == "__main__":
    main()
